.. _regetron: http://gitorious.org/regetron

The regetron_ filter runs text through regetron and compares it with regex files. You apply the regetron filter to a .regex file, and any files you specify as inputs provide the text that is evaluated against the regex.

Here is a regex::

    {{ d['example.regex'] | indent(4) }}

Here is a sample text file::

    {{ d['input1.txt'] | indent(4) }}

Here is the output from running this through regetron::

    {{ d['example.regex|regetron']['input1.txt'] | indent(4) }}

Here is another text file::

    {{ d['input2.txt'] | indent(4) }}

Here is the output from running this through regetron::

    {{ d['example.regex|regetron']['input2.txt'] | indent(4) }}

Here is how this is specified in the `dexy.yaml` file::

    {{ d['dexy.yaml|idio|t']['regetron'] | indent(4) }}
