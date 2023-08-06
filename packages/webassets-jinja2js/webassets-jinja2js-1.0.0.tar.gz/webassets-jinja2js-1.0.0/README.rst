-----
Usage
-----

Easiest way to install:

    pip install pwt.jinja2js

    pip install webassets-jinja2js

In your assets.py file:

    from webassets_ext import JinjaToJSFilter

    from webassets.filter import register_filter

    register_filter(JinjaToJSFilter)

Then use filter="jinja2js" wherever you want to use it.
If you want to chain it with a js minifer, make sure that
jinja2js comes first in the list of filters.

----
Bugs
----

If you have any issues, please open a ticket at the
`Github page <https://github.com/Emsu/webassets-jinja2js>`_.
