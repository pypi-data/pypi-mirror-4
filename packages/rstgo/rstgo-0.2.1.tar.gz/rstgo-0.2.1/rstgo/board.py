from __future__ import division

from itertools import cycle
import os

from PIL import Image, ImageDraw, ImageFont

FONTPATH = "/usr/share/fonts/truetype/freefont"

class TileSet(object):

    def __init__(self, name='tiny'):
        self.name = name
        self.tile_size = (14, 14)
        self.resource_dir = '%s/resources/%s' % (os.path.abspath(os.path.dirname(__file__)), name)
           
        self.tile_cache = {}
        self.valid_tiles = [
            'tl-corner', 'tr-corner', 'bl-corner', 'br-corner',
            't-side', 'b-side', 'l-side', 'r-side',
            'point', 'starpoint', 'empty',
            'black', 'white',
        ]

    def __getitem__(self, tile):
        if tile not in self.valid_tiles:
            raise KeyError
        if tile not in self.tile_cache:
            self.tile_cache[tile] = Image.open('%s/%s.png' % (self.resource_dir, tile))
        return self.tile_cache[tile]

    def annotate(self, tilename, annotation):
        if not annotation:
            annotation = ''

        if tilename == 'black':
            fgcolor = (255, 255, 255)
        else:
            fgcolor = (0, 0, 0)
        if annotation:
            annotated_tile_name = '-'.join([tilename, annotation])
        else:
            annotated_tile_name = tilename
        if annotated_tile_name not in self.tile_cache:
            tile_object = self.render_annotation(
                self[tilename].copy(),
                annotation, 
                fgcolor,
            )
            self.tile_cache[annotated_tile_name] = tile_object
        return self.tile_cache[annotated_tile_name]
      
    def render_annotation(self, stone, annotation, fgcolor):
        fontsize_mapping = {
            1: 11,
            2: 9,
            3: 8
        }

        fontsize = fontsize_mapping.get(len(annotation), 11)
        font = ImageFont.truetype(os.path.join(FONTPATH, 'FreeSans.ttf'), 
                                  fontsize)
        label = Image.new('RGBA', self.tile_size, (255,255,255,255))
        draw = ImageDraw.Draw(stone) 
        label_size = draw.textsize(annotation, font=font)
        offset = (
            (self.tile_size[0] - label_size[0]) // 2,
            (self.tile_size[1] - label_size[1]) // 2 + 1
        )
        draw.text(offset, annotation, fill=fgcolor, font=font)
        return stone

    def render(self, diagram):
        image = Image.new('RGBA', 
            (diagram.board.size[0] * self.tile_size[0], 
             diagram.board.size[1] * self.tile_size[1])
        )
        for x in xrange(diagram.board.size[0]):
            for y in xrange(diagram.board.size[1]):
                point = x, y
                if point in diagram.initial_black:
                    mark = 'black'
                elif point in diagram.initial_white:
                    mark = 'white'
                
                elif diagram.board.left_edge and x == 0:
                    if diagram.board.top_edge and y == 0:
                       mark = 'tl-corner'
                    elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                       mark = 'bl-corner'
                    else:
                       mark = 'l-side'
                elif diagram.board.right_edge and x == diagram.board.size[0] - 1:
                    if diagram.board.top_edge and y == 0:
                       mark = 'tr-corner'
                    elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                       mark = 'br-corner'
                    else:
                       mark = 'r-side'
                elif diagram.board.top_edge and y == 0:
                    mark='t-side'
                elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                    mark='b-side'
                elif (x, y) in diagram.board.star_points:
                    mark = 'starpoint'
                else:
                    mark = 'point'
                box = (x*self.tile_size[0], y*self.tile_size[1],
                       (x+1)*self.tile_size[0], (y+1)*self.tile_size[1])
                tile = self.annotate(mark, None)
                image.paste(tile, box)

        for x, y in diagram.marked_coordinates:
            box = (x*self.tile_size[0], y*self.tile_size[1],
                   (x+1)*self.tile_size[0], (y+1)*self.tile_size[1])
            mark = diagram.marked_coordinates[x, y]
            if mark[1]:
            	tile = self.annotate(mark[0], mark[1])
            else:
                tile = self.annotate(mark[0], None)
            image.paste(tile, box)
        return image


class Board(object):

    def __init__(self, size=(19, 19), left_edge=True, right_edge=True, top_edge=True, bottom_edge=True):
        self.size=size
        self.top_edge = top_edge
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.bottom_edge = bottom_edge
        self.set_star_points() 
        
    def set_star_points(self):
        x_ranks = set()
        y_ranks = set()
        if self.left_edge and not self.right_edge:
            if self.size[0] >= 4:
                x_ranks.add(3)
            if self.size[0] >= 10:
                x_ranks.add(9)
            if self.size[0] >= 16:
                x_ranks.add(15)

        elif self.right_edge and not self.left_edge:
            if self.size[0] >= 4:
                x_ranks.add(self.size[0] - 4)
            if self.size[0] >= 10:
                x_ranks.add(self.size[0] - 10)
            if self.size[0] >= 16:
                x_ranks.add(self.size[0] - 16)
            
        elif self.left_edge and self.right_edge:
            if self.size[0] >=9:
                x_ranks.add(3)
                x_ranks.add(self.size[0] - 4)
            if self.size[0] % 2 and self.size[0] >= 15:
                x_ranks.add((self.size[0] - 1) // 2)

        if self.top_edge and not self.bottom_edge:
            if self.size[1] >= 4:
                y_ranks.add(3)
            if self.size[1] >= 10:
                y_ranks.add(9)
            if self.size[1] >= 16:
                y_ranks.add(15)
 
        elif not self.top_edge and self.bottom_edge:
            if self.size[1] >= 4:
                y_ranks.add(self.size[1] - 4)
            if self.size[1] >= 10:
                y_ranks.add(self.size[1] - 10)
            if self.size[1] >= 16:
                y_ranks.add(self.size[1] - 16)

        elif self.top_edge and self.bottom_edge:
            if self.size[1] >=9:
                y_ranks.add(3)
                y_ranks.add(self.size[1] - 4)
            if self.size[1] % 2 and self.size[1] >= 15:
                y_ranks.add((self.size[1] - 1) // 2)
    
        self.star_points = set()
        for x in x_ranks:
            for y in y_ranks:
                self.star_points.add((x, y))


class GoDiagram(object):

    @classmethod
    def load_from_parser(cls, parser):
        board = Board(
            size=parser.board_size(),
            top_edge=parser.top_edge,
            left_edge=parser.left_edge,
            right_edge=parser.right_edge,
            bottom_edge=parser.bottom_edge,
        )
        return cls(board=board,
            initial_black=parser.initial_black,
            initial_white=parser.initial_white,
            marked_coordinates=parser.marked_coordinates,
            first_player=parser.first_player,
        )

    def __init__(self, board=Board(), initial_black=None, initial_white=None, marked_coordinates=None, first_player='black'):
        self.board = board
        self.initial_black = initial_black or set()
        self.initial_white = initial_white or set()
        self.marked_coordinates = marked_coordinates or {}
        self.first_player = first_player
        if self.first_player == 'black':
            self.second_player = 'white'
        elif self.first_player == 'white':
            self.second_player = 'black'
        else:
            self.first_player = 'black'
            self.second_player = 'white'
        self.tiles = TileSet('tiny')

    def render(self):
        self.image = self.tiles.render(self)

    def show(self):
        self.image.show()

    def save(self, filename, format):
        self.image.save(filename, format)
        
if __name__ == '__main__':
    black_set = set([(4, 4), (4, 5)])
    white_set = set([(3, 2), (7, 3), (8, 3)])
    marked_coordinates = {
        (2, 2): 1,
        (1, 2): 2,
        (2, 3): 3,
        (3, 1): 4,
    } 
    board = Board(
        (9, 9), 
    )
    board.star_points = set([(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)])
    sequence = []
    diagram = GoDiagram(board=board, 
            initial_black=black_set, 
            initial_white=white_set, 
            marked_coordinates=sequence)
    diagram.render()
    diagram.show()
