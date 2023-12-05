Minesweeper
Albert Zhang (albertz2)
Carnegie Mellon University 15-112 Fall 2023 Term Project

----------

Description

A recreation of the traditional minesweeper game, it allows the user to play on any of 3 different board sizes: 
- Easy (9 x 9 with 10 mines)
- Medium (16 x 16 with 40 mines)
- Hard (16 x 30 with 99 mines)
- Custom ([5-25] x [10-50] with at most 0.5 * #ofTiles mines)

There will be a rectangular grid with square cells as the board, with mines placed randomly in different cells (unknown to the user, but unchanging for each different game). The user has two options, left click to clear a space or right click to mark a mine. There is also an option for the user to receive a hint, if desired.
Each cleared space provides the number of mines within the 8 tiles immediately touching or diagonally touching the space. 
The game is over when the user clears a space with a mine (loss) or marks all spaces with flags (victory).

----------

How to Run

There are only 2 required items to run this project. 1) The "minesweeper.py" file, which is the file to run to start the game. 2) The "images" folder, which will contain images used in the project. Both these files should be on the same level in the same file directory, and are both provided within the zip that contains this file.

There should be no external libraries or modules required beyond the imports at the top of the minesweeper.py file

----------

Shortcuts (also available in the "rules" page within the game):

- Press p to pause the game
- Press r to restart the game
- Press h for a hint (details in the rules page)
- Press m to return to main menu (game must be paused or over)

----------
