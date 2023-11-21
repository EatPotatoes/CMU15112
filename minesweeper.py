from cmu_graphics import *
import datetime
from datetime import date
import copy
import random

def onAppStart(app):
    reset(app)

def reset(app):
    app.rows, app.cols = 9, 9
    app.numMines = 10
    app.fontSize = 48
    # Easy board = 9x9, 10 mines, font 48
    # Medium board = 16x16, 40 mines, font 24
    # Hard board = 16x30, 99 mines, font 16

    app.showBoard = [([False] * app.cols) for row in range(app.rows)]
    app.board = [([0] * app.cols) for row in range(app.rows)]
    app.boardLeft = 30
    app.boardTop = 100
    app.boardWidth = (app.width - (2 * app.boardLeft))
    app.boardHeight = app.boardWidth
    if app.cols == 30:
        app.boardWidth *= 2
    app.height = app.boardHeight + app.boardTop + 20
    app.width = app.boardWidth + app.boardLeft * 2
    # app.boardHeight = (app.height - (app.boardTop + 20))
    app.cellBorderWidth = 2

    app.flagged = []

    generateMines(app)
    generateNumbers(app)

    app.gameOver = False
    app.win = False

def generateMines(app):
    n = 0
    while n < app.numMines:
        x = random.randrange(app.rows)
        y = random.randrange(app.cols)
        if app.board[x][y] != '*':
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
            
def onKeyPress(app, key):
    if key == 'r':
        reset(app)

def onMousePress(app, mouseX, mouseY, button):
    if app.gameOver or app.win:
        return
    for row in range(app.rows):
        for col in range(app.cols):
            if mouseInCell(app, row, col, mouseX, mouseY):
                if button == 0 and (row, col) not in app.flagged:
                    if app.board[row][col] == 0:
                        floodFill(app, row, col)
                    elif app.board[row][col] == '*':
                        app.gameOver = True
                    app.showBoard[row][col] = True
                elif button == 2 and not app.showBoard[row][col]:
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

def floodFill(app, row, col):
    oldValue = 0
    newValue = -1
    if oldValue != newValue:
        floodFillHelper(app, row, col, oldValue, newValue)

def floodFillHelper(app, row, col, oldValue, newValue):
    rows, cols = len(app.board), len(app.board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols) or
        (app.board[row][col] != oldValue)):
        return
    else:
        app.board[row][col] = newValue
        app.showBoard[row][col] = True
        revealSurrounding(app, row, col)
        floodFillHelper(app, row-1, col, oldValue, newValue) # up
        floodFillHelper(app, row+1, col, oldValue, newValue) # down
        floodFillHelper(app, row, col-1, oldValue, newValue) # left
        floodFillHelper(app, row, col+1, oldValue, newValue) # right

def revealSurrounding(app, row, col):
    for drow, dcol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), 
                       (1, 0), (1, 1)]:
        newRow, newCol = row + drow, col + dcol
        if (newRow < 0 or newRow >= app.rows or newCol < 0 or 
            newCol >= app.cols):
            continue
        if app.board[newRow][newCol] not in ['*', 0, -1]:
            app.showBoard[newRow][newCol] = True


def redrawAll(app):
    drawLabel('Minesweeper', app.width/2, app.boardTop/2, align='center',
              bold=True, size=32)
    drawBoard(app)
    if app.gameOver:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='red', opacity=75)
        drawLabel('You Lose! Press r to restart', app.width/2, app.height/2,
                  size=24, bold=True)
    elif app.win:
        drawRect(app.width/6, app.height/6, app.width*2/3, app.height*2/3,
                 fill='blue', opacity=75)
        drawLabel('You Win! Press r to restart', app.width/2, app.height/2,
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
        drawLabel(app.board[row][col], cellLeft + cellWidth/2, 
                  cellTop + cellHeight/2, bold=True, fill='black', 
                  size=app.fontSize, align='center')
    elif app.showBoard[row][col] == False:
        if (row, col) in app.flagged:
            drawLabel('^', cellLeft + cellWidth/2, cellTop + cellHeight/2,
                      bold=True, fill='red', size=app.fontSize, align='center')

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