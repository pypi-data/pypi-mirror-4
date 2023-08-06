"""
Simple static page generator.
Uses jinja2 to compile templates.
Templates should live inside `./templates` and will be compiled in '.'.
"""
import inspect
import os
import re

from jinja2 import Environment, FileSystemLoader


class Renderer(object):
    def __init__(self, env, outpath,
                 contexts=None, rules=None, encoding="utf8"):
        """
        -   contexts should be a list of regex-function pairs where the
            function should return a context for that template and the regex,
            if matched against a filename, will cause the context to be used.
        -   rules are used to override template compilation. The value of rules
            should be a list of `regex`-`function` pairs where `function` takes
            a jinja2 Environment, the filename, and the context and renders the
            template, and `regex` is a regex that if matched against a filename
            will cause `function` to be used instead of the default.
        """
        self.env = env
        self.outpath = outpath

        self.encoding = encoding
        self.contexts = contexts
        self.rules = rules

    @property
    def template_names(self):
        return self.env.list_templates(filter_func=self.filter_func)

    def get_template(self, template_name):
        return self.env.get_template(template_name)

    def filter_func(self, filename):
        """Check if the file should be rendered.
        -   Hidden files will not be rendered.
        -   Files prefixed with an underscore are assumed to be partials and
            will not be rendered.
        """
        _, tail = os.path.split(filename)
        return not (tail.startswith('_') or tail.startswith("."))

    def render_template(self, template_name, **kwargs):
        """Compile a template.
        -   template should be the name of the template as it appears inside
            of `./templates`.
        -   kwargs should be a series of key-value pairs. These items will be
            passed to the template to be used as needed.
        """
        template = self.get_template(template_name)
        for regex, func in self.rules:
            if re.match(regex, template_name):
                func(self.env, template, **kwargs)
                break
        else:
            head, tail = os.path.split(template.name)
            if head:
                head = os.path.join(self.outpath, head)
                if not os.path.exists(head):
                    os.makedirs(head)
            x = os.path.join(self.outpath, template.name)
            template.stream(**kwargs).dump(x, self.encoding)

    def get_context(self, template_name):
        template = self.get_template(template_name)
        for regex, context_generator in self.contexts:
            if re.match(regex, template_name):
                try:
                    context = context_generator(template)
                except TypeError:
                    context = context_generator()
                break
        else:
            context = {}
        return context

    def render_templates(self):
        """Render each template inside of `env`.
        """
        for template_name in self.template_names:
            print "rendering %s..." % template_name
            context = self.get_context(template_name)
            self.render_template(template_name, **context)


def main(searchpath="templates", outpath=".", filter_func=None, contexts=None,
         extensions=None, rules=None, autoreload=True, encoding="utf8"):
    """
    Render each of the templates and then recompile on any changes.
    -   searchpath should be the directory that contains the template.
        Defaults to "templates"
    -   filter_func should be a function that takes a filename and returns
        a boolean indicating whether or not a template should be rendered.
        Defaults to ignore any files with '.' or '_' prefixes.
    -   contexts should be a map of template names to functions where each
        function should return a context for that template.
    -   extensions should be any extensions to add to the Environment.
    -   autoreload should be a boolean indicating whether or not to
        automatically recompile templates. Defaults to true.
    """
    if extensions is None:
        extensions = []

    calling_module = inspect.getmodule(inspect.stack()[-1][0])
    # Absolute path to project
    project_path = os.path.realpath(os.path.dirname(calling_module.__file__))
    # Absolute path to templates
    template_path = os.path.join(project_path, searchpath)

    loader = FileSystemLoader(searchpath=searchpath, encoding=encoding)
    env = Environment(loader=loader, extensions=extensions)

    def render_all():
        render_templates(env, outpath, contexts, filter_func=filter_func,
                         rules=rules, encoding=encoding)
        print "Templates built."
    render_all()

    if autoreload:
        import easywatch
        print "Watching '%s' for changes..." % searchpath
        print "Press Ctrl+C to stop."

        def handler(event_type, src_path):
            if event_type == "modified":
                if src_path.startswith(template_path):
                    render_all()
        easywatch.watch("./" + searchpath, handler)

        print "Process killed"
    return 0
