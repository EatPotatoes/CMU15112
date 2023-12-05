### ALBERT ZHANG (albertz2)
### CMU 15-112 F23 Term Project
### MINESWEEPER

from cmu_graphics import *
from PIL import Image
import copy
import random
import math

# ༼ つ ◕_◕ ༽つ We love OOP ༼ つ ◕_◕ ༽つ
class Tile:
    #Keep track of all flagged tiles and tile size (depends on board size)
    flagged = []
    size = None

    def __init__(self,):
        self.hasMine = False
        self.show = False
        self.value = 0
        self.hasFlag = False
        self.showMineHint = False
        self.showSpaceHint = False
        self.highlight = False

    def addMine(self):
        self.hasMine = True
        self.value = 9
    
    def removeMine(self):
        self.hasMine = False

#Initial Setup
def onAppStart(app):
    app.flag = Image.open('images/flag.png')
    app.mine = Image.open('images/mine.png')
    app.numbers = []
    for i in range(1, 9):
        # Number images cropped and edited from
        # https://www.reddit.com/r/Minesweeper/comments/qf1735/minesweeper_numbers_tier_list/
        image = Image.open(f'images/{i}.png')
        app.numbers.append(image)

    app.width, app.height = 600, 700

def reset(app):
    #Initialize empty board (mines placed after first click)
    app.board = []
    Tile.flagged = []
    for row in range(app.rows):
        currRow = []
        for col in range(app.cols):
            currRow.append(Tile())
        app.board.append(currRow)
    setBoardSize(app)

    #Variables for gameplay
    app.firstClick = (None, None)
    app.mineCoords = []

    #Variables for stopwatch
    app.time = 0
    app.stepsPerSecond = 10
    app.count = 0

    #Variables for game status (pause/win/lose)
    app.paused = False
    app.gameOver = False
    app.win = False
    app.revealMines = False

    # Images, usage/implementation referenced from makeNewImages.py, 
    # shared by instructors via Piazza
    app.headerFlag = CMUImage(app.flag.resize((30, 30)))
    Tile.size = getCellSize(app)
    (x, y) = Tile.size
    Tile.size = (x - 5, y - 5)
    app.tileFlag = CMUImage(app.flag.resize(Tile.size))
    app.tileMine = CMUImage(app.mine.resize(Tile.size))
    Tile.size = (x - 15, y - 15)
    
    app.numImages = []
    for image in app.numbers:
        newImage = CMUImage(image.resize(Tile.size))
        app.numImages.append(newImage)
    
def setBoardSize(app):
    #Set board dimensions
    app.boardLeft = 30
    app.boardTop = 100
    app.boardWidth = (600 - (2 * app.boardLeft))
    app.boardHeight = app.boardWidth
    if app.cols >= 30:
        app.boardWidth *= math.floor(app.cols / 16) + 1
        app.boardWidth = 1400
    if app.rows > 16:
        app.boardHeight = 700
    app.height = app.boardHeight + app.boardTop + 20
    app.width = app.boardWidth + app.boardLeft * 2
    if app.cols >= 16:
        app.width -= 12
        app.height -= 2
    elif app.cols >= 30:
        app.height -= 2
    app.cellBorderWidth = 2

def game_onStep(app):
    #Increase stopwatch if game is going
    app.count += 1
    if (app.firstClick != (None, None) and not app.gameOver and not app.win and
        not app.paused):
        app.time += 1 if app.count % 10 == 0 else 0
    #Reveal mines one by one if game is over
    if app.revealMines:
        revealNextMine(app)

def revealNextMine(app):
    #Go through mines and reveal next one
    for x, y in app.mineCoords:
        if app.board[x][y].show == False:
            app.board[x][y].show = True
            return

#Find (VERY BASIC) move that is possible from given information, just overlooked
#by the player (Note: This is not a solver, it just reveals a move)
#https://github.com/Developer-Mike/Minesweeper-AI/blob/master/game.py 
def hint(app):
    #Basically only reveals with given information
    #Also functions under the assumption user has not made any mistakes yet
    for row in range(app.rows):
        for col in range(app.cols):
            currTile = app.board[row][col]
            if not currTile.show:
                continue

            #Get neighboring tiles of any given revealed space
            neighbors, flags = getUncoveredNeighbors(app, row, col)
            uncovered = len(neighbors) + flags

            #If number of flags + number of unrevealed spaces = number of mines
            #Show mine as hint
            if currTile.value == uncovered:
                for neighbor in neighbors:
                    neighbor.showMineHint = True
                    currTile.highlight = True
                    return
                
            #If all nieghbor mines are flagged and there are neighbors uncovered
            #They are safe to uncover
            elif currTile.value == flags and len(neighbors) > 0:
                for neighbor in neighbors:
                    neighbor.showSpaceHint = True
                    currTile.highlight = True
                return

def unhighlight(app):
    #remove all hint-based highlights from board
    #this function is called on user action
    for row in range(app.rows):
        for col in range(app.cols):
            currTile = app.board[row][col]
            currTile.highlight = False
            currTile.showSpaceHint = False
            currTile.showMineHint = False
                        

def getUncoveredNeighbors(app, row, col):
    neighbors = []
    flags = 0
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        #Go through all 8 neighbors (excluding out of bounds)
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        neighbor = app.board[newRow][newCol]
        #If neighbor unrevealed and has no flag, add to neighbor list
        if neighbor.show == False and not neighbor.hasFlag:
            neighbors.append(app.board[newRow][newCol])
        #If neighbor has flag, add to count of neighboring flags
        if neighbor.hasFlag:
            flags += 1
    return neighbors, flags

def setSize(app, size):
    # Easy board (0) = 9x9, 10 mines, font 48
    # Medium board (1) = 16x16, 40 mines, font 24
    # Hard board (2) = 16x30, 99 mines, font 16
    if size == 0:
        app.rows, app.cols = 9, 9
        app.numMines = 10
        app.fontSize = 48
    elif size == 1:
        app.rows, app.cols = 16, 16
        app.numMines = 40
        app.fontSize = 24
    elif size == 2:
        app.rows, app.cols = 16, 30
        app.numMines = 99
        app.fontSize = 18
    elif size == 3:
        app.rows, app.cols, app.numMines = getSize(app)

def getSize(app):
    rows = app.getTextInput('''Enter number of rows 5-25 or -1 to cancel
                            (about 1:2 rows:cols is ideal)''')
    if rows == '-1':  
        return (-1, -1, -1)
    #rows must be numbers only
    while not rows.isdigit() or int(rows) > 25 or int(rows) <= 4:  
        if rows == '-1':  
            return (-1, -1, -1)
        rows = app.getTextInput('''Invalid: Enter number of rows 5-25 or 
                                -1 to cancel (about 1:2 rows:cols is ideal)''')
        
    cols = app.getTextInput('''Enter number of columns 10-50 or -1 to cancel
                            (about 1:2 rows:cols is ideal)''')
    if cols == '-1':  
        return (-1, -1, -1)
    #cols must be numbers only
    while not cols.isdigit() or int(cols) > 50 or int(cols) <= 9:  
        if cols == '-1':  
            return (-1, -1, -1)
        cols = app.getTextInput('''Invalid: Enter number of cols 10-50 or 
                                -1 to cancel (about 1:2 rows:cols is ideal)''')
        
    mines = app.getTextInput('''Enter number of mines 
                             (less than 0.5*rows*cols) or -1 to cancel 
                             (about 1:8 mines:tiles is ideal)''')
    if mines == '-1':  
        return (-1, -1, -1)
    #mines must be less than number of tiles
    while not mines.isdigit() or int(mines) >= int(int(rows) * int(cols) * 0.5):  
        if mines == '-1':  
            return (-1, -1, -1)
        mines= app.getTextInput('''Invalid: Enter number of mines 
                                (less than 0.5*rows*cols) or -1 to cancel 
                                (about 1:8 mines:tiles is ideal)''')
        
    return int(rows), int(cols), int(mines)

def getFlagCount(app):
    if len(Tile.flagged) > app.numMines:
        return 0
    return app.numMines - len(Tile.flagged)

def generateMines(app):
    n = 1
    (firstX, firstY) = app.firstClick
    if firstX > 1:
        dx = -1
    else:
        dx = 1
    if firstY > 1:
        dy = -1
    else:
        dy = 1
    newX = firstX + 2 * dx
    newY = firstY + 2 * dy

    app.board[newX][newY].addMine()
    while n < app.numMines:
        x = random.randrange(app.rows)
        y = random.randrange(app.cols)

        if abs(firstX - x) <= 1 and abs(firstY - y) <= 1:
            # guarantees no mines within the 3x3 square 
            # that is centered around first click
            continue
        elif searchSurrounding(app, x, y) >= 5:
            #no large chunk of mines
            continue
        elif not app.board[x][y].hasMine:
            app.board[x][y].addMine()
            app.mineCoords.append((x, y))
            n += 1

    if not solvable(app):
        generateMines(app)

# Characteristics of "unsolvable" boards (not every part of either source is used)
# https://stackoverflow.com/questions/27815411/mine-sweeper-improve-mine-random-locate-algorithm
# https://www.reddit.com/r/Minesweeper/comments/ze9vz4/how_are_guessfree_minesweeper_games_generated/ 
def solvable(app):
    for row in range(app.rows):
        rowMines = 0 
        for col in range(app.cols):
            if app.board[row][col].hasMine:
                rowMines += 1
        if rowMines == app.rows: #check whole row for mines
            return False
        
    for col in range(app.cols):
        colMines = 0
        for row in range(app.rows):
            if app.board[row][col].hasMine:
                colMines += 1
            if colMines == app.cols: #check whole col for mines
                return False
    
    for x, y in app.mineCoords:
        if searchSurrounding(app, x, y) >= 6:
                return False

    return True
    
def isRectangular(app):
    #Get min and max row and col of the first click floodfill
    #also count number of tiles revealed by floodfill
    minRow, maxRow = app.rows, -1
    minCol, maxCol = app.cols, -1
    count = 0
    for row in range(app.rows):
        for col in range(app.cols):
            currTile = app.board[row][col]
            if currTile.show:
                count += 1
                if row > maxRow:
                    maxRow = row
                if row < minRow:
                    minRow = row
                if col > maxCol:
                    maxCol = col
                if col < minCol:
                    minCol = col
    #Floodfill is rectangular if number of revealed tiles from floodfill is
    #equal to area of rectangle of min and max row and col
    area = (maxRow - minRow + 1) * (maxCol - minCol + 1)
    return area == count
    #I am pretty sure there is no exception to this but if there is I have not
    #run into it and either way it will just regenerate a non-rectangular area

def generateNumbers(app):
    #After mines placed, each tile has an unchanging number of adjacent mines,
    #assigned in this function
    for row in range(app.rows):
        for col in range(app.cols):
            if not app.board[row][col].hasMine:
                app.board[row][col].value = searchSurrounding(app, row, col)

def searchSurrounding(app, row, col):
    #Counts number of adjacent mines
    count = 0
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol].hasMine:
            count += 1
    return count

def checkWin(app):
    #Win is defined when all tiles with mines are flagged
    if len(Tile.flagged) != app.numMines:
        return False
    for row, col in Tile.flagged:
        if not app.board[row][col].hasMine:
            return False

    return True

#Control (MVC) Functions
def game_onKeyPress(app, key):
    if key == 'r':
        reset(app)

    if key == 'm' and (app.paused or app.gameOver or app.win):
        setActiveScreen('home')
        app.width, app.height = 600, 700

    if (key == 'h' and not (app.paused or app.gameOver or app.win or 
                            app.firstClick == (None, None))):
        hint(app)

    if app.gameOver or app.win:
        return
    
    if key == 'p':
        app.paused = not app.paused

# Had to mess with cmu_graphics file for right clicking to work with screens 
# seen here https://piazza.com/class/lkq6ivek5cg1bc/post/2427 
def game_onMousePress(app, mouseX, mouseY, button):
    if app.gameOver or app.win or app.paused:
        return
    
    for row in range(app.rows):
        for col in range(app.cols):
            #Checks the tile on board that is clicked
            if mouseInCell(app, row, col, mouseX, mouseY):
                #User left click
                if button == 0 and (row, col) not in Tile.flagged:
                    #First Click generates board
                    if app.firstClick == (None, None):
                        app.firstClick = (row, col)
                        generateMines(app)
                        generateNumbers(app)
                        floodFill(app, row, col)
                        #Regenerate board in case of rectangular start
                        if isRectangular(app):
                            reset(app)
                            app.firstClick = (row, col)
                            generateMines(app)
                            generateNumbers(app)
                            floodFill(app, row, col)
                    #Floodfill if click on empty space
                    if app.board[row][col].value == 0:
                        floodFill(app, row, col)
                    #Click is on a mine = lose game
                    elif app.board[row][col].hasMine:
                        app.gameOver = True
                        app.revealMines = True
                    #Reset the background colors of tiles after a hint
                    app.board[row][col].show = True
                    app.board[row][col].showMineHint = False
                    app.board[row][col].showSpaceHint = False
                    unhighlight(app)
                #User right click (also checks no flags before mine placement)
                #also checks not flagging a revealed tile
                elif (button == 2 and app.firstClick != (None, None) and  
                      not app.board[row][col].show):
                    #Reset the background colors of tiles after a hint
                    app.board[row][col].showMineHint = False
                    app.board[row][col].showSpaceHint = False
                    unhighlight(app)
                    #Remove flag if space was flagged
                    if (row, col) in Tile.flagged:
                        Tile.flagged.remove((row, col))
                        app.board[row][col].hasFlag = False
                    #Add flag if space was not flagged and eligible for flag
                    else:
                        Tile.flagged.append((row, col))
                        app.board[row][col].hasFlag = True
                
                #If last move was game winning, change status to won
                if checkWin(app):
                    app.win = True

def mouseInCell(app, row, col, mouseX, mouseY):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    if (cellLeft < mouseX < cellLeft + cellWidth and
        cellTop < mouseY < cellTop + cellHeight):
        return True

# ALGORITHM PSEUDOCODE FOR FLOODFILL
# https://en.wikipedia.org/wiki/Flood_fill#Moving_the_recursion_into_a_data_structure
def floodFill(app, row, col):
    #Creates a queue of tiles to be revealed by floodfill
    old = 0
    new = -1
    queue = []
    queue.append((row, col))
    
    app.board[row][col].value = new
    app.board[row][col].show = True
    revealSurrounding(app, row, col)

    #Continue to reveal tiles in queue until queue empty
    while len(queue) > 0:
        currRow, currCol = queue.pop()

        for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
            newRow, newCol = currRow + drow, currCol + dcol
            #Adds tiles to queue that can be floodfilled
            if isValid(app, newRow, newCol, old):
                app.board[newRow][newCol].value = new
                app.board[newRow][newCol].show = True
                revealSurrounding(app, newRow, newCol)
                queue.append((newRow, newCol))
            
def isValid(app, row, col, old):
    #Tile is valid to be floodfilled if same value and not out of bounds
    rows, cols = len(app.board), len(app.board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols) or
        (app.board[row][col].value != old)):
        return False
    else:
        return True

def revealSurrounding(app, row, col):
    #Reveals surrounding tiles so floodfill includes numbers on edge
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol].value not in ['*', 0, -1]:
            app.board[newRow][newCol].show = True

#View (MVC) Functions Below

def game_redrawAll(app):
    drawLabel('Minesweeper', app.width/2, app.boardTop/2, align='center',
              bold=True, size=32)
    drawLabel(f'{getFlagCount(app)}', app.width/8, app.boardTop/2,
              align='center', bold=True, size=32)
    drawImage(app.headerFlag, app.width/8 + 40, app.boardTop/2, align='center')
    
    #Stopwatch
    timeString = '00:00'
    if app.time > 0:
        minutes = app.time // 60
        seconds = app.time % 60
        timeString = f'{minutes}:{seconds}'
        if minutes < 10:
            timeString = '0' + timeString
        if seconds < 10:
            timeString = timeString[:-1] + '0' + timeString[-1]
    drawLabel(timeString, app.width*7/8, app.boardTop/2, align='center',
              bold=True, size=32)
    
    drawBoard(app)

    #Paused screen
    if app.paused:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='gray', opacity=90)
        drawLabel('Paused', app.width/2, app.height/2 - 30,
                  size=24, bold=True)
        drawLabel('Press p to resume', app.width/2, app.height/2,
                  size=24, bold=True)
        drawLabel('Press m to go to main menu', app.width/2, app.height/2 + 30,
                  size=24, bold=True)
    #Game over screen (loss)
    elif app.gameOver:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='red', opacity=75)
        drawLabel('You Lose! Press r to restart', app.width/2, app.height/2 - 15,
                  size=24, bold=True)
        drawLabel('Press m to go to main menu', app.width/2, app.height/2 + 15,
                  size=24, bold=True)
    #Win screen
    elif app.win:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='blue', opacity=75)
        drawLabel('You Win! Press r to restart', app.width/2, app.height/2 - 30,
                  size=24, bold=True)
        drawLabel(f'Time: {timeString}', app.width/2, app.height/2,
                  size=24, bold=True)
        drawLabel('Press m to go to main menu', app.width/2, app.height/2 + 30,
                  size=24, bold=True)

# GENERAL STRUCTURE OF DRAWING BOARD REFERENCED FROM TETRIS HOMEWORK.
# INCLUDES DRAWBOARD, DRAWBOARDBORDER, DRAWCELL, GETCELLLEFTTOP, AND GETCELLSIZE
# https://academy.cs.cmu.edu/exercise/13125
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
            
    drawBoardBorder(app)

def drawBoardBorder(app):
  # draw the board outline (with double-thickness):
  cellWidth, cellHeight = getCellSize(app)
  drawRect(app.boardLeft, app.boardTop, app.cols*cellWidth, 
           app.rows*cellHeight,
           fill=None, border='black',
           borderWidth = 2 * app.cellBorderWidth)

def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)

    #Changes tile background based on hints or if tile has been revealed
    if app.board[row][col].highlight:
        color = 'gold'
    elif app.board[row][col].show:
        color = 'green'
    elif app.board[row][col].showMineHint:
        color = 'crimson'
    elif app.board[row][col].showSpaceHint:
        color = 'blue'
    else:
        color = 'lightGreen'
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill=color,
             border='black', borderWidth=app.cellBorderWidth)
    
    #Draws tile that are revealed and not empty (aka tile has number or mine)
    if (app.board[row][col].show and 
        app.board[row][col].value != 0 and app.board[row][col].value != -1):
        if app.board[row][col].value == 9:
            drawImage(app.tileMine, cellLeft+cellWidth/2, cellTop+cellHeight/2,
                      align='center')
        else:
            number = app.numImages[app.board[row][col].value - 1]
            drawImage(number, cellLeft + cellWidth/2, 
                  cellTop + cellHeight/2, align='center')
    #Draw flags
    elif app.board[row][col].show == False:
        for i in range(len(Tile.flagged)):
            (flagRow, flagCol) = Tile.flagged[i]
            if (row, col) == (flagRow, flagCol):
                if i < app.numMines:
                    drawImage(app.tileFlag, cellLeft+cellWidth/2, 
                              cellTop+cellHeight/2, align='center')
                else:
                    drawLabel('?', cellLeft+cellWidth/2, cellTop+cellHeight/2,
                             bold=True, fill='black', size=app.fontSize, 
                             align='center')

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (int(cellWidth), int(cellHeight))

##------------------------------------------------------------------------------

def home_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='lightGreen')
    drawLabel('Minesweeper', app.width/2, app.height/10, align='top',
              bold=True, size=60)
    
    #Buttons
    text = ['Easy', 'Medium', 'Hard', 'Custom', 'Rules']
    for i in range(2, 7):
        drawRect(app.width/2, app.height*i/7, app.width/3, app.height/10, 
                 align='center', border='black', fill='lightGray')
        
        drawLabel(text[i-2], app.width/2, app.height*i/7, size=36, bold=True,
                align='center')
        
def home_onMousePress(app, mouseX, mouseY, button):
    for i in range(5):
        startX, endX = 200, 400
        startY, endY = 165 + 100*i, 235 + 100*i
        if (startX <= mouseX <= endX and startY <= mouseY <= endY):
            if i < 4:
                setSize(app, i)
                if (app.rows, app.cols, app.numMines) == (-1, -1, -1):
                    setActiveScreen('home')
                else:
                    reset(app)
                    setActiveScreen('game')
            else:
                setActiveScreen('rules')

##------------------------------------------------------------------------------

def rules_redrawAll(app):
    #Background
    drawRect(0, 0, app.width, app.height, fill='lightBlue')
    #Back button
    drawRect(10, 10, 100, 40, fill='lightGray', border='black')
    drawLabel('Back', 60, 30, size=24, fill='black', bold=True, align='center')
    #Rules text
    drawLabel('Rules', app.width/2, app.height/10, align='top',
              bold=True, size=48)
    text = [
        'Mines will be placed randomly on the board',
        'Left-click to reveal tiles',
        'Right-click to flag/unflag',
        'Revealed tiles with numbers indicate the',
        'number of mines immediately around the tile',
        'Revealing a mine leads to lose',
        'Flagging all mines leads to win',
        'Press p to pause',
        'Press r to restart',
        'Press h for a hint (blue for clear, red for mine)',
        'Press m to return to main menu while paused or game over'
    ]
    for i in range(len(text)):
        drawLabel(text[i], app.width/2, 150 + 50*i, align='top',
                  size=16)
        
def rules_onKeyPress(app, key):
    if key == 'm':
        setActiveScreen('home')

def rules_onMousePress(app, mouseX, mouseY, button):
    startX, startY = 10, 10
    endX, endY = 100, 40
    if (startX <= mouseX <= endX and startY <= mouseY <= endY):
        setActiveScreen('home')

def main():
    # runApp(width=600, height=800)
    runAppWithScreens(initialScreen='home')

main()