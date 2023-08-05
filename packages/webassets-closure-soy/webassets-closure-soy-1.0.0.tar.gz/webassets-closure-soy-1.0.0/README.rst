-----
Usage
-----

Easiest way to install:

    pip install closure-soy

    pip install webassets-closure-soy

You can set environment variables to use your own SoyToJsSrcCompiler.jar
but this package will look for the ``closure-soy`` package for easy setup.

In your assets.py file:

    from webassets_ext import ClosureSoyFilter

    from webassets.filter import register_filter

    register_filter(ClosureSoyFilter)

Then use filter="closure_soy" wherever you want to use it.
If you want to chain it with a js minifer, make sure that
closure_soy comes first in the list of filters.

----
Bugs
----

If you have any issues, please open a ticket at the
`Github page <https://github.com/Emsu/webassets-closure-soy>`_.
