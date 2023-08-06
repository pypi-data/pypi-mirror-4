class Traversal(object):
    def __init__(self, start_node):
        assert hasattr('__node__', self.start_node)
        self.start_node = start_node
        self.query = [{'start': self.start_node.__node__.id,
            'class': self.start_node.__class__}]

    def traverse(self, rel_manager):
        assert hasattr(rel_manager, self.start_node)
        manager = getattr(rel_manager. self.start_node)
        self.query.append(manager.description)

    def execute(self):
        target = self.query[-1]['name']
        self.query.append({'return': target})
        return self.query
