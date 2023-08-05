"""Client Side Templating with `Google Closure Templates
<https://code.google.com/p/closure-templates/>`_.

Google Closure Templates is an external tool written in Java, which needs
to be available. One way to get it is to install the
`closure-soy <http://pypi.python.org/pypi/closure-soy>`_ package::

    pip install closure-soy

No configuration is necessary in this case.

You can also define a ``CLOSURE_TEMPLATES_PATH`` setting that
points to the ``.jar`` file. Otherwise, an environment variable by
the same name is tried. The filter will also look for a ``JAVA_HOME``
environment variable to run the ``.jar`` file, or will otherwise
assume that ``java`` is on the system path.

Supported configuration options:

CLOSURE_EXTRA_ARGS
    A list of further options to be passed to the Closure compiler.
    There are a lot of them.

    For options which take values you want to use two items in the list::

        ['--inputPrefix', 'prefix']
"""

from __future__ import absolute_import
import os
import subprocess
import tempfile

from webassets.filter import Filter


__all__ = ('ClosureSoyFilter',)


class ClosureSoyFilter(Filter):
    """Filter to take in multiple .soy files and output a compiled javascript template

    Note: This doesn't use the JavaMixin from the webassets package because the
    soy compiler doesn't take input streams. It only takes paths.
    """

    name = 'closure_soy'
    options = {
        'extra_args': 'CLOSURE_EXTRA_ARGS',
    }

    def setup(self):
        super(ClosureSoyFilter, self).setup()

        try:
            self.jar = self.get_config('CLOSURE_TEMPLATES_PATH',
                                       what='Google Closure Soy Templates Compiler')
        except EnvironmentError:
            try:
                import closure_soy
                self.jar = closure_soy.get_jar_filename()
            except ImportError:
                raise EnvironmentError(
                    "\nClosure Templates jar can't be found."
                    "\nPlease either install the closure package:"
                    "\n\n    pip install closure-soy\n"
                    "\nor provide a CLOSURE_TEMPLATES_PATH setting "
                    "or an environment variable with the full path to "
                    "the Closure compiler jar."
                )
        self.java_setup()

    def input(self, _in, out, source_path, output_path, **kw):
        # Awkward but this is the only way I can find to pass source_paths to the output method
        # TODO: improve the way we pass the source_paths to the output
        out.write(source_path + " ")

    def output(self, _in, out, **kw):
        source_paths = _in.read().split(" ")
        # removes extra spaces and newlines characters
        source_paths = [path.replace("\n", "") for path in source_paths if path]

        # Create a temporary file because soy compiler needs an output path
        # And we want to write the output to the 'out' file so filters can be chained
        temp = tempfile.NamedTemporaryFile(dir='.', delete=True)

        args = ["--outputPathFormat", temp.name]
        args.extend(source_paths)

        if self.extra_args:
            args.extend(self.extra_args)
        self.java_run(args)

        out.write(open(temp.name).read())

    def java_setup(self):
        # We can reasonably expect that java is just on the path, so
        # don't require it, but hope for the best.
        path = self.get_config(env='JAVA_HOME', require=False)
        if path is not None:
            self.java = os.path.join(path, 'bin/java')
        else:
            self.java = 'java'

    def java_run(self, args):
        proc = subprocess.Popen(
            [self.java, '-jar', self.jar] + args,
            # we cannot use the in/out streams directly, as they might be
            # StringIO objects (which are not supported by subprocess)
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            raise FilterError('%s: subprocess returned a '
                'non-success result code: %s, stdout=%s, stderr=%s' % (
                     self.name, proc.returncode, stdout, stderr))
