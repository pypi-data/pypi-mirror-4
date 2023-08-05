pysixel
=======

Provides Japanese Input Method SKK (Simple Kana to Kanji conversion) on your terminal.

Install
-------

via github ::

    $ git clone https://github.com/saitoha/PySixel.git
    $ cd pysixel 
    $ python setup.py install

or via pip ::

    $ pip install PySixel 


Usage
-----

Command line tool::

    $ sixelconv [options] filename

or ::

    $ cat filename | sixelconv [options]


* Options::

    -h, --help                  show this help message and exit
    --version                   show version
    -t TERM, --term=TERM        override TERM environment variable
    -l LANG, --lang=LANG        override LANG environment variable
    -o ENC, --outenc=ENC        set output encoding

Code Example
------------

:: python

    import sixel
    writer = sixel.SixelWriter()
    writer.draw('test.png') 

Dependency
----------
 - Python Imaging Library (PIL)
   http://www.pythonware.com/products/pil/ 

Reference
---------
 - Chris_F_Chiesa, 1990 : All About SIXELs
   ftp://ftp.cs.utk.edu/pub/shuford/terminal/all_about_sixels.txt

 - vt100.net
   http://vt100.net/

