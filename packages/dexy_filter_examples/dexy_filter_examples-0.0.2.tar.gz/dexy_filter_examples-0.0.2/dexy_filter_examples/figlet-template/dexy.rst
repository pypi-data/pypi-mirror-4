Figlet Example
==============

Here is the result of running the text `{{ d['figlet.txt'].strip() }}` through the figlet filter::

    {{ d['figlet.txt|figlet'] | indent(4) }}

The config is::
    
    {{ d['dexy.yaml|idio|t']['figlet'] | indent(4) }}

