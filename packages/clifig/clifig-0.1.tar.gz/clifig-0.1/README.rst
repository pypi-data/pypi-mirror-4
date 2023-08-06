clifig
======
Clifig provides a very simple CLI for modifying config files.

Usage
=====
Clifig can be accessed directly from the terminal

.. code:: Bash

 $ clifig path/to/config/file.conf
 (file.conf)

of from a Python script

.. code:: Python

 >>> from clifig import Clifig
 >>> Clifig.run('path/to/config/file.conf')
 (file.conf) 

Commands
========
**show [SECTION [OPTION]]**
   Show the values for the provided section or option
**add SECTION**
   Add a new section to the config
**set SECTION OPTION VALUE**
   Set a value
**del SECTION [OPTION]**
   Delete a section or specific option
**abort**
   Abort all changes
**exit or Ctrl+D**
   Safely exit and save all changes

Notes
=====
I made this for another project and thought some people may find it useful.
It was primarily an exercise to learn about Python styling, packaging,
distribution, and open source licenses, but I do intend to maintain it.


License
=======
Copyright (C) 2013 Andrew Guenther

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
