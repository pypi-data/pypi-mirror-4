"""
The LogicTree provides a means of parsing a raw JSON-compatible structure. The
grammar is as follows:

    NODE    ::= F_NODE | L_NODE

    F_NODE  ::= '{'
                    'id'        ::= INT
                    'operator'  ::= STRING
                    'value'     ::= STRING | NUMBER | BOOL | None
                '}'

    L_NODE  ::= '{'
                    'type'  ::= 'AND' | 'OR'
                    'children'  ::= '[' NODE{2,} ']'
                '}'

Two examples as follows:

    # single F_NODE
    {
        'id': 1,
        'operator': 'exact',
        'value': 30
    }

    # nested L_NODE structure
    {
        'type': 'OR',
        'children': [{
            'id': 1,
            'operator': 'exact',
            'value': 30
        }, {
            'id': 1,
            'operator': 'exact',
            'value': 45
        }]
    }
"""
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS
from avocado.models import Field, Criterion, CriterionField

AND = 'AND'
OR = 'OR'

class Node(object):
    condition = None
    annotations = None
    text = None
    extra = None

    def get_field_ids(self):
        return []

    def apply(self, queryset, *args, **kwargs):
        if self.annotations:
            queryset = queryset.values('pk').annotate(**self.annotations)
        if self.condition:
            queryset = queryset.filter(self.condition)
        if self.extra:
            queryset = queryset.extra(**self.extra)
        return queryset


class Condition(Node):
    "Contains information for a single query condition."
    def __init__(self, context=None, using=DEFAULT_MODELTREE_ALIAS, **kwargs):
        self.context = context
        self.using = using
        self.id = kwargs['id']
        self.operator = kwargs['operator']
        self.value = kwargs['value']
        self.concept_id = kwargs['concept_id']

    @property
    def _meta(self):
        if not hasattr(self, '__meta'):
            self.__meta = self.field.translate(self.operator, self.value,
                using=self.using, **self.context)
        return self.__meta

    @property
    def criterion(self):
        if not hasattr(self, '_criterion'):
            self._criterion = Criterion.objects.get(id=self.concept_id)
        return self._criterion

    @property
    def criterionfield(self):
        if not hasattr(self, '_criterionfield'):
            self._criterionfield = CriterionField.objects.get(concept__id=self.concept_id,
                field__id=self.id)
        return self._criterionfield

    @property
    def field(self):
        if not hasattr(self, '_field'):
            self._field = Field.objects.get(id=self.id)
        return self._field

    @property
    def condition(self):
        return self._meta.get('condition', None)

    @property
    def annotations(self):
        return self._meta.get('annotations', None)

    @property
    def extra(self):
        return self._meta.get('extra', None)

    @property
    def text(self, flatten=True):
        operator = self._meta['cleaned_data']['operator']
        # the original value is used here to prevent representing a different
        # value from what the client had submitted. this text has no impact
        # on the stored 'cleaned' data structure
        value = self._meta['raw_data']['value']
        return self.criterionfield.text(operator, value)

    def get_field_ids(self):
        return [self.id]


class LogicalOperator(Node):
    "Provides a logical relationship between it's children."
    def __init__(self, type, using=DEFAULT_MODELTREE_ALIAS):
        self.using = using
        self.type = (type.upper() == AND) and AND or OR
        self.children = []

    def _combine(self, q1, q2):
        if self.type.upper() == OR:
            return q1 | q2
        return q1 & q2

    @property
    def condition(self):
        if not hasattr(self, '_condition'):
            condition = None
            for node in self.children:
                if node.condition:
                    if condition:
                        condition = self._combine(node.condition, condition)
                    else:
                        condition = node.condition
            self._condition = condition
        return self._condition

    @property
    def annotations(self):
        if not hasattr(self, '_annotations'):
            self._annotations = {}
            for node in self.children:
                if node.annotations:
                    self._annotations.update(node.annotations)
        return self._annotations

    @property
    def extra(self):
        if not hasattr(self, '_extra'):
            self._extra = {}
            for node in self.children:
                if node.extra:
                    for key, value in node.extra.items():
                        _type = type(value)
                        # Initialize an empty container for the value type..
                        self._extra.setdefault(key, _type())
                        if _type is list:
                            current = self._extra[key][:]
                            [self._extra[key].append(x) for x in value if x not in current]
                        elif _type is dict:
                            self._extra[key].update(value)
                        else:
                            raise TypeError('The `.extra()` method only takes '
                                'list of dicts as keyword values')
        return self._extra

    @property
    def text(self, flatten=True):
        if not hasattr(self, '_text'):
            children = []
            for node in self.children:
                t = node.text
                # flatten if nested conditions are also AND's
                if not hasattr(node, 'type') or node.type.lower() == self.type.lower():
                    children.append(t)
                else:
                    children.append('(%s)' % t)
            self._text = (' %s ' % self.type.lower()).join(children)
        return self._text

    def get_field_ids(self):
        ids = []
        for node in self.children:
            ids.extend(node.get_field_ids())
        return ids


def transform(rnode, pnode=None, using=DEFAULT_MODELTREE_ALIAS, **context):
    "Takes the raw data structure and converts it into the node tree."
    if not rnode:
        return Node()

    if rnode.has_key('children'):
        # ensure the logic makes sense
        if len(rnode['children']) < 2:
            raise TypeError, 'a logical operator must apply to 2 or more ' \
                'conditions'
        node = LogicalOperator(rnode['type'], using=using)
        for child in rnode['children']:
            transform(child, node, using=using, **context)
    else:
        node = Condition(context, using=using, **rnode)
    # top level node returns, i.e. no parent node
    if pnode is None:
        return node
    pnode.children.append(node)
