#
# Copyright 2008, 2009, 2010 Brett Adams
# Copyright 2014-2015 Mario Frasca <mario@anche.no>.
# Copyright 2017 Jardín Botánico de Quito
#
# This file is part of ghini.desktop.
#
# ghini.desktop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ghini.desktop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ghini.desktop. If not, see <http://www.gnu.org/licenses/>.
import logging
from gettext import gettext as _
from sqlalchemy.orm import class_mapper
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
import bauble.utils as utils
#from bauble.db import get_orm_entity_by_name
from bauble.error import check
from gi.repository import Gtk
from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import alphas8bit
from pyparsing import CaselessLiteral
from pyparsing import delimitedList
from pyparsing import Forward
from pyparsing import Group
from pyparsing import infixNotation
from pyparsing import Keyword
from pyparsing import Literal
from pyparsing import oneOf
from pyparsing import OneOrMore
from pyparsing import opAssoc
from pyparsing import quotedString
from pyparsing import Regex
from pyparsing import removeQuotes
from pyparsing import srange
from pyparsing import stringEnd
from pyparsing import Word
from pyparsing import WordEnd
from pyparsing import WordStart
from pyparsing import ZeroOrMore
from sqlalchemy import select
from sqlalchemy import except_
#from sqlalchemy import not_
from sqlalchemy import and_
from sqlalchemy import or_
#from sqlalchemy import Unicode
#from sqlalchemy import UnicodeText
from sqlalchemy.inspection import inspect
#from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import aliased
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql import Select, Alias, Subquery
from sqlalchemy.sql import func

from sqlalchemy.exc import NoInspectionAvailable

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


RelationProperty = RelationshipProperty

from sqlalchemy.orm import RelationshipProperty


def resolve_relationships(cls, steps, env):
    """
    Dynamically resolve relationships for a given class and steps.

    Args:
        cls: The current SQLAlchemy class being evaluated.
        steps: A list of relationship steps to resolve.
        env: The environment containing the session and other context.

    Returns:
        (stmt, current_cls): The updated statement and the final resolved class.
    """
    if not steps:
        raise ValueError("No relationship steps provided to resolve.")
        
    stmt = select(cls)  # Start with the base class
    current_cls = cls

    for step in steps:
        # Ensure we are inspecting the mapper of current_cls
        mapper = inspect(current_cls).mapper if isinstance(current_cls, AliasedClass) else inspect(current_cls)

        # Retrieve the relationship property
        if step not in mapper.relationships:
            raise ValueError(f"Relationship '{step}' not found on '{current_cls.__name__}'. Available: {list(mapper.relationships.keys())}")

        relationship_property = mapper.relationships[step]
        if not relationship_property:
            raise ValueError(f"Relationship '{step}' not found on '{current_cls.__name__}'.")

        # Resolve target class and alias it
        target_cls = relationship_property.mapper.class_
        if not target_cls:
            raise ValueError(f"Unable to resolve target class for relationship '{step}'.")

        aliased_entity = aliased(target_cls)
        stmt = stmt.join(aliased_entity, getattr(current_cls, step))
        current_cls = aliased_entity  # Update for next steps

    return stmt, current_cls

def search(text, session=None):
    results = set()
    for strategy in list(_search_strategies.values()):
        logger.debug(
            "applying search strategy %s from module %s"
            % (type(strategy).__name__, type(strategy).__module__)
        )
        results.update(strategy.search(text, session))
    return list(results)


class NoneToken(object):
    def __init__(self, t=None):
        pass

    def __repr__(self):
        return "(None<NoneType>)"

    def express(self):
        return None


class EmptyToken(object):
    def __init__(self, t=None):
        pass

    def __repr__(self):
        return "Empty"

    def express(self):
        return set()

    def __eq__(self, other):
        if isinstance(other, EmptyToken):
            return True
        if isinstance(other, set):
            return len(other) == 0
        return NotImplemented


class ValueABC(object):
    # abstract base class.

    def express(self):
        return self.value


class ValueToken(object):

    def __init__(self, t):
        self.value = t[0]

    def __repr__(self):
        return repr(self.value)

    def express(self):
        return self.value.express()


class StringToken(ValueABC):
    def __init__(self, t):
        self.value = t[0]  # no need to parse the string

    def __repr__(self):
        return "'%s'" % (self.value)


class NumericToken(ValueABC):
    def __init__(self, t):
        self.value = float(t[0])  # store the float value

    def __repr__(self):
        return "%s" % (self.value)


def smartdatetime(year_or_offset, *args):
    """return either datetime.datetime, or a day with given offset.

    When given only one argument, this is interpreted as an offset for
    timedelta, and it is added to datetime.today().  If given more
    arguments, it just behaves as datetime.datetime.

    """
    from datetime import datetime, timedelta

    if not args:
        return datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(year_or_offset)
    else:
        return datetime(year_or_offset, *args)


def smartboolean(*args):
    """translate args into boolean value

    Result is True whenever first argument is not numerically zero nor
    literally 'false'.  No arguments cause error.

    """
    if len(args) == 1:
        try:
            return float(args[0]) != 0.0
        except:
            return args[0].lower() != "false"
    return True


class TypedValueToken(ValueABC):
    # |<name>|<paramlist>|
    constructor = {
        "datetime": (smartdatetime, int),
        "bool": (smartboolean, str),
    }

    def __init__(self, t):
        logger.debug("constructing typedvaluetoken %s" % str(t))
        try:
            constructor, converter = self.constructor[t[1]]
        except KeyError:
            return
        params = tuple(converter(i) for i in t[3].express())
        self.value = constructor(*params)

    def __repr__(self):
        return "%s" % (self.value)

class IdentifierAction(object):
    def __init__(self, t):
        logger.debug("IdentifierAction::__init__(%s)" % t)
        self.steps = t[0][:-2:2]
        self.leaf = t[0][-1]

    def __repr__(self):
        return ".".join(self.steps + [self.leaf])


    def evaluate(self, env):
        """
        Return pair (stmt, attribute).

        The value associated with the identifier is an altered query where the
        joinpoint is the one relative to the attribute, and the attribute itself.
        """
        # If no steps, operate directly on the base table
        if not self.steps:
            stmt = select(env.domain)
            current_cls = env.domain
        else:
            # Resolve relationships dynamically
            stmt, current_cls = resolve_relationships(env.domain, self.steps, env)

            if stmt is None or current_cls is None:
                raise ValueError(f"Failed to resolve relationships for steps: {self.steps}")

        # Resolve the leaf attribute on the final class
        try:
            attr = getattr(current_cls, self.leaf)
        except AttributeError:
            raise ValueError(f"Attribute '{self.leaf}' not found on class '{current_cls}'.")

        logger.debug(f"Resolved attribute: {attr}")
        return stmt, attr

    def needs_join(self, env):
        return self.steps or []


class FilteredIdentifierAction(object):
    def __init__(self, t):
        logger.debug("FilteredIdentifierAction::__init__(%s)" % t)
        self.steps = t[0][:-7:2]
        self.filter_attr = t[0][-6]
        self.filter_op = t[0][-5]
        self.filter_value = t[0][-4]
        self.leaf = t[0][-1]

        # cfr: SearchParser.binop
        # = == != <> < <= > >= not like contains has ilike icontains ihas is
        self.operation = {
            "=": lambda x, y: x == y,
            "==": lambda x, y: x == y,
            "is": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            "<>": lambda x, y: x != y,
            "not": lambda x, y: x != y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "like": lambda x, y: utils.ilike(x, "%s" % y),
            "contains": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "has": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "ilike": lambda x, y: utils.ilike(x, "%s" % y),
            "icontains": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "ihas": lambda x, y: utils.ilike(x, "%%%s%%" % y),
        }.get(self.filter_op)

    def __repr__(self):
        return "{}[{}{}{}].{}".format(
            ".".join(self.steps),
            self.filter_attr,
            self.filter_op,
            self.filter_value,
            self.leaf,
        )

    def evaluate(self, env):
        """
        Evaluate the identifier and return the query and attribute.
        """
        # Use resolve_relationships to dynamically resolve steps
        stmt, current_cls = resolve_relationships(env.domain, self.steps, env)

        # Apply the filter clause on the resolved class
        if not hasattr(current_cls, self.filter_attr):
            raise ValueError(f"Attribute '{self.filter_attr}' not found on '{current_cls}'")

        attr = getattr(current_cls, self.filter_attr)
        clause = lambda x: self.operation(attr, x)
        stmt = stmt.filter(clause(self.filter_value.express()))

        # Resolve the final leaf attribute
        leaf_attr = getattr(current_cls, self.leaf, None)
        if not leaf_attr:
            raise ValueError(f"Leaf attribute '{self.leaf}' not found on '{current_cls}'")

        return stmt, leaf_attr

    def needs_join(self, env):
        return self.steps


class IdentExpression(object):
    def __init__(self, t):
        logger.debug("IdentExpression::__init__(%s)" % t)
        self.op = t[0][1]

        # cfr: SearchParser.binop
        # = == != <> < <= > >= not like contains has ilike icontains ihas is
        self.operation = {
            "=": lambda x, y: x == y,
            "==": lambda x, y: x == y,
            "is": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            "<>": lambda x, y: x != y,
            "not": lambda x, y: x != y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "like": lambda x, y: utils.ilike(x, "%s" % y),
            "contains": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "has": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "ilike": lambda x, y: utils.ilike(x, "%s" % y),
            "icontains": lambda x, y: utils.ilike(x, "%%%s%%" % y),
            "ihas": lambda x, y: utils.ilike(x, "%%%s%%" % y),
        }.get(self.op)
        self.operands = t[0][0::2]  # every second object is an operand

    def __repr__(self):
        return "({} {} {})".format(self.operands[0], self.op, self.operands[1])

    def evaluate(self, env):
        """
        Evaluate and return the filtered query result.
        """
        # Unpack the query and attribute from the first operand
        stmt, attr = self.operands[0].evaluate(env)

        # Check if the second operand represents an empty set
        if self.operands[1].express() == set():
            if self.op in ('is', '=', '=='):
                return stmt.filter(~attr.any())
            elif self.op in ('not', '<>', '!='):
                return stmt.filter(attr.any())

        # Apply the operation
        clause = lambda x: self.operation(attr, x)
        logger.debug('filtering on %s(%s)', type(attr), attr)

        # Directly filter using the attribute and clause
        stmt = stmt.filter(clause(self.operands[1].express()))
        return stmt
    
    def needs_join(self, env):
        """
        Collect join steps from operands, ensuring a flat list.
        """
        return [self.operands[0].needs_join(env)]        
        #joins = []
        #for operand in self.operands:
        #    steps = operand.needs_join(env)
        #    if steps:  # Only extend if steps are non-empty
        #        joins.extend(steps)
        #return joins


class ElementSetExpression(IdentExpression):
    # currently only implements `in`

    def evaluate(self, env):
        q, a = self.operands[0].evaluate(env)

        # Ensure 'q' is turned into a subquery
        if not isinstance(q, AliasedClass):
            q = q.subquery()

        stmt = select(q).filter(a.in_(self.operands[1].express()))
        return env.session.scalars(stmt)
        

class AggregatedExpression(IdentExpression):
    """select on value of aggregated function

    this one looks like ident.binop.value, but the ident is an
    aggregating function, so that the query has to be altered
    differently: not filter, but group_by and having.
    """

    def __init__(self, t):
        super().__init__(t)
        logger.debug("AggregatedExpression::__init__(%s)" % t)

    def evaluate(self, env):
        """
        Evaluate the aggregated function query.
        """
        # Get the query and attribute
        stmt, attr = self.operands[0].identifier.evaluate(env)
        
        if not isinstance(stmt, AliasedClass):
            stmt = stmt.subquery()

        stmt = (
            stmt.group_by(group_by_column)
            .having(clause(val))
        )

        # Resolve the aggregate function
        f = getattr(func, self.operands[0].function)

        # Build HAVING clause
        clause = lambda x: self.operation(f(attr), x)
        val = self.operands[1].express()

        # Group by the main table's ID
        main_table = stmt.column_descriptions[0]["type"]
        group_by_column = getattr(main_table, "id", None)
        if not group_by_column:
            raise ValueError("Main table must have an 'id' column to group by.")

        logger.debug(f"Applying aggregate function {f} to attribute {attr}")
        stmt = (
            stmt.group_by(group_by_column)
            .having(clause(val))
        )
        return stmt


class BetweenExpressionAction(object):
    def __init__(self, t):
        self.operands = t[0][0::2]  # every second object is an operand

    def __repr__(self):
        return "(BETWEEN %s %s %s)" % tuple(self.operands)

    def evaluate(self, env):
        q, a = self.operands[0].evaluate(env)

        # Validate the type of `q`
        if not isinstance(q, (AliasedClass, Alias)):
            raise ValueError(f"Invalid type for q: {type(q)}. Expected AliasedClass or subquery.")

        # Ensure `q` is a subquery
        if not isinstance(q, Subquery):
            q = q.subquery()

        # Validate the attribute `a`
        if not hasattr(a, 'clause_element'):
            raise ValueError(f"Invalid attribute for a: {a}. Expected SQLAlchemy column or expression.")

        # Build the filter clauses
        clause_low = lambda low: low <= a
        clause_high = lambda high: a <= high

        # Check operand values
        low_value = self.operands[1].express()
        high_value = self.operands[2].express()
        if low_value is None or high_value is None:
            raise ValueError("Operands[1] or Operands[2] returned None for express().")

        logger.debug(f"Building query with low={low_value}, high={high_value}")

        # Construct the statement
        stmt = select(q).filter(
            and_(
                clause_low(low_value),
                clause_high(high_value)
            )
        )

        # Execute and return the results
        try:
            return env.session.scalars(stmt)
        except Exception as e:
            logger.error(f"Failed to execute statement: {stmt}. Error: {e}")
            raise


    def needs_join(self, env):
        return [self.operands[0].needs_join(env)]


class UnaryLogical(object):
    ## abstract base class. `name` is defined in derived classes
    def __init__(self, t):
        self.op, self.operand = t[0]

    def __repr__(self):
        return "%s %s" % (self.name, str(self.operand))

    def needs_join(self, env):
        """
        Return join steps from operand, ensuring a flat list.
        """
        steps = self.operand.needs_join(env)
        return steps if steps else []


class BinaryLogical(object):
    ## abstract base class. `name` is defined in derived classes
    def __init__(self, t):
        self.op = t[0][1]
        self.operands = t[0][0::2]

    def __repr__(self):
        return "(%s %s %s)" % (self.operands[0], self.name, self.operands[1])

    def needs_join(self, env):
        return self.operands[0].needs_join(env) + \
               self.operands[1].needs_join(env)


class SearchAndAction(BinaryLogical):
    name = "AND"

    def evaluate(self, env):
        result = self.operands[0].evaluate(env)
        for operand in self.operands[1:]:
            result = result.intersect(operand.evaluate(env))
        return result


class SearchOrAction(BinaryLogical):
    name = 'OR'

    def evaluate(self, env):
        result = self.operands[0].evaluate(env)
        for operand in self.operands[1:]:
            result = result.union(operand.evaluate(env))
        return result


class SearchNotAction(UnaryLogical):
    name = 'NOT'

    def evaluate(self, env):
        """
        Evaluate the NOT action, which excludes the results of the operand
        from the base query.
        """
        # Start with a SELECT statement for the main domain
        stmt = select(env.domain)

        # Apply joins for all domains
        for domain in env.domains:
            if domain:  # Skip empty domains
                stmt = stmt.join(domain)

        # Exclude the operand's results using an EXCEPT clause
        operand_stmt = self.operand.evaluate(env)
        stmt = except_(stmt, operand_stmt)

        return stmt


class ParenthesisedQuery(object):
    def __init__(self, t):
        self.content = t[1]

    def __repr__(self):
        return "(%s)" % self.content.__repr__()

    def evaluate(self, env):
        return self.content.evaluate(env)

    def needs_join(self, env):
        return self.content.needs_join(env)

class QueryAction(object):
    def __init__(self, t):
        self.domain = t[0]
        self.filter = t[1][0]

    def __repr__(self):
        return "SELECT * FROM %s WHERE %s" % (self.domain, self.filter)

    def invoke(self, search_strategy):
        """
        Update search_strategy object with statement results.

        Queries can use more database-specific features. This also
        means that the same query might not work the same on different
        database types. For example, on a PostgreSQL database you can
        use ilike but this would raise an error on SQLite.

        Args:
            search_strategy: The search strategy object.

        Returns:
            A set of results from the search.
        """

        logger.debug(
            "QueryAction:invoke - %s(%s) %s(%s)"
            % (type(self.domain), self.domain, type(self.filter), self.filter)
        )
        domain = self.domain
        check(
            domain in search_strategy._domains
            or domain in search_strategy._shorthand,
            "Unknown search domain: %s" % domain,
        )
        self.domain = search_strategy._shorthand.get(domain, domain)
        self.domain = search_strategy._domains[domain][0]
        self.search_strategy = search_strategy

        result = set()
        if search_strategy._session is not None:
            self.domains = self.filter.needs_join(self)
            self.session = search_strategy._session

            # Unpack the evaluated query and attribute
            stmt = self.filter.evaluate(self)

            if isinstance(stmt, Select):
                stmt = stmt.subquery()

            result.update(self.session.scalars(stmt).all())


        if None in result:
            logger.warning("removing None from result set")
            result = {i for i in result if i is not None}
        return result


class StatementAction(object):
    def __init__(self, t):
        self.content = t[0]

    def __repr__(self):
        return repr(self.content)

    def invoke(self, search_strategy):
        return self.content.invoke(search_strategy)


class BinomialNameAction(object):
    """created when the parser hits a binomial_name token.

    Searching using binomial names returns one or more species objects.
    """

    def __init__(self, t):
        self.genus_epithet = t[0]
        self.species_epithet = t[1]

    def __repr__(self):
        return "%s %s" % (self.genus_epithet, self.species_epithet)

    def invoke(self, search_strategy):
        from bauble.plugins.plants.genus import Genus
        from bauble.plugins.plants.species import Species
        logger.debug('BinomialNameAction:invoke')

        stmt = (
            select(Species)
            .filter(
                or_(
                    Species.sp.startswith(self.species_epithet),
                    and_(self.species_epithet == 'sp', Species.infrasp1 == 'sp')
                )
            )
            .join(Genus)
            .filter(Genus.genus.startswith(self.genus_epithet))
        )

        result = set(search_strategy._session.scalars(stmt).all())
        if None in result:
            logger.warning('removing None from result set')
            result = {i for i in result if i is not None}
        return result


class DomainExpressionAction(object):
    """created when the parser hits a domain_expression token.

    Searching using domain expressions is a little more magical than an
    explicit query. you give a domain, a binary_operator and a value,
    the domain expression will return all object with at least one
    property (as passed to add_meta) matching (according to the binop)
    the value.
    """

    def __init__(self, t):
        self.domain = t[0]
        self.cond = t[1]
        self.values = t[2]

    def __repr__(self):
        return "%s %s %s" % (self.domain, self.cond, self.values)

    from sqlalchemy import select, or_
    from sqlalchemy import inspect

    def invoke(self, search_strategy):
        logger.debug("DomainExpressionAction:invoke")
        try:
            if self.domain in search_strategy._shorthand:
                self.domain = search_strategy._shorthand[self.domain]
            cls, properties = search_strategy._domains[self.domain]
        except KeyError:
            raise KeyError(_("Unknown search domain: %s") % self.domain)

        # Start by building a SELECT statement
        stmt = select(cls)

        # here is the place where to optionally filter out unrepresented
        # domain values. each domain class should define its own 'I have
        # accessions' filter. see issue #42

        result = set()

        # Handle wildcard case
        if self.values == "*":
            # execute directly if we want all records
            result.update(search_strategy._session.scalars(stmt).all())

            return result

        try:
            mapper = inspect(cls).mapper  # Use inspect to get mapper
        except NoInspectionAvailable:
            raise ValueError(f"Cannot inspect class {cls}. Ensure it's mapped.")

        inspect(cls)  # Validate cls as a mapped class

        # Define conditions
        if self.cond in ('like', 'ilike'):
            condition = lambda col: lambda val: getattr(col, self.cond)(f'{val}')
        elif self.cond in ('contains', 'icontains', 'has', 'ihas'):
            condition = lambda col: lambda val: getattr(col, 'ilike')(f'%{val}%')
        elif self.cond == '=':
            condition = lambda col: lambda val: col == utils.utf8(val)
        else:
            condition = lambda col: lambda val: col.op(self.cond)(val)

        # Apply filters for the properties
        for col_name in properties:
            try:
                col = getattr(cls, col_name)
            except AttributeError:
                logger.warning(f"Column '{col_name}' not found on class '{cls}'.")
                continue

            ors = or_(*[condition(col)(val) for val in self.values.express()])
            stmt = stmt.filter(ors)  # Add filter to statement

        result.update(search_strategy._session.scalars(stmt).all())

        # Remove None values from result
        if None in result:
            logger.warning('removing None from result set')
            result = {i for i in result if i is not None}

        return result


class AggregatingAction(object):

    def __init__(self, t):
        logger.debug("AggregatingAction::__init__(%s)" % t)
        self.function = t[0]
        self.identifier = t[2]

    def __repr__(self):
        return "(%s %s)" % (self.function, self.identifier)
    
    def needs_join(self, env):
        return [self.identifier.needs_join(env)]

    def evaluate(self, env):
        """return pair (query, attribute)

        let the identifier compute the query and its attribute, we do
        not need alter anything right now since the condition on the
        aggregated identifier is applied in the HAVING and not in the
        WHERE.

        """
        q, a = self.identifier.evaluate(env)
        return q, a


class ValueListAction(object):

    def __init__(self, t):
        logger.debug("ValueListAction::__init__(%s)" % t)
        self.values = t[0]

    def __repr__(self):
        return str(self.values)

    def express(self):
        return [i.express() for i in self.values]

    from sqlalchemy import select, or_

    def invoke(self, search_strategy):
        """
        Called when the whole search string is a value list.

        Search with a list of values is the broadest search and
        searches all the mapper and the properties configured with
        add_meta().
        """

        logger.debug('ValueListAction:invoke')
        # make searches case-insensitive, in postgres use ilike,
        # in other use upper()
        def ilike_filter(cls, column, value):
            """Portable case-insensitive filtering."""
            return func.lower(getattr(cls, column)).like(f"%{value.lower()}%")

        result = set()

        for cls, columns in search_strategy._properties.items():
            # Build cross product of columns and values
            column_value_pairs = [
                (column, value) for column in columns for value in self.express()
            ]

            # Build a filter condition for each column-value pair
            filters = [
                ilike_filter(cls, column, value) for column, value in column_value_pairs
            ]

            # Execute the query for the current class
            query = search_strategy._session.query(cls).filter(or_(*filters))
            result.update(query.all())

        # Post-process the results
        def replace(item):
            try:
                replacement = item.replacement()
                logger.debug('Replacing %s with %s in result set', item, replacement)
                return replacement
            except Exception as e:
                logger.debug('No replacement for %s due to: %s', item, e)
                return item

        result = {replace(item) for item in result if item is not None}

        logger.debug("Result is now %s", result)
        return result

wordStart, wordEnd = WordStart(), WordEnd()


class SearchParser:
    """The parser for bauble.search.MapperSearch"""

    numeric_value = Regex(r"[-]?\d+(\.\d*)?([eE]\d+)?").setParseAction(
        NumericToken
    )("number")
    unquoted_string = Word(alphanums + alphas8bit + "%.-_*;:")
    string_value = (
        quotedString.setParseAction(removeQuotes) | unquoted_string
    ).setParseAction(StringToken)("string")

    none_token = Literal("None").setParseAction(NoneToken)
    empty_token = Literal("Empty").setParseAction(EmptyToken)

    value_list = Forward()
    typed_value = (
        Literal("|")
        + unquoted_string
        + Literal("|")
        + value_list
        + Literal("|")
    ).setParseAction(TypedValueToken)

    value = (
        typed_value
        | WordStart("0123456789.-e") + numeric_value + WordEnd("0123456789.-e")
        | none_token
        | empty_token
        | string_value
    ).setParseAction(ValueToken)("value")
    value_list <<= Group(
        OneOrMore(value) ^ delimitedList(value)
    ).setParseAction(ValueListAction)("value_list")

    domain = Word(alphas, alphanums)
    binop = oneOf(
        "= == != <> < <= > >= not like contains has ilike " "icontains ihas is"
    )
    binop_set = oneOf("in")
    equals = Literal("=")
    star_value = Literal("*")
    domain_values = (value_list.copy())("domain_values")
    domain_expression = (
        (domain + equals + star_value + stringEnd)
        | (domain + binop + domain_values + stringEnd)
    ).setParseAction(DomainExpressionAction)("domain_expression")

    caps = srange("[A-Z]")
    lowers = caps.lower()
    binomial_name = (Word(caps, lowers) + Word(lowers)).setParseAction(
        BinomialNameAction
    )("binomial_name")

    AND_ = wordStart + (CaselessLiteral("AND") | Literal("&&")) + wordEnd
    OR_ = wordStart + (CaselessLiteral("OR") | Literal("||")) + wordEnd
    NOT_ = wordStart + (CaselessLiteral("NOT") | Literal("!")) + wordEnd
    BETWEEN_ = wordStart + CaselessLiteral("BETWEEN") + wordEnd

    aggregating_func = (
        Literal("sum") | Literal("min") | Literal("max") | Literal("count")
    )

    query_expression = Forward()("filter")

    atomic_identifier = Word(alphas + "_", alphanums + "_")
    identifier = Group(
        atomic_identifier
        + ZeroOrMore("." + atomic_identifier)
        + "["
        + atomic_identifier
        + binop
        + value
        + "]"
        + "."
        + atomic_identifier
    ).setParseAction(FilteredIdentifierAction) | Group(
        atomic_identifier + ZeroOrMore("." + atomic_identifier)
    ).setParseAction(
        IdentifierAction
    )

    aggregated = (
        aggregating_func + Literal("(") + identifier + Literal(")")
    ).setParseAction(AggregatingAction)
    ident_expression = (
        Group(identifier + binop + value).setParseAction(IdentExpression)
        | Group(identifier + binop_set + value_list).setParseAction(
            ElementSetExpression
        )
        | Group(aggregated + binop + value).setParseAction(
            AggregatedExpression
        )
        | (Literal("(") + query_expression + Literal(")")).setParseAction(
            ParenthesisedQuery
        )
    )
    between_expression = Group(
        identifier + BETWEEN_ + value + AND_ + value
    ).setParseAction(BetweenExpressionAction)
    query_expression <<= infixNotation(
        (ident_expression | between_expression),
        [
            (NOT_, 1, opAssoc.RIGHT, SearchNotAction),
            (AND_, 2, opAssoc.LEFT, SearchAndAction),
            (OR_, 2, opAssoc.LEFT, SearchOrAction),
        ],
    )
    query = (
        domain
        + Keyword("where", caseless=True).suppress()
        + Group(query_expression)
        + stringEnd
    ).setParseAction(QueryAction)

    statement = (
        query("query")
        | domain_expression("domain")
        | binomial_name("binomial")
        | value_list("value_list")
    ).setParseAction(StatementAction)("statement")

    def parse_string(self, text):
        """request pyparsing object to parse text

        `text` can be either a query, or a domain expression, or a list of
        values. the `self.statement` pyparsing object parses the input text
        and return a pyparsing.ParseResults object that represents the input
        """

        return self.statement.parseString(text)


class SearchStrategy(object):
    """
    Interface for adding search strategies to a view.
    """

    def search(self, text, session=None):
        """
        :param text: the search string
        :param session: the session to use for the search

        Return an iterator that iterates over mapped classes retrieved
        from the search.
        """
        logger.debug(
            'SearchStrategy "{}"({})'.format(text, self.__class__.__name__)
        )


class MapperSearch(SearchStrategy):
    """
    Mapper Search support three types of search expression:
    1. value searches: search that are just list of values, e.g. value1,
    value2, value3, searches all domains and registered columns for values
    2. expression searches: searched of the form domain=value, resolves the
    domain and searches specific columns from the mapping
    3. query searchs: searches of the form domain where ident.ident = value,
    resolve the domain and identifiers and search for value
    """

    _domains = {}
    _shorthand = {}
    _properties = {}

    def __init__(self):
        super().__init__()
        self._results = set()
        self.parser = SearchParser()

    def add_meta(self, domain, cls, properties):
        """Add a domain to the search space

        an example of domain is a database table, where the properties would
        be the table columns to consider in the search.  continuing this
        example, a record is be selected if any of the fields matches the
        searched value.

        :param domain: a string, list or tuple of domains that will resolve
                       a search string to cls.  domain act as a shorthand to
                       the class name.
        :param cls: the class the domain will resolve to
        :param properties: a list of string names of the properties to
                           search by default
        """

        logger.debug(
            "%s.add_meta(%s, %s, %s)" % (self, domain, cls, properties)
        )

        check(
            isinstance(properties, list),
            _(
                "MapperSearch.add_meta(): "
                "default_columns argument must be list"
            ),
        )
        check(
            len(properties) > 0,
            _(
                "MapperSearch.add_meta(): "
                "default_columns argument cannot be empty"
            ),
        )
        if isinstance(domain, (list, tuple)):
            self._domains[domain[0]] = (cls, properties)
            for d in domain[1:]:
                self._shorthand[d] = domain[0]
        else:
            # Extract the first word for single-word domain strings
            #domain_key = domain.split(" ")[0]
            self._domains[domain] = (cls, properties)
        self._properties[cls] = properties

    @classmethod
    def get_domain_classes(cls):
        d = {}
        for domain, item in cls._domains.items():
            d.setdefault(domain, item[0])
        return d

    def search(self, text, session=None):
        """
        Returns a set() of database hits for the text search string.

        If session=None then the session should be closed after the results
        have been processed or it is possible that some database backends
        could cause deadlocks.
        """
        super().search(text, session)
        self._session = session

        self._results.clear()
        # 1) Parse string => statement
        parse_result = self.parser.parse_string(text)
        statement = parse_result.statement
        logger.debug("statement : {}({})".format(type(statement), statement))

        raw_results = statement.invoke(self)  # Likely a set of IDs
        logger.debug("raw_results : {}".format(raw_results))

        action_name = parse_result.getName()  # e.g. "domain_expression", "query", "value_list"
        logger.debug("Pyparsing action: %s", action_name)
        logger.debug("raw_results = %s", raw_results)

        if not raw_results:
            return self._results  # empty, just return now

        # 2) If parse_result is a ValueListAction, we do the domain fallback.
        #    If domain_expression or query, skip it.
        if action_name == "value_list":
            # your old "domain_name = text.split(' ')[0]" logic
            # possibly checking if that single token is in _domains
            domain_name = text.split(" ")[0]
            domain_class = self._domains.get(domain_name, [None])[0]
            if domain_class is not None:
                # subquery approach
                subq = (
                    select(domain_class.id)
                    .where(domain_class.id.in_(obj.id for obj in raw_results))
                    .subquery()
                )
                orm_results = (
                    self._session.query(domain_class)
                    .join(subq, domain_class.id == subq.c.id)
                    .all()
                )
                self._results.update(orm_results)
            else:
                # not recognized => keep raw_results
                self._results.update(raw_results)
        else:
            # 3) For domain_expression or query, just accept raw_results
            self._results.update(raw_results)

        # these _results get filled in when the parse actions are called
        return self._results


# list of search strategies to be tried on each search string
_search_strategies = {"MapperSearch": MapperSearch()}


def add_strategy(strategy):
    obj = strategy()
    _search_strategies[obj.__class__.__name__] = obj


def get_strategy(name):
    return _search_strategies.get(name, None)


class SchemaBrowser(Gtk.VBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_property("spacing", 10)
        # WARNING: this is a hack from MapperSearch
        self.domain_map = MapperSearch.get_domain_classes().copy()

        frame = Gtk.Frame(_("Search Domain"))
        self.pack_start(frame, False, False, 0)
        self.table_combo = Gtk.ComboBoxText()
        frame.add(self.table_combo)
        for key in sorted(self.domain_map.keys()):
            self.table_combo.append_text(key)

        self.table_combo.connect("changed", self.on_table_combo_changed)

        self.prop_tree = Gtk.TreeView()
        self.prop_tree.set_headers_visible(False)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Property"), cell)
        self.prop_tree.append_column(column)
        column.add_attribute(cell, "text", 0)

        self.prop_tree.connect("test_expand_row", self.on_row_expanded)

        frame = Gtk.Frame(_("Domain Properties"))
        sw = Gtk.ScrolledWindow()
        sw.add(self.prop_tree)
        frame.add(sw)
        self.pack_start(frame, True, True, 0)

    def _insert_props(self, mapper, model, treeiter):
        """
        Insert the properties from mapper into the model at treeiter
        """
        column_properties = sorted(
            [
                x
                for x in mapper.iterate_properties
                if isinstance(x, ColumnProperty) and not x.key.startswith("_")
            ],
            key=lambda k: (k.key != "id", not k.key.endswith("_id"), k.key),
        )
        for prop in column_properties:
            model.append(treeiter, [prop.key, prop])

        relation_properties = sorted(
            [
                x
                for x in mapper.iterate_properties
                if isinstance(x, RelationProperty)
                and not x.key.startswith("_")
            ],
            key=lambda k: k.key,
        )
        for prop in relation_properties:
            it = model.append(treeiter, [prop.key, prop])
            model.append(it, ["", None])

    def on_row_expanded(self, treeview, treeiter, path):
        """
        Called before the row is expanded and populates the children of the
        row.
        """
        logger.debug("on_row_expanded")
        model = treeview.props.model
        parent = treeiter
        while model.iter_has_child(treeiter):
            nkids = model.iter_n_children(parent)
            child = model.iter_nth_child(parent, nkids - 1)
            model.remove(child)

        # prop should always be a RelationProperty
        prop = treeview.props.model[treeiter][1]
        self._insert_props(prop.mapper, model, treeiter)

    def on_table_combo_changed(self, combo, *args):
        """
        Change the table to use for the query
        """
        utils.clear_model(self.prop_tree)
        it = combo.get_active_iter()
        domain = combo.props.model[it][0]
        mapper = inspect(self.domain_map[domain])
        model = Gtk.TreeStore(str, object)
        root = model.get_iter_root()
        self._insert_props(mapper, model, root)
        self.prop_tree.set_property("model", model)
