######
README
######

rstgo is a package for parsing go diagrams of the style used at the 
`Sensei's Library`_ and rendering them using reStructuredText.  It was 
designed for embedding dynamically generated images of go games into reST 
documents, particularly for pelican blogs or sphinx documentation.  

The code lives at http://bitbucket.org/cliff/rstgo.  Bug reports, feature
requests, and contributions are all welcome.  If you find the code useful,
hop on bitbucket and send me a quick message letting me know.

To use with sphinx, add 'rstgo.rst' to your list of extensions.  

To use with pelican or another docutils-based system, add the following to 
your pelican configuration file::

    from rstgo import rst
    rst.setup_docutils()
    
To use rstgo in standalone rst files, you can use the included
``rst2html+go.py`` script, which should get installed onto your PATH.

You can even use rstgo programmatically with go diagrams outside of 
reStructuredText documents.  Just pass a file-like object containing only 
the text of the diagram to a GoDiagramParser, and then render the image file
using a GoDiagram::

    from StringIO import StringIO
    from rstgo import parsers
    from rstgo import board

    diagram_text = StringIO("""\
        $$ -------
        $$ |. 1 .|
        $$ |X . O|
        $$ |b a 2|
        $$ -------
    """)
    parser = parsers.GoDiagramParser()
    parser.parse(diagram_text)
    diagram = board.GoDiagram.load_from_parser(parser)
    diagram.render()
    diagram.show() 
    diagram.save('diagram.png', 'PNG')


Changelog
=========

0.2.1 -- 2012/11/29
-------------------

* Fixed bug causing misrendering of basic stones in certain circumstances
* Fixed example code in this README file

0.2.0 -- 2011/12/04
-------------------

* Implemented parsing of multi-digit numbers--not supported by sensei's 
  library.
* Renamed ``setup_pelican()`` to ``setup_docutils()``, because that's what it does.
* Deprecated ``setup_pelican()``.
* Parser now creates a ``marked_coordinates`` dict, which allows multiple
  instances of the same annotation.
* Boards now render non-alphanumeric annotations.
* Added ``rstgo.__version__`` information.

0.1.7 -- 2011/11/06
-------------------

* Fixed an error in refactored parser that caused the first line of the board
  to be processed twice.
* Added documentation for rendering diagrams in plain python.
* Renamed ``GoDiagram.load_diagram_from_parser()`` method to 
  ``GoDiagram.load_from_parser()``
* Implemented rendering of 0 as a stone marked "10".

0.1.6 -- 2011/11/05
-------------------
* Sequence moves can now start with either black or white.  
* Refactored parser a little bit.  

0.1.5 -- 2011/11/05
-------------------

Implemented rendering of sequence moves and letter annotations.  Currently,
sequence moves have to start with black


0.1.4 -- 2011/11/04
-------------------

Fixed a bug where ``:alt:`` argument was unintentionally required.


0.1.3 -- 2011/11/03
-------------------

Fixed pathing and extension loading for usage with Sphinx.


0.1.2 -- 2011/10/27
-------------------

Added release notes to ``README.txt``


0.1.1 -- 2011/10/27
-------------------

Added intro text to ``README.txt`` 


0.1.0 -- 2011/10/27
-------------------

Initial release


To Do
=====

* Diagrams should render captions and metadata.

.. _Sensei's Library: http://senseis.xmp.net/?HowDiagramsWork
