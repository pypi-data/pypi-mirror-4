ABC is a music notation::

    {{ d['jingle.abc'] | indent(4) }}

The abc filter converts this to one of the available output formats, using the abcm2ps utility which must be installed on your system. By default it will convert to SVG::

    {{ d['dexy.yaml|idio|t']['jingle'] | indent(4) }}

Here is some of the SVG generated::

    {{ d['jingle.abc|abc'] | head(10) | indent(4) }}

To get EPS or another type of output, set the desired file extension::

    {{ d['dexy.yaml|idio|t']['jingle-eps'] | indent(4) }}

Here is some of the EPS generated::

    {{ d['jingle.abc|abc|-'] | head(10) | indent(4) }}

For HTML you can also use the shortcut `h` filter which forces the previous filter to output HTML. Here we also set some custom command line arguments which get passed to abcm2ps::

    {{ d['dexy.yaml|idio|t']['jingle-html'] | indent(4) }}

Here is some of the HTML generated::

    {{ d['jingle.abc|abc|h'] | head(10) | indent(4) }}
