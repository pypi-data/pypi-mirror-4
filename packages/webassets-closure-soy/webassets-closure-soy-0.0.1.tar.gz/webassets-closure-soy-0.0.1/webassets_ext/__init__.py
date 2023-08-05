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

from webassets.filter import Filter, JavaMixin


__all__ = ('ClosureSoyFilter',)


class ClosureSoyFilter(Filter, JavaMixin):

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

    def output(self, _in, out, **kw):

        args = ["--outputFormat", out.name]

        if self.extra_args:
            args.extend(self.extra_args)
        self.java_run(_in, out, args)
