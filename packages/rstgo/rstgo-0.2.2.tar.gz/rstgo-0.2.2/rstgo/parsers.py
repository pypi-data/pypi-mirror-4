
class MalformedGoDiagram(ValueError): 
    pass

class GoDiagramParser(object):
    line_prefix = '$$'

    def __init__(self):
        self.top_edge = False
        self.left_edge = False
        self.right_edge = False
        self.bottom_edge = False
        self.board_width = 0
        self.board_height = 0
        self.initial_black = set()
        self.initial_white = set()
        self.sequence_moves = {}
        self.marked_coordinates = {}
        self.first_player = 'black'
        self.second_player = 'white'
        self._state = 'header'

    def board_size(self):
        return self.board_width, self.board_height

    def parse(self, board):
        for line in board:
            if self._state == 'header':
                self.parse_header(line)
            elif self._state == 'board':
                self.parse_board(line)
            elif self._state == 'footer':
                self.parse_footer(line)

    def parse_header(self, line):
        header_line = False
        line = line.strip()
        if line.startswith(self.line_prefix + 'W'):
            header_line = True
            self.first_player = 'white'
            self.second_player = 'black'
            prefix = self.line_prefix + 'W'
        elif line.startswith(self.line_prefix + 'B'):
            header_line = True
            self.first_player = 'black'
            self.second_player = 'white'
            prefix = self.line_prefix + 'B'
        elif line.startswith(self.line_prefix):
            prefix = self.line_prefix
        else:
            raise MalformedGoDiagram("All lines must start with $$")

        if '---' in line:
            header_line = True
            line = line[len(prefix):]
            line = line.strip()
            # top border:
            if any(c != '-' for c in line):
                raise MalformedGoDiagram('Top edge must consist of only "-" characters')
            self.top_edge=True
        if not header_line:
            self._state = 'board'
            self.parse_board(line)
                
    def parse_board(self, line):
        line = line.strip()
        if not line.startswith(self.line_prefix):
            raise MalformedGoDiagram("All lines must start with $$")
        line = line[len(self.line_prefix):]
        line = line.strip()
        if '---' in line:
            self._state == 'footer'
            self.parse_footer(line)
        else:
            self.board_height += 1
            if line[0] == '|':
                self.left_edge = True
                line = line[1:]
            if line[-1] == '|':
                self.right_edge = True
                line = line[:-1]
            points = line.split()
            if not self.board_width:
                self.board_width = len(points)
            elif self.board_width != len(points):
                raise MalformedGoDiagram("All lines must have the same number of points")
            for i, point in enumerate(points):
                coord = (i, self.board_height - 1)
                if point == 'X':
                    self.initial_black.add(coord)
        	    self.marked_coordinates[coord] = ('black', None)
                elif point == 'O':
                    self.initial_white.add(coord)
        	    self.marked_coordinates[coord] = ('white', None)
                elif all(c in list('1234567890') for c in point):
                    point = int(point)
                    if point == 0:
                        point = 10
                    self.sequence_moves[point] = coord
        	    if point % 2:
        	        player = self.first_player
        	    else:
        		player = self.second_player
        	    self.marked_coordinates[coord] = (player, str(point))
 
                elif point in list(u'abcdefghijklmnopqrstuvwxyz'):
		    # empty point annotations
		    self.marked_coordinates[coord] = (u'empty', point)
		elif point in list(u'BW#@YQZPCSTM'):
                    translations = {
                        'B': (u'black', u'O'),
                        'W': (u'white', u'O'), 
                        'C': (u'empty', u'O'), #MEDIUM SMALL WHITE CIRCLE, WHITE CIRCLE?
                        '#': (u'black', u'\N{BLACK MEDIUM SQUARE}'), 
                        '@': (u'white', u'\N{BLACK MEDIUM SQUARE}'),
                        'S': (u'empty', u'\N{BLACK MEDIUM SQUARE}'), # BLACK SQUARE
                        'Y': (u'black', u'\N{BLACK UP-POINTING TRIANGLE}'),
                        'Q': (u'white', u'\N{BLACK UP-POINTING TRIANGLE}'),
                        'T': (u'empty', u'\N{BLACK UP-POINTING TRIANGLE}'),
                        'Z': (u'black', u'X'),
                        'P': (u'white', u'X'),
                        'M': (u'white', u'X'),
                    }

		    # stone annotations
        	    self.marked_coordinates[coord] = translations[point]
                elif point in list('.,'):
                    #Empty point
                    pass
                else:
                    raise MalformedGoDiagram('Unrecognized board marking: "%s"' % point)
                    
    def parse_footer(self, line):
        if '---' in line:
            self.bottom_edge = True
            if any(c != '-' for c in line):
                raise MalformedGoDiagram('Bottom edge must consist of only "-" characters')
        else:
            #Not handling other footer information yet.
            pass

