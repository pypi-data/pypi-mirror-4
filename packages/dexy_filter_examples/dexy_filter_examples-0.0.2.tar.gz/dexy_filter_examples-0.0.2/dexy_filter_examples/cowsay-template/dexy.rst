Cowsay Examples
---------------

The `cowsay` filter makes cows say things::

    {{ d['dexy.yaml|idio|t']['hello'] | indent(4) }}

    {{ str(d['hello.txt|cowsay']) | indent(4) }}

You can also pass command line options like `-b` for borg::

    {{ d['dexy.yaml|idio|t']['borg'] | indent(4) }}

    {{ str(d['borg.txt|cowsay']) | indent(4) }}

Or `-d` for dead::

    {{ d['dexy.yaml|idio|t']['dead'] | indent(4) }}

    {{ str(d['dead.txt|cowsay']) | indent(4) }}

Or use `-T` to set a custom setting for the tongue::

    {{ d['dexy.yaml|idio|t']['tongue'] | indent(4) }}

    {{ str(d['tongue.txt|cowsay']) | indent(4)  }}

And of course content be passed through other filters first::

    {{ str(d['youthful.txt']) | indent(4) }}

    {{ d['dexy.yaml|idio|t']['youthful'] | indent(4) }}

    {{ str(d['youthful.txt|jinja|cowsay']) | indent(4) }}
