htmlsections filter

Here is some HTML::

    {{ d['docs.html'] | indent(4) }}

Here is some HTML split into sections::

    {{ d['sections.html'] | indent(4) }}

Here is how we specify this::

    {{ d['dexy.yaml'] | indent(4) }}
