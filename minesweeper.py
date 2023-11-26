from cmu_graphics import *
import copy
import random

#Initial Setup
def onAppStart(app):
    reset(app)

def reset(app):
    setSize(app, 0)
    # Easy board (0) = 9x9, 10 mines, font 48
    # Medium board (1) = 16x16, 40 mines, font 24
    # Hard board (2) = 16x30, 99 mines, font 16

    app.showBoard = [([False] * app.cols) for row in range(app.rows)]
    app.board = [([0] * app.cols) for row in range(app.rows)]
    app.boardLeft = 30
    app.boardTop = 100
    app.boardWidth = (600 - (2 * app.boardLeft))
    app.boardHeight = app.boardWidth
    if app.cols == 30:
        app.boardWidth *= 2
    app.height = app.boardHeight + app.boardTop + 20
    app.width = app.boardWidth + app.boardLeft * 2
    app.cellBorderWidth = 2

    app.colors = ['black', 'dodgerBlue', 'green', 'red', 'darkBlue', 'brown',
                  'skyBlue', 'purple', 'darkGray']
    app.flagged = []
    app.firstClick = (None, None)

    # generateMines(app)
    # generateNumbers(app)

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
    if len(app.flagged) > app.numMines:
        return 0
    return app.numMines - len(app.flagged)

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
        elif app.board[x][y] != '*':
            app.board[x][y] = '*'
            n += 1

def generateNumbers(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] != '*':
                app.board[row][col] = searchSurrounding(app, row, col)

def searchSurrounding(app, row, col):
    count = 0
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol] == '*':
                count += 1
    return count

def checkWin(app):
    if len(app.flagged) != app.numMines:
        return False
    for row, col in app.flagged:
        if app.board[row][col] != '*':
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
                if button == 0 and (row, col) not in app.flagged:
                    if app.firstClick == (None, None):
                        app.firstClick = (row, col)
                        generateMines(app)
                        generateNumbers(app)
                    if app.board[row][col] == 0:
                        floodFill(app, row, col)
                    elif app.board[row][col] == '*':
                        app.gameOver = True
                    app.showBoard[row][col] = True
                elif (button == 2 and app.firstClick != (None, None) and  
                      not app.showBoard[row][col]):
                    if (row, col) in app.flagged:
                        app.flagged.remove((row, col))
                    else:
                        app.flagged.append((row, col))
                
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
    
    app.board[row][col] = new
    app.showBoard[row][col] = True
    revealSurrounding(app, row, col)

    while len(queue) > 0:
        currRow, currCol = queue.pop()

        for drow in [-1, 1]:
            if isValid(app, currRow + drow, currCol, old):
                app.board[currRow + drow][currCol] = new
                app.showBoard[currRow + drow][currCol] = True
                revealSurrounding(app, currRow + drow, currCol)
                queue.append((currRow + drow, currCol))
        
        for dcol in [-1, 1]:
            if isValid(app, currRow, currCol + dcol, old):
                app.board[currRow][currCol + dcol] = new
                app.showBoard[currRow][currCol + dcol] = True
                revealSurrounding(app, currRow, currCol + dcol)
                queue.append((currRow, currCol + dcol))
            
def isValid(app, row, col, old):
    rows, cols = len(app.board), len(app.board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols) or
        (app.board[row][col] != old)):
        return False
    else:
        return True

# def floodFill(app, row, col):
#     oldValue = 0
#     newValue = -1
#     if oldValue != newValue:
#         floodFillHelper(app, row, col, oldValue, newValue)

# def floodFillHelper(app, row, col, oldValue, newValue):
#     rows, cols = len(app.board), len(app.board[0])
#     if ((row < 0) or (row >= rows) or
#         (col < 0) or (col >= cols) or
#         (app.board[row][col] != oldValue)):
#         return
#     else:
#         app.board[row][col] = newValue
#         app.showBoard[row][col] = True
#         revealSurrounding(app, row, col)
#         floodFillHelper(app, row-1, col, oldValue, newValue)
#         floodFillHelper(app, row+1, col, oldValue, newValue)
#         floodFillHelper(app, row, col-1, oldValue, newValue)
#         floodFillHelper(app, row, col+1, oldValue, newValue)

def revealSurrounding(app, row, col):
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol] not in ['*', 0, -1]:
            app.showBoard[newRow][newCol] = True

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
                 fill='red', opacity=90)
        drawLabel('You Lose! Press r to restart', app.width/2, app.height/2,
                  size=24, bold=True)
    elif app.win:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='blue', opacity=90)
        drawLabel('You Win! Press r to restart', app.width/2, app.height/2,
                  size=24, bold=True)
        drawLabel(f'Time: {timeString}', app.width/2, app.height/2 + 30,
                  size=24, bold=True)

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
    if app.board[row][col] == -1:
        color = 'green'
    else:
        color = 'lightGreen'
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill=color,
             border='black', borderWidth=app.cellBorderWidth)
    if (app.showBoard[row][col] and 
        app.board[row][col] != 0 and app.board[row][col] != -1):
        if type(app.board[row][col]) == int:
            color = app.colors[app.board[row][col]]
        drawLabel(app.board[row][col], cellLeft + cellWidth/2, 
                  cellTop + cellHeight/2, bold=True, fill=color, 
                  size=app.fontSize, align='center')
    elif app.showBoard[row][col] == False:
        for i in range(len(app.flagged)):
            (flagRow, flagCol) = app.flagged[i]
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