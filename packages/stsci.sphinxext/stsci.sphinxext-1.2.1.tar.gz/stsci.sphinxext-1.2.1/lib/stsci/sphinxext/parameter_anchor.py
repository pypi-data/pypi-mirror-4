"""
Adds HTML id's to the parameter names in Numpy-formatted HTML.
"""

from docutils import nodes

def setup(app):
    app.connect("doctree-resolved", add_parameter_anchors)

class Visitor(nodes.NodeVisitor):
    def default_visit(self, node):
        pass

    def unknown_visit(self, node):
        pass

    def visit_field(self, node):
        if (type(node[0]) == nodes.field_name and
            node[0].astext().strip().lower() == 'parameters'):
            field_body = node[1]
            for subnode in field_body:
                parnode = subnode[0]
                if isinstance(parnode, nodes.strong):
                    name = parnode.astext()
                    parnode['ids'].append(name)

def add_parameter_anchors(app, doctree, fromdocname):
    doctree.walk(Visitor(doctree))

