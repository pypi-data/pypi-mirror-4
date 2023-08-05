==============================
Wempy and Wemplates for Python
==============================

Wempy is a command line tool for parsing embedded python (similar to Ruby's
erb). Wempy's syntax is pure python with 3 very important differences:

    1.  There is no need for indentation

    2.  The python keyword 'pass' must be used to indicate the end of some
        satements, blocks, and loops (like if/else, Try/Except, for or while )
        depending on context

    3.  'extend' and 'include' are special keywords used to make templates (which can inherit)

Example
=======

::

    % wempy <<-EOF

    {{first_name = 'Tyler'}}

    {{last_name = 'Durden'}}

    Hello Mr. {{=last_name}} or shall I call you {{=first_name}} instead?

    EOF

This generates the following output:

::

    Hello Mr.  Durden  or shall I call you  Tyler  instead?

You can see the python script that is generated & executed by using the -x flag. 

::

    % wempy -x <<-EOF

    {{first_name = 'Tyler'}}

    {{last_name = 'Durden'}}

    Hello Mr. {{=last_name}} or shall I call you {{=first_name}} instead?

    EOF

Which prints out:

::

    import sys

    sys.stdout.write('    ')

    first_name = 'Tyler'
    
    sys.stdout.write('\n    ')

    last_name = 'Durden'

    sys.stdout.write('\n    Hello Mr. ')

    sys.stdout.write(last_name)

    sys.stdout.write(' or shall I call you ')

    sys.stdout.write(first_name)

    sys.stdout.write(' instead?\n')

wempy.py shows how to use the wemplate library. But here's a quick rundown:

::

    >> import wemplate.wemplate

    >> text="Hello {{=planet}} !"

    >> parser = wemplate.wemplate.TemplateParser(text)

    >>

    >> print parser.render(planet="World")       #print the rendered template

    'Hello World !'

Origin
======

Wempy is taken directly from Web2py's template engine.  We've removed some
things like the gluon integration wrapper functions, the response object, and
HTML/XML escaping. 

The name stands for (W)eb2py's (Em)bedded (Py)thon

Documentation
=============

There isn't any for wempy (yet). To understand the caveats of the engine take
a look at the `Views Basic Syntax <http://web2py.com/books/default/chapter/29/5#Basic-syntax>`_
section of the `web2py manual <http://web2py.com/books/>`_

I'll be working on Wempy specific documentation shortly

License
=======

As Web2py is licensed under the LGPL v3 so too is Wempy

Home
====

More information will soon be available at http://www.wempy.org
