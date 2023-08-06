
class StarBrowser(AggregationBrowser):
    def __init__(self, cube, connectable=None, locale=None, metadata=None,
            debug=False)
        pass

    def aggregate(self, cell=None, measures=None, drilldown=None,
                  attributes=None, page=None, page_size=None, order=None,
                  include_summary=None, include_cell_count=None, **options):

        if not cell:
            cell = Cell(self.cube)
    def values(self, cell, dimension, depth=None, hierarchy=None):
        """docstring"""

        cell = cell or Cell(self.cube)

        dimension = self.cube.dimension(dimension)
        hierarchy = dimension.hierarchy(hierarchy)

        levels = hierarchy.levels

        if depth == 0:
            raise ArgumentError("Depth for dimension values should not be 0")
        elif depth is not None:
            levels = levels[0:depth]

        attributes = []
        for level in levels:
            attributes.extend(level.attributes)

        cond = self.condition_for_cell(cell)

        dimensions = set(cut.dimension for cut in cell.cuts

        statement = ...

        join_expression = self....

    def condition_for_cell(self, cell):
        """Returns a tuple: (dimensions, condition)




        
