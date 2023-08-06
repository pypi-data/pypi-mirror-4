""" Constructs for SphinxQL generation"""

from sqlalchemy.sql import expression, func

__all__ = ("Select", "Replace", "select", "replace")


class _Options(object):

    def __init__(self, options):
        self.options = list(options)

    def extend(self, options):
        self.options.extend(options)

    def _clone(self):
        return _Options(self.options[:])

    def __iter__(self):
        return iter(self.options)


class MatchClause(expression.ClauseElement):

    __visit_name__ = "match"

    def __init__(self, query):
        self.query = query


class Select(expression.Select):
    """ SphinxQL SELECT construct.

    See corresponding doc section_.

    .. _section: http://sphinxsearch.com/docs/2.0.2/sphinxql-select.html
    """

    _within_group_order_by_clause = expression.ClauseList()
    _options = None

    def __init__(self, columns, *args, **kwargs):
        columns = columns + [func.weight().label("__weight__")]
        super(Select, self).__init__(columns, *args, **kwargs)

    def with_only_columns(self, columns):
        columns = columns + [func.weight().label("__weight__")]
        return super(Select, self).with_only_columns(columns)

    @expression._generative
    def match(self, query):
        """ Provide full text query for index

        Sphinx uses `extended query syntax`_ in SphinxQL.

        .. _`extended query syntax`: \
                http://sphinxsearch.com/docs/2.0.2/extended-syntax.html
        """
        self.append_whereclause(MatchClause(query))

    @expression._generative
    def within_group_order_by(self, *clauses):
        self.append_within_group_order_by(*clauses)

    @expression._generative
    def options(self, *args, **kwargs):
        """ Provide options to execute query

        Available options described here_.

        .. _here: http://sphinxsearch.com/docs/2.0.2/sphinxql-select.html
        """
        options = list(args) + kwargs.items()
        if self._options is None:
            self._options = _Options(options)
        else:
            self._options.extend(options)

    def append_within_group_order_by(self, *clauses):
        """Append the given WITHIN GROUP ORDER BY criterion applied to this
        selectable.

        The criterion will be appended to any pre-existing WITHIN GROUP ORDER BY
        criterion.
        """
        if len(clauses) == 1 and clauses[0] is None:
            self._within_group_order_by_clause = expression.ClauseList()
        else:
            if getattr(self, '_within_group_order_by_clause', None) is not None:
                clauses = list(self._within_group_order_by_clause) \
                        + list(clauses)
            self._within_group_order_by_clause = expression.ClauseList(*clauses)

    def _copy_internals(self, clone=expression._clone, **kw):
        super(Select, self)._copy_internals(clone=clone, **kw)
        for attr in '_within_group_order_by_clause', '_options':
            if getattr(self, attr) is not None:
                setattr(self, attr, clone(getattr(self, attr), **kw))

    def get_children(self, column_collections=True, **kwargs):
        """return child elements as per the ClauseElement specification."""
        c = super(Select, self).get_children(
            column_collections=column_collections, **kwargs)
        return c + [x for x
                    in self._within_group_order_by_clause
                    if x is not None]


class Replace(expression.Insert):
    """Represent an REPLACE construct.

    The :class:`.Replace` object is created using the :func:`~.replace()` function.

    See also:

    :ref:`coretutorial_insert_expressions`

    """
    __visit_name__ = 'replace'


def replace(table, values=None, inline=False, **kwargs):
    return Replace(table, values, inline=inline, **kwargs)


def select(columns=None, whereclause=None, from_obj=[], **kwargs):
    """ Factory for creating :class:`.Select` constructs.

    Ressembles :func:`sqlalchemy.sql.expression.select`.
    """
    return Select(columns, whereclause=whereclause, from_obj=from_obj, **kwargs)
