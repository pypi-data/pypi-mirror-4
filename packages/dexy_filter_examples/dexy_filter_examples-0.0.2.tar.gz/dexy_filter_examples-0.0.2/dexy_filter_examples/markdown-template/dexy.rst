Markdown Example
================

The markdown filter converts markdown, like this::

    {{ d['example.md'] | indent(4) }}

into HTML, like this::

    {{ d['example.md|markdown'] | indent(4) }}

Here is how this is specified in YAML::

    {{ d['dexy.yaml|idio|t']['markdown'] | indent(4) }}

Markdown & Jinja
================

If you are running a document through both the markdown and jinja filters, then put jinja earlier in the filter chain, before markdown, so that markdown doesn't mangle the jinja tags. This will mean that markdown will run on the content returned by jinja during its processing. For example::

    {{ d['dexy.yaml|idio|t']['example-with-jinja'] | indent(4) }}

If your jinja content is returning already-formatted HTML, then markdown will leave this alone as long as there are no blank lines within your content. Dexy's pyg and idio filters have the `lineanchors` feature enabled by default which, in addition to giving each line of output a linkable URL, also means there are no blank lines in the pygments output, so the markdown filter should not cause problems as long as this feature is kept enabled.

Here is an example of a markdown document with jinja tags::

    {{ d['example-with-jinja.md'] | indent(4) }}

Here is the HTML after this has been processed by both jinja and markdown::

    {{ d['example-with-jinja.md|jinja|markdown'] | indent(4) }}

Markdown Extensions
===================

.. _python-markdown: http://freewisdom.org/projects/python-markdown/Available_Extensions
.. _Table of Contents: http://freewisdom.org/projects/python-markdown/Table_of_Contents

The python-markdown_ implementation has a number of extensions which, when enabled, make available additional markdown features. By default the `Table of Contents`_ extension is enabled (with no custom configuration options set).

To enable an extension, you need to pass a dictionary of arguments to the `markdown` filter. For each extension you wish to enable, you need to pass that extension's module name as the key, and a dictionary setting any custom configuration options for that extension as the value (this must be a blank dictionary if you don't wish to set any custom options).

Here is a markdown document containing a table::

    {{ d['table-example.md'] | indent(4) }}

Without any extensions enabled, this doesn't render specially::

    {{ d['table-example.md|markdown|-no-tables'] | indent(4) }}

However when we enable `tables` like this::

    {{ d['dexy.yaml|idio|t']['table-example-enabled'] | indent(4) }}

Then we get a HTML table in our output::

    {{ d['table-example.md|markdown'] | indent(4) }}

If we set a custom option, then the TOC module is no longer automatically enabled. Here is an example of enabling the tables and toc modules, and setting a custom option to the toc module::

    {{ d['dexy.yaml|idio|t']['table-and-custom-toc-options'] | indent(4) }}

Here is the HTML we generate::

    {{ d['table-and-toc-example.md|markdown'] | indent(4) }}
