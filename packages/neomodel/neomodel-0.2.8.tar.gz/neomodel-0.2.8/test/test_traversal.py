from neomodel.traversal import Traversal
from neomodel import (StructuredNode, RelationshipTo, RelationshipFrom)


class Friend(StructuredNode):
    name = StringProperty(unique_index=True)
    is_from = RelationshipTo('Country', 'IS_FROM')
