"""

    sautils -- SQLAlchemy utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Various SQLAlchemy utilities which are a little specific to be proposed to
    main SQLAlchemy distribution.

"""

from sqlalchemy import exists, text, exc
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import select, and_, literal, cast, types
from sqlalchemy.sql.expression import (
    Executable, ClauseElement, Alias, ColumnClause)

__all__ = ('insert_from_select', 'idem_insert_from_select', 'idem_insert', 'sqltype')

class InsertFromSelect(Executable, ClauseElement):
    """ Insert from select"""

    def __init__(self, table, select, *fields, **kw):
        self.table = table
        self.select = select
        self.fields = fields

@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    if element.fields:
        f = ' (%s) ' % ', '.join(element.fields)
    else:
        f = ' '
    return 'INSERT INTO %s%s(%s)' % (
        compiler.process(element.table, asfrom=True),
        f,
        compiler.process(element.select)
    )

insert_from_select = InsertFromSelect

class UpsertNode(Executable, ClauseElement):

    def __init__(self, update, insert):
        self.update = update
        self.insert = insert
        self._returning = None

@compiles(UpsertNode)
def visit_upsert_node(element, compiler, **kw):
    return 'WITH update as (%s) %s' % (
        compiler.process(element.update),
        compiler.process(element.insert)
        )

def idem_insert_from_select(table, q, *fields):
    """ Idempotent insert from select"""
    sq = q.alias('__q')
    pks = table.primary_key.columns
    q = (select([sq])
        .select_from(sq.outerjoin(table,and_(*[sq.c[c.key] == c for c in pks])))
        .where(list(pks)[0] == None))
    return insert_from_select(table, q, *fields)

def idem_insert(table, **values):
    """ Idempotent insert"""
    values = values.items()
    fields = [k for (k, v) in values.items()]
    vals = [cast(literal(v, table.c[k].type), table.c[k].type).label(k)
            for (k, v) in values]
    return idem_insert_from_select(table, select(vals), *fields)

def upsert(table, **values):
    """ Upsert"""
    pks = table.primary_key.columns
    try:
        pks_pred = and_(*[c == values[c.key] for c in pks])
    except KeyError as e:
        raise exc.ArgumentError('missing pk for upsert: %s' % e)
    update = (table.update()
        .values(**values)
        .where(pks_pred)
        .returning(literal(1)))
    fields = [k for (k, v) in values.items()]
    vals = [cast(literal(v, table.c[k].type), table.c[k].type).label(k)
            for (k, v) in values.items()]
    insert = insert_from_select(
        table,
        select(vals).where('not exists (select 1 from update)'),
        *fields)

    return UpsertNode(update, insert)

class TypeCoercion(types.UserDefinedType):

    def __init__(self, name):
        self.name = name

    def get_col_spec(self):
        return self.name

    def bind_processor(self, dialect):
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process

sqltype = TypeCoercion
