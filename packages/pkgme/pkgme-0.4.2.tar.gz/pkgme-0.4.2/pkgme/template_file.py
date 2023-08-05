import pkg_resources

from Cheetah.Template import Template


class TemplateFile(object):

    def __init__(self, name):
        self.name = name

    def render(self, data):
        t = Template(
            file=pkg_resources.resource_stream(
                __name__, "templates/%s" % self.name),
            searchList=[data])
        return str(t)
