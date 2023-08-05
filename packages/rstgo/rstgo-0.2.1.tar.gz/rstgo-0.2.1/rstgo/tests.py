try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from unittest2 import TestCase

from rstgo.board import Board
from rstgo.parsers import GoDiagramParser

class ParserTestCase(TestCase):

    def test_parsing_full_empty_board(self):
        board = StringIO("""\
            $$  ------------------------------------- 
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$ |. . . . . . . . . . . . . . . . . . .|
            $$  -------------------------------------  """
        )
        parser = GoDiagramParser()
        parser.parse(board)
        self.assertEqual(parser.board_size(), (19, 19))
        self.assertEqual(parser.initial_black, set())
        self.assertEqual(parser.initial_white, set())
        self.assertEqual(parser.top_edge, True)
        self.assertEqual(parser.left_edge, True)
        self.assertEqual(parser.right_edge, True)
        self.assertEqual(parser.bottom_edge, True)
 
    def test_parsing_empty_small_full_board(self):
        board = StringIO("""\
            $$  ----------------- 
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$ |. . . . . . . . .|
            $$  ----------------- """
        )
        parser = GoDiagramParser()
        parser.parse(board)
        self.assertEqual(parser.board_size(), (9, 9))
        self.assertEqual(parser.initial_black, set())
        self.assertEqual(parser.initial_white, set())
        self.assertEqual(parser.top_edge, True)
        self.assertEqual(parser.left_edge, True)
        self.assertEqual(parser.right_edge, True)
        self.assertEqual(parser.bottom_edge, True)

    def test_parsing_partial_board(self):
        board = StringIO("""\
            $$ ----------------- 
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|
            $$ . . . . . . . . .|"""
        )
        parser = GoDiagramParser()
        parser.parse(board)
        self.assertEqual(parser.top_edge, True)
        self.assertEqual(parser.left_edge, False)
        self.assertEqual(parser.right_edge, True)
        self.assertEqual(parser.bottom_edge, False)

    def test_parsing_partial_board_with_stones(self):
        board = StringIO("""\
            $$  ----------------- 
            $$ |. . . . . . . . . 
            $$ |. . . . . . . . . 
            $$ |. X . . . . . . . 
            $$ |. O . . . . . . . 
            $$ |. . . . . . . . . 
            $$ |. . . . . . . . . 
            $$ |. . . . . . . . . 
            $$ |. . . . . . . . . 
            $$ |. . . . . . . . . """
        )
        
        parser = GoDiagramParser()
        parser.parse(board)
        self.assertEqual(len(parser.initial_black), 1)
        self.assertIn((1, 2), parser.initial_black)
        self.assertIn((1, 3), parser.initial_white)


class StarpointTestCase(TestCase):
    def test_standard_star_points(self):
        board = Board()
        standard_points=set([(3, 3), (3, 9), (3, 15),
                      (9, 3), (9, 9), (9, 15),
                      (15, 3), (15, 9), (15, 15)])
        self.assertEqual(standard_points, board.star_points)

    def test_no_middle_points_on_even_sizes(self):
        board = Board((18, 19))
        self.assertEqual(len(board.star_points), 6)
        board = Board((18, 18))
        self.assertEqual(len(board.star_points), 4)

    def test_no_middle_points_below_fifteen_rows(self):
        board = Board((15, 15))
        self.assertEqual(len(board.star_points), 9)
        board = Board((13, 13))
        self.assertEqual(len(board.star_points), 4)

    def test_no_points_below_nine_rows(self):
        board = Board((9, 9))
        self.assertEqual(len(board.star_points), 4)
        board = Board((8, 8))
        self.assertEqual(len(board.star_points), 0)


class AnnotationsTestCase(TestCase):
    def setUp(self):
        self.board = StringIO("""\
            $$  1 b
            $$  a 2""")
        self.parser = GoDiagramParser()
        self.parser.parse(self.board)

    def test_sequence_moves_are_parsed(self):
        self.assertEqual(len(self.parser.sequence_moves), 2)
        self.assertEqual(self.parser.sequence_moves[1], (0,0))
        self.assertEqual(self.parser.sequence_moves[2], (1,1))

    def test_annotated_points_are_parsed(self):
        self.assertEqual(len(self.parser.annotated_points), 2)
        self.assertEqual(self.parser.annotated_points['a'], (0,1))
        self.assertEqual(self.parser.annotated_points['b'], (1,0))

