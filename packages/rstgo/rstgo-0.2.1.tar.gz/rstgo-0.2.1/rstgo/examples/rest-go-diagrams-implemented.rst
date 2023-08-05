############################
reST Go Diagrams Implemented
############################


This is the result of my recent game against enzondio on 
http://dragongoserver.net.  I lost.

.. go:: 
    :alt: A basic go diagram.

    $$ ---------------------------------------
    $$ |O O O . X O O X X O O . . . . . . . .|
    $$ |X X O O O O X X X X O . . O . . . . .|
    $$ |X . X O X X X O . X O . O . O O . . .|
    $$ |. X X O O O O X X . X O O O X X O . .|
    $$ |X . X O . O X X . X X X X X X O O O .|
    $$ |. X O O O O O X . X . O O . X X X O .|
    $$ |. X O . . O X X X X O O X X X O O . .|
    $$ |. X O O . O O O X O X X X O O O . O O|
    $$ |. . X O O X X O X . . . O X X O O X X| 
    $$ |. . X O O X O O X O . . X X . X X X .|
    $$ |. O X X O X O O X . X . X . . . . X X|
    $$ |. X . . X X X X . X X X . X X X X O X|
    $$ |. X . X . X . X X O X O X X X . O . O|
    $$ |. X X X . X X O O O O O O X . X O O O|
    $$ |. O O O . X X X O O . X X O X X X X X|
    $$ |O X X . X X O O O O X X O O X O O O .|
    $$ |X . . X . X X O . O X . O . O O . . .|
    $$ ---------------------------------------
 
The markup to create the above diagram looks like this::

    .. go:: 
        :alt: A basic go diagram.
    
        $$ ---------------------------------------
        $$ |O O O . X O O X X O O . . . . . . . .|
        $$ |X X O O O O X X X X O . . O . . . . .|
        $$ |X . X O X X X O . X O . O . O O . . .|
        $$ |. X X O O O O X X . X O O O X X O . .|
        $$ |X . X O . O X X . X X X X X X O O O .|
        $$ |. X O O O O O X . X . O O . X X X O .|
        $$ |. X O . . O X X X X O O X X X O O . .|
        $$ |. X O O . O O O X O X X X O O O . O O|
        $$ |. . X O O X X O X . . . O X X O O X X| 
        $$ |. . X O O X O O X O . . X X . X X X .|
        $$ |. O X X O X O O X . X . X . . . . X X|
        $$ |. X . . X X X X . X X X . X X X X O X|
        $$ |. X . X . X . X X O X O X X X . O . O|
        $$ |. X X X . X X O O O O O O X . X O O O|
        $$ |. O O O . X X X O O . X X O X X X X X|
        $$ |O X X . X X O O O O X X O O X O O O .|
        $$ |X . . X . X X O . O X . O . O O . . .|
        $$ ---------------------------------------
     

That's it.  For now it works using data URIs.  If you specify a filename, it creates a file, but it puts it in the wrong place.  That needs to be fixed.
