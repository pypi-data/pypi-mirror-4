from distutils.spawn import find_executable
import subprocess
from os import path
import tempfile

from webassets.exceptions import FilterError
from webassets.filter.jst import JSTemplateFilter


__all__ = ('JinjaToJSFilter',)


class JinjaToJSFilter(JSTemplateFilter):
    """Compile `Jinja <http://jinja.pocoo.org/docs/>`_ templates.

    This filter assumes that the ``jinja2s`` executable is in the path.

    .. note::
        Use this filter if you want to compile Jinja templates.

    .. warning::
        Currently, this filter is not compatible with input filters. Any
        filters that would run during the input-stage will simply be
        ignored. Input filters tend to be other compiler-style filters,
        so this is unlikely to be an issue.
    """

    name = 'jinja2js'
    options = {
        'extra_args': 'JINJA2JS_EXTRA_ARGS',
        'root': 'JINJA2JS_ROOT',
    }
    max_debug_level = None

    def process_templates(self, out,  hunks, **kw):

        if not find_executable("jinja2js"):
            raise EnvironmentError(
                    "The jinja2js executable can't be found."
                    "\nPlease pip install pwt.jinja2js")

        templates = [info['source_path'] for _, info in hunks]

        temp = tempfile.NamedTemporaryFile(dir='.', delete=True)
        args = ['jinja2js', '--outputPathFormat', temp.name]
        args.extend(templates)
        if self.extra_args:
            args.extend(self.extra_args)

        proc = subprocess.Popen(
            args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            raise FilterError(('handlebars: subprocess had error: stderr=%s, '+
                               'stdout=%s, returncode=%s') % (
                                    stderr, stdout, proc.returncode))
        out.write(open(temp.name).read())
