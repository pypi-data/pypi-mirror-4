from __future__ import division, absolute_import
import os.path
import posixpath
import tempfile

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.images import Image as ImageDirective

from . import parsers, board

class godiagram_node(nodes.General, nodes.Element):
    pass

class GoDiagramDirective(ImageDirective):

    """Renders a go diagram.  This will take an ascii go diagram and return
    an image node which points to the new image
   
    Looks like:
  
    ..go:: filename.png

        $$ -----------
        $$ | . . . . .
        $$ | . . O . .
        $$ | . X O . .
        $$ | . X X . .
        $$ | . . . . .

    It will only render png images.
    """
    
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    option_spec = {
        'alt': directives.unchanged,
    }

    def run(self):
        """Do it."""

        self.assert_has_content()
        node = godiagram_node()
        node['content'] = self.content
        node['alt'] = self.options.get('alt', '')
        if self.arguments:
            node['filename'] = self.arguments[0] 
        else:
            node['filename'] = None
        return [node]

def render_godiagram(self, node, imgbase='.', outbase='.'):

    outfile = node['filename']
    if outfile and outbase:
        imgpath = posixpath.join(imgbase, outfile)
        outpath = os.path.join(outbase, outfile)
        outdir = os.path.dirname(outpath)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
    else:
        imgpath = None
        outpath = tempfile.TemporaryFile()

    parser = parsers.GoDiagramParser()
    parser.parse(node['content'])
    diagram = board.GoDiagram.load_from_parser(parser)
    diagram.render()
    diagram.save(outpath, 'PNG')
    return imgpath, outpath 

def render_godiagram_html(self, node, imgbase, outbase):
    imgpath, outpath = render_godiagram(self, node, imgbase, outbase)
    self.body.append(self.starttag(node, 'p', CLASS='godiagram'))
  
    if not imgpath:
        try:
            outpath.seek(0)
            imgpath = 'data:image/png;base64,%s' % outpath.read().encode('base64').replace('\n', '')
        finally:
            outpath.close()
    self.body.append('<img src="%s" alt="%s"/>\n' % (imgpath, node['alt']))
    self.body.append('</p>')


# HTML Visitor for godiagram_nodes
def html_visit_godiagram_node(self, node):
    if hasattr(self, 'builder'):
        # Sphinx
        imgbase = getattr(self.builder, 'imgpath')
        outbase = os.path.join(getattr(self.builder, 'outdir'), '_images')
    elif False:
        # Figure out how to do this for Pelican
        pass
    else:
        # Otherwise, fall back to 
        imgbase = None
        outbase = None
    render_godiagram_html(self, node, imgbase, outbase)

def setup(app):
    """setup method to allow sphinx to render go diagrams"""
    app.add_node(godiagram_node,
        html=(html_visit_godiagram_node, lambda self, node: None),
    )
    app.add_directive('go', GoDiagramDirective)

def setup_docutils():
    directives.register_directive('go', GoDiagramDirective)
    from docutils.writers.html4css1 import HTMLTranslator
    setattr(HTMLTranslator, 'visit_godiagram_node', html_visit_godiagram_node)
    setattr(HTMLTranslator, 'depart_godiagram_node', lambda self, node: None)

def setup_pelican():
    import warnings
    warnings.warn(
        "setup_pelican() is deprecated. Use setup_docutils() instead",
        DeprecationWarning
    )
    return setup_docutils()
