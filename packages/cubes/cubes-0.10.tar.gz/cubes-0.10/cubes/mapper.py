# -*- coding: utf-8 -*-
from cubes.common import get_logger
import collections

class Mapper(object):
    """Mapper is core clas for translating logical model to physical
    database schema.
    """
    # WARNING: do not put any SQL/engine/connection related stuff into this
    # class yet. It might be moved to the cubes as one of top-level modules
    # and subclassed here.

    def __init__(self, cube, locale=None, simplify=True, **options):
        """Abstract class for mappers which maps logical references to
        physical references (tables and columns).

        Attributes:

        * `cube` - mapped cube
        * `simplify` – references for flat dimensions (with one level and no
          details) will consist just of dimension names, no attribute name.
          Might be useful when using single-table schema with one-column
          dimensions.
        * `locale` – locale to be used for fetching dimension data

        .. note::

            For compatibility reasons, when "simplify_dimension_references" is
            present in options, it has precedence over the `simplify`
            attribute.
        """

        super(Mapper, self).__init__()

        if cube == None:
            raise Exception("Cube for mapper should not be None.")

        self.logger = get_logger()

        self.cube = cube
        self.locale = locale

        self.simplify = options.get("simplify_dimension_references", simplify)
        self._collect_attributes()

    def cube_mapping(self, cube, attribute):
        """Return mapping for a cube attribute"""
        pass

    def dimension_mapping(self, dimension, attribute):
        pass

        # 

    def logical(self, attribute, locale=None):
        """Returns logical reference as string for `attribute` in `dimension`.
        If `dimension` is ``Null`` then fact table is assumed. The logical
        reference might have following forms:

        * ``dimension.attribute`` - dimension attribute
        * ``attribute`` - fact measure or detail

        If `simplify` of the receiver is ``True`` then references for flat
        dimensios without details is `dimension`.

        If `locale` is specified, then locale is added to the reference. This
        is used by backends and other mappers, it has no real use in end-user
        browsing.
        """

        return attribute.ref(self.simplify, locale or self.locale)

    def _collect_attributes(self):
        """Collect all cube attributes and create a dictionary where keys are
        logical references and values are `cubes.model.Attribute` objects.
        This method should be used after each cube or mappings change.
        """

        self.attributes = collections.OrderedDict()

        for attr in self.cube.measures:
            self.attributes[self.logical(attr)] = attr

        for attr in self.cube.details:
            self.attributes[self.logical(attr)] = attr

        for dim in self.cube.dimensions:
            for attr in dim.all_attributes():
                if not attr.dimension:
                    raise Exception("No dimension in attr %s" % attr)
                self.attributes[self.logical(attr)] = attr

    def all_attributes(self, expand_locales=False):
        """Return a list of all attributes of a cube. If `expand_locales` is
        ``True``, then localized logical reference is returned for each
        attribute's locale."""
        return self.attributes.values()

    def attribute(self, name):
        """Returns an attribute with logical reference `name`. """
        # TODO: If attribute is not found, returns `None` (yes or no?)

        return self.attributes[name]

    def map_attributes(self, attributes, expand_locales=False):
        """Convert `attributes` to physical attributes. If `expand_locales` is
        ``True`` then physical reference for every attribute locale is
        returned."""

        if expand_locales:
            physical_attrs = []

            for attr in attributes:
                if attr.locales:
                    refs = [self.physical(attr, locale) for locale in attr.locales]
                else:
                    refs = [self.physical(attr)]
                physical_attrs += refs
        else:
            physical_attrs = [self.physical(attr) for attr in attributes]

        return physical_attrs

    def split_logical(self, reference):
        """Returns tuple (`dimension`, `attribute`) from `logical_reference` string. Syntax
        of the string is: ``dimensions.attribute``."""
        
        split = reference.split(".")

        if len(split) > 1:
            dim_name = split[0]
            attr_name = ".".join(split[1:])
            return (dim_name, attr_name)
        else:
            return (None, reference)

    def physical(self, attribute, locale=None):
        """Returns physical reference as tuple for `attribute`, which should
        be an instance of :class:`cubes.model.Attribute`. If there is no
        dimension specified in attribute, then fact table is assumed. The
        returned tuple has structure: (`schema`, `table`, `column`).

        This method should be implemented by `Mapper` subclasses.
        """
        
        raise NotImplementedError
