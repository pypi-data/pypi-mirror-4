from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring

from pkgme.package_files import default_package_file_group


class PkgmeInfoElementsDirective(Directive):

    def get_elements(self):
        return default_package_file_group.get_elements()

    def split_required(self, elements):
        required = set()
        not_required = set()
        for element in elements:
            if element.required:
                required.add(element)
            else:
                not_required.add(element)
        return required, not_required

    def sort_elements(self, elements):
        new_elements = list(elements)
        new_elements.sort(key=lambda x: x.name)
        return new_elements

    def get_node_for_element(self, element):
        item = nodes.definition_list_item()
        term = nodes.term()
        term += nodes.Text(element.name)
        definition = nodes.definition()
        description = ViewList()
        for i, line in enumerate(prepare_docstring(element.description)):
            description.append(
                line,
                'description attribute of %s info element' % element.name,
                i)
        self.state.nested_parse(description, 0, definition)
        if element.default is not None:
            para = nodes.paragraph()
            definition += para
            para += nodes.Text("The default value is ")
            para += nodes.literal(element.default, element.default)
        item += term
        item += definition
        return item

    def build_definition_list(self, elements):
        node = nodes.definition_list()
        for element in self.sort_elements(elements):
            node += self.get_node_for_element(element)
        return node

    def run(self):
        elements = self.get_elements()
        required, not_required = self.split_required(elements)
        node = nodes.paragraph()
        node.document = self.state.document
        node += nodes.Text("The following elements are required, and must be provided if asked for to produce any packaging.")
        node += self.build_definition_list(required)
        node += nodes.Text("The following elements are optional, and do not have to be provided to produce packaging.")
        node += self.build_definition_list(not_required)
        return [node]


def setup(app):
    app.add_directive('pkgme_info_elements', PkgmeInfoElementsDirective)
