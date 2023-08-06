Pygments Stylesheets Examples
-----------------------------

The `pygments` filter applies syntax highlighting to source code. For HTML and LaTeX, the default pygments output wraps the code with a class or macro, and a stylesheet needs to be applied to actually colorize the output.

You can use the `pygmentize` command line tool to list available styles::

    {{ d['pygments.sh|idio|shint']['list-styles'] | head(16) | indent(4) }}

to generate a CSS stylesheet for use with HTML::

    {{ d['pygments.sh|idio|shint']['generate-css'] | indent(4) }}

or to generate a .sty file for use with LaTeX::

    {{ d['pygments.sh|idio|shint']['generate-sty'] | indent(4) }}

The pygments filter also has some built-in ways to get stylesheets in your project.

Any blank file ending in `.css` or `.sty` passed through the `pyg` filter will have stylesheet contents generated if the final output extension of the file is also set to `.css` or `.sty`::

    {{ d['dexy.yaml|idio|t']['generate-css'] | indent(4) }}

Here is an excerpt from the generated stylesheet::

    {{ d['pastie.css|pyg'] | head(10) | indent(4) }}

Here is a LaTeX version::

    {{ d['dexy.yaml|idio|t']['generate-sty'] | indent(4) }}

Here is an excerpt from the generated `.sty` file::

    {{ d['pastie.sty|pyg'] | head(10) | indent(4) }}

You can also insert style definitions directly into the header of a document. Jinja has a `pygments` object which contains entries for each of the avaliable pygments styles, for html or latex.

Here is how to include css::

    {{ d['dexy.rst|idio|t']['pastie-css'] | indent(4) }}

{% if False -%}
.. @export "pastie-css"

{{ pygments['pastie.css'] }}

.. @end
{% endif -%}

Here is a list of the available stylesheets:

.. @export "list-stylesheets"

{% for k in sorted(pygments) -%}
- `{{ k }}`
{% endfor %}


.. @end

Which we obtained by iterating over the `pygments` object::

    {{ d['dexy.rst|idio|t']['list-stylesheets'] | indent(4) }}

