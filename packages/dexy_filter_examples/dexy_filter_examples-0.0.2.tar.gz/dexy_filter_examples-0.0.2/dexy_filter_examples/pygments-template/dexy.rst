Pygments Examples
-----------------

The `pygments` filter applies syntax highlighting to source code.

Here is some raw source code::

    {{ d['hello.py'] | indent(4) }}

And here is how we specify in `dexy.yaml` that the `pyg` filter should be applied to this file::

    {{ d['dexy.yaml|idio|t']['pygments'] | indent(4) }}

The default format is HTML, so the code will come out looking like this, with HTML markup applied::

    {{ d['hello.py|pyg'] | indent(4) }}

If we follow the `pyg` filter with the `l` filter (which does nothing, but it only accepts input of documents with `.tex` extension)::

    {{ d['dexy.yaml|idio|t']['latex'] | indent(4) }}

then pygments will output LaTeX markup instead::

    {{ d['hello.py|pyg|l'] | indent(4) }}

Pygments will automatically determine which lexer to use based on the file extension of the incoming file. In the above examples, the `.py` file extension tells pygments that it should use the python lexer. If you need a different lexer than the default for the file extension, then you can pass a custom `lexer` argument::

    {{ d['dexy.yaml|idio|t']['custom-lexer'] | indent(4) }}

You can see a list of all the available lexers, the file extensions they correspond to, and the aliases you can use to specify them, as follows::

    {{ d['pygments.sh|idio|shint']['list-lexers'] | head(16) | indent(4) }}

Dexy adds some custom file extension -> lexer mappings of its own, such as `.pycon` and `.rbcon` for python console and ruby console transcripts.

.. _Pygments Documentation: http://pygments.org/docs/formatters/#formatter-classes

Custom formatter options can also be passed. Note that these options may be different for the HTMLFormatter and, say, the LatexFormatter. For information consult the `Pygments Documentation`_ for the formatter you are using. Here is an example of setting the `noclasses` attribute to True::

    {{ d['dexy.yaml|idio|t']['html-noclasses'] | indent(4) }}

And here is the resulting HTML::

    {{ d['hello.py|pyg|-noclasses'] | indent(4) }}

As a reminder here is the default HTML again::

    {{ d['hello.py|pyg'] | indent(4) }}

