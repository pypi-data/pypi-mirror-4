partpy
------

Parser Tools in Python (``partpy``, pronounced ``Par-Tee-Pie``), a
collection of tools for hand writing lexers and parsers in python.

There are many parser generators but there isn't much help for those
who wish to roll their own parser/lexer as counter-intuitive as that
may sound. ``partpy`` provides a solid base for hand written parsers
and lexers through a library of common tools.

By using ``partpy`` as the base for your own parser or lexer the hope
is to provide you with an environment where you can dive straight into
the language design, recognition and whatever else you need to do
without having to figure out how string matching should be done or
most of the error handling process.

Performance
===========

``partpy`` is written with ``Cython`` support through decorators and
can be compiled for extra speed. If you do not want to use ``Cython``
you can strip away the ``Cython`` decorators and imports and have no
more need for it.

Usage
=====

There are tutorials and information on how to use ``partpy`` at
http://github.com/Nekroze/partpy/wiki and the main GitHub repository
contains an examples directory that are tested for correctness each
release so they will always be up to date. Also many examples for
how each feature is used can be seen in the test directory at github
and also shows the expected output of each test.


Feedback
========
If you have any suggestions or questions about ``partpy`` feel free
to email me at nekroze@eturnilnetwork.com.

You can check out more of what I am doing at
http://nekroze.eturnilnetwork.com my blog.

If you encounter any errors or problems with ``partpy``, please let me
know! Open an Issue at the GitHub http://github.com/Nekroze/partpy
main repository.

Thanks!
