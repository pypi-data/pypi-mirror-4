class QueryArgs(object):
    @property
    def order_by(self):
        order_by = self.order_by_value

        if order_by:
            if order_by[0] in ('-', '+'):
                sort_dir, field = -1 if order_by[0] == '-' else 1, order_by[1:]
            else:
                sort_dir, field = 1, order_by
            order_by = [(field, sort_dir)]

        return order_by

    def __init__(self, query={}, select=None, distinct=None, limit=0,
                 order_by=None):
        """A holder for query arguments.

        :param query: An optional query.
        :param select: An optional select to limit the fields in the dframe.
        :param distinct: Return distinct entries for this field.
        :param limit: Limit on the number of rows in the returned dframe.
        :param order_by: Sort resulting rows according to a column value and
            sign indicating ascending or descending.

        Example of `order_by`:

          - ``order_by='mycolumn'``
          - ``order_by='-mycolumn'``
        """

        self.query = query
        self.select = select
        self.distinct = distinct
        self.limit = limit
        self.order_by_value = order_by
