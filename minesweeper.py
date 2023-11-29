from cmu_graphics import *
import copy
import random

class Tile:
    flagged = []

    def __init__(self,):
        self.hasMine = False
        self.show = False
        self.value = 0

    def addMine(self):
        self.hasMine = True
        self.value = 9
    
    def removeMine(self):
        self.hasMine = False

#Initial Setup
def onAppStart(app):
    reset(app)

def reset(app):
    setSize(app, 1)
    # Easy board (0) = 9x9, 10 mines, font 48
    # Medium board (1) = 16x16, 40 mines, font 24
    # Hard board (2) = 16x30, 99 mines, font 16

    app.board = []
    Tile.flagged = []
    for row in range(app.rows):
        currRow = []
        for col in range(app.cols):
            currRow.append(Tile())
        app.board.append(currRow)
    app.boardLeft = 30
    app.boardTop = 100
    app.boardWidth = (600 - (2 * app.boardLeft))
    app.boardHeight = app.boardWidth
    if app.cols == 30:
        app.boardWidth *= 2
    app.height = app.boardHeight + app.boardTop + 20
    app.width = app.boardWidth + app.boardLeft * 2
    app.cellBorderWidth = 2

    app.colors = ['black', 'dodgerBlue', 'limeGreen', 'red', 'darkBlue', 'brown',
                  'skyBlue', 'purple', 'darkGray', 'black']

    app.firstClick = (None, None)

    app.time = 0
    app.stepsPerSecond = 1
    app.paused = False
    app.gameOver = False
    app.win = False

def onStep(app):
    if (app.firstClick != (None, None) and not app.gameOver and not app.win and
        not app.paused):
        app.time += 1

def setSize(app, size):
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
        app.fontSize = 16

def getFlagCount(app):
    if len(Tile.flagged) > app.numMines:
        return 0
    return app.numMines - len(Tile.flagged)

def generateMines(app):
    n = 0
    while n < app.numMines:
        x = random.randrange(app.rows)
        y = random.randrange(app.cols)

        (firstX, firstY) = app.firstClick
        if abs(firstX - x) <= 1 and abs(firstY - y) <= 1:
            # guarantees no mines within the 3x3 square 
            # that is centered around first click
            continue
        elif searchSurrounding(app, x, y) >= 5:
            continue
        elif not app.board[x][y].hasMine:
            app.board[x][y].addMine()
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
            if searchSurrounding(app, row, col) >= 7:
                return False
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
    return True
    


def generateNumbers(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if not app.board[row][col].hasMine:
                app.board[row][col].value = searchSurrounding(app, row, col)

def searchSurrounding(app, row, col):
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
    if len(Tile.flagged) != app.numMines:
        return False
    for row, col in Tile.flagged:
        if not app.board[row][col].hasMine:
            return False

    return True

#Control (MVC) Functions
def onKeyPress(app, key):
    if key == 'r':
        reset(app)

    if app.gameOver or app.win:
        return
    
    if key == 'p':
        app.paused = not app.paused

def onMousePress(app, mouseX, mouseY, button):
    if app.gameOver or app.win or app.paused:
        return
    
    for row in range(app.rows):
        for col in range(app.cols):
            if mouseInCell(app, row, col, mouseX, mouseY):
                if button == 0 and (row, col) not in Tile.flagged:
                    if app.firstClick == (None, None):
                        app.firstClick = (row, col)
                        generateMines(app)
                        generateNumbers(app)
                    if app.board[row][col].value == 0:
                        floodFill(app, row, col)
                    elif app.board[row][col].hasMine:
                        app.gameOver = True
                    app.board[row][col].show = True
                elif (button == 2 and app.firstClick != (None, None) and  
                      not app.board[row][col].show):
                    if (row, col) in Tile.flagged:
                        Tile.flagged.remove((row, col))
                    else:
                        Tile.flagged.append((row, col))
                
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
    old = 0
    new = -1
    queue = []
    queue.append((row, col))
    
    app.board[row][col].value = new
    app.board[row][col].show = True
    revealSurrounding(app, row, col)

    while len(queue) > 0:
        currRow, currCol = queue.pop()

        for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
            newRow, newCol = currRow + drow, currCol + dcol
            if isValid(app, newRow, newCol, old):
                app.board[newRow][newCol].value = new
                # app.board[newRow][newCol] = new
                app.board[newRow][newCol].show = True
                revealSurrounding(app, newRow, newCol)
                queue.append((newRow, newCol))
            
def isValid(app, row, col, old):
    rows, cols = len(app.board), len(app.board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols) or
        (app.board[row][col].value != old)):
        return False
    else:
        return True

def revealSurrounding(app, row, col):
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol].value not in ['*', 0, -1]:
            app.board[newRow][newCol].show = True

#View (MVC) Functions Below

def redrawAll(app):
    drawLabel('Minesweeper', app.width/2, app.boardTop/2, align='center',
              bold=True, size=32)
    drawLabel(f'{getFlagCount(app)}', app.width/8, app.boardTop/2,
              align='center', bold=True, size=32)
    
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
    if app.paused:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='gray', opacity=90)
        drawLabel('Paused', app.width/2, app.height/2,
                  size=24, bold=True)
        drawLabel('Press p to resume', app.width/2, app.height/2 + 30,
                  size=24, bold=True)
    elif app.gameOver:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='red', opacity=75)
        drawLabel('You Lose! Press r to restart', app.width/2, app.height/2,
                  size=24, bold=True)
    elif app.win:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='blue', opacity=75)
        drawLabel('You Win! Press r to restart', app.width/2, app.height/2,
                  size=24, bold=True)
        drawLabel(f'Time: {timeString}', app.width/2, app.height/2 + 30,
                  size=24, bold=True)

# GENERAL STRUCTURE OF DRAWING BOARD REFERENCED FROM TETRIS HOMEWORK
# INCLUDES DRAWBOARD, DRAWBOARDBORDER, DRAWCELL, GETCELLLEFTTOP, AND GETCELLSIZE
# https://academy.cs.cmu.edu/exercise/13125
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
            
    drawBoardBorder(app)

def drawBoardBorder(app):
  # draw the board outline (with double-thickness):
  drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
           fill=None, border='black',
           borderWidth = 2 * app.cellBorderWidth)

def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    if app.board[row][col].show:
        color = 'green'
    else:
        color = 'lightGreen'
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill=color,
             border='black', borderWidth=app.cellBorderWidth)
    if (app.board[row][col].show and 
        app.board[row][col].value != 0 and app.board[row][col].value != -1):
        if type(app.board[row][col].value) == int:
            color = app.colors[app.board[row][col].value]
        if app.board[row][col].value == 9:
            value = '*'
        else:
            value = app.board[row][col].value
        drawLabel(value, cellLeft + cellWidth/2, 
                  cellTop + cellHeight/2, bold=True, fill=color, 
                  size=app.fontSize, align='center')
    elif app.board[row][col].show == False:
        for i in range(len(Tile.flagged)):
            (flagRow, flagCol) = Tile.flagged[i]
            if (row, col) == (flagRow, flagCol):
                if i < app.numMines:
                    symbol = '^'
                    color = 'red'
                else:
                    symbol = '?'
                    color = 'black'
                drawLabel(symbol, cellLeft+cellWidth/2, cellTop+cellHeight/2,
                          bold=True, fill=color, size=app.fontSize, 
                          align='center')

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def main():
    runApp(width=600, height=800)

main()