#encoding=utf-8
#Author: Tom Qian  
#Email: TomQianMaple@outlook.com



import pygame,sys
import numpy as np
import os
import AIPlayer
import random
class FiveInARow:

    rowNum=15
    columnNum=15
    imgPath='imgs'

    def __init__(self):

        pygame.init()

        self.size = width, height = 800, 800

        # load all relevant images
        self.screen = pygame.display.set_mode(self.size)

        # set title of window
        pygame.display.set_caption('Five in a Row')

        self.board = pygame.image.load("%s/board.gif"%FiveInARow.imgPath)
        self.board=pygame.transform.scale(self.board, (width, height)) #转化大小
        board_rect = self.board.get_rect()

        # cursor
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        self.refreshGame()

    def __distance(self,pos1,pos2):
        return np.sqrt(pow(pos1[0]-pos2[0],2)+pow(pos1[1]-pos2[1],2))

    def __accuratePosi(self,pos):
        row = (pos[0] - self.topLeftPos[0]) // self.cellLen
        column = (pos[1] - self.topLeftPos[1]) // self.cellLen
        # Determine the accurate position
        rowList = [row - 1, row, row + 1]
        columnList = [column - 1, column, column + 1]
        minDis = 9999999
        cloestPos = [-1, -1]
        for i in range(3):
            for j in range(3):
                tempRow = rowList[i]
                tempColumn = columnList[j]
                if tempRow < game.rowNum and tempRow >= 0 and tempColumn >= 0 and tempColumn < game.columnNum:
                    crossPos = self.boardGridPointPosMrx[tempRow][tempColumn]
                    tempDis = self.__distance(crossPos, pos)
                    if tempDis < minDis:
                        minDis = tempDis
                        cloestPos = [tempRow, tempColumn]
        return cloestPos

    def nextStep(self,player,posIndex):
        row,column=posIndex

        # Judge whether the position has been occupied
        #  problem: refer to http://www.cnblogs.com/btchenguang/archive/2012/01/30/2332479.html
        if self.boardStateMrx[row][column]=='null':

            self.boardStateMrx[row][column] = player


            piece=pygame.transform.scale(pygame.image.load("%s/focused_%s_piece.png"%(FiveInARow.imgPath,player)),(self.board.get_width()//18,self.board.get_height()//18))
            self.screen.blit(piece,(self.boardGridPointPosMrx[row][column][0]-piece.get_width()/2,self.boardGridPointPosMrx[row][column][1]-piece.get_height()/2))

            pygame.display.flip()

            return True
        else:
            return False


    def checkGameState(self,player):
        # Chekc Five in a Row
        occupiedCount=0
        for i in range(FiveInARow.rowNum):
            for j in range(FiveInARow.columnNum):
                piece=self.boardStateMrx[i][j]
                # judge whether one side has win
                if piece!='null':
                    occupiedCount+=1
                    result=self.checkNInARow((i,j),5,player)
                    if result:
                       return result

        if occupiedCount==self.columnNum*self.rowNum:
            return 'tie'

        return False

    # check (right, down, down left,down right), four directions.
    def checkNInARow(self,pos,N,player):
        x,y=pos
        # right

        directionList=['right','down','down-left','down-right']
        for direction in directionList:
            count = 0
            tempx = x
            tempy = y
            while tempx<FiveInARow.rowNum and tempy < FiveInARow.columnNum:
                if self.boardStateMrx[tempx][tempy]==player:
                    count+=1
                    if count == N:
                        return self.boardStateMrx[x][y]
                else:
                    break;

                if direction == 'right':
                    tempx += 1
                elif direction == 'down':
                    tempy += 1
                elif direction == 'down-left':
                    tempx -= 1
                    tempy += 1
                elif direction == 'down-right':
                    tempx += 1
                    tempy += 1

        return False

    def start(self,gameMode):
        # randomly choose piecetype
        humanPlayerPieceType='black'
        # choose game mode
        if not gameMode:
            gameMode=self.chooseGameMode()

        self.humanPlayerPieceType=humanPlayerPieceType

        # self.playMusic();
        print('gameMode:%s'%gameMode)
        if gameMode=='SimpleAI' or gameMode=='ReinforcementAI':
            AI=AIPlayer.FollowYouPlayer('white')

            nextTurnPlayer = humanPlayerPieceType
            while 1:
                # human player turn
                if nextTurnPlayer==humanPlayerPieceType:
                    event = pygame.event.wait()
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        nextPos = pygame.mouse.get_pos()
                        posIndex = self.__accuratePosi(nextPos)
                        lastAction = posIndex
                        # player may try clicking on positon that has already been occupied, it's ineffective
                        flag = self.nextStep(nextTurnPlayer, posIndex)
                    elif event.type == pygame.KEYDOWN:
                        if pygame.key.get_pressed()[pygame.K_SPACE] == 1:
                            self.refreshGame()
                        elif pygame.key.get_pressed()[pygame.K_r] == 1:
                            self.chooseGameMode()
                    else:
                        continue
                # AI player turn
                else:
                    action=AI.nextAction(self.boardStateMrx, lastAction)
                    flag = self.nextStep(nextTurnPlayer,action)


                # check whether the game has ended/ one player has won the game
                result = self.checkGameState(nextTurnPlayer)
                if result:
                    self.over(result)

                # switch turn
                if flag:
                    if nextTurnPlayer == 'white':
                        nextTurnPlayer = 'black'
                    else:
                        nextTurnPlayer = 'white'
        elif gameMode=='DoublePlayer':
            turnIndex = 0
            while 1:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_SPACE] == 1:
                        self.refreshGame()
                    elif pygame.key.get_pressed()[pygame.K_r] == 1:
                        self.chooseGameMode()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # if pygame.mouse.get_pressed()[0]==1:
                    nextTurnPlayer = ('black', 'white')[turnIndex % 2]
                    nextPos = pygame.mouse.get_pos()
                    posIndex = self.__accuratePosi(nextPos)
                    # player may try clicking on positon that has already been occupied, it's ineffective
                    flag = self.nextStep(nextTurnPlayer, posIndex)
                    if flag:
                        turnIndex += 1

                    # chech whether the game has ended/ one player has won the game
                    result = self.checkGameState(nextTurnPlayer)
                    if result:
                        self.over(result)

    def over(self,result):
        if result=='tie':
            resultImg = pygame.image.load('%s/tie.jpeg'%FiveInARow.imgPath)
        elif result==self.humanPlayerPieceType:
            resultImg = pygame.image.load('%s/youWin.jpeg'%FiveInARow.imgPath)
        else:
            resultImg = pygame.image.load('%s/youLose.jpeg'%FiveInARow.imgPath)

        speed = [0.5, 0.8]
        # black = 0, 0, 0
        resultImg=pygame.transform.scale(resultImg,(150,150))
        resultImgRect = resultImg.get_rect()

        # self.screen.blit(resultImg, (0, 0))
        pygame.display.flip()
        while 1:
            breakFlag = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                # If push space key, user can restart the game
                if event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_SPACE]==1:
                        breakFlag=True
                        break;
            if breakFlag:
                break;
            resultImgRect = resultImgRect.move(speed)
            if resultImgRect.left < 0 or resultImgRect.right > self.size[0]:
                speed[0] = -speed[0]
            if resultImgRect.top < 0 or resultImgRect.bottom > self.size[1]:
                speed[1] = -speed[1]

            self.screen.blit(resultImg, resultImgRect)
            pygame.display.flip()

        # restart the game
        self.refreshGame()

    def refreshGame(self):
        self.screen.blit(self.board, (0, 0))

        # bool matrix recording whether position is occupied
        self.boardStateMrx = [['null'] * FiveInARow.rowNum for i in range(FiveInARow.rowNum)]

        self.topLeftPos = [37, 37]
        self.cellLen = 52
        self.boardGridPointPosMrx = []
        for i in range(FiveInARow.rowNum):
            self.boardGridPointPosMrx.append([])
            for j in range(FiveInARow.columnNum):
                self.boardGridPointPosMrx[i].append([])

        for i in range(FiveInARow.rowNum):
            for j in range(FiveInARow.columnNum):
                self.boardGridPointPosMrx[i][j] = [self.topLeftPos[0] + self.cellLen * i,
                                                   self.topLeftPos[1] + self.cellLen * j]

        pygame.display.flip()

    def chooseGameMode(self):
        self.refreshGame()

        self.interface = pygame.image.load("%s/interface.png" % FiveInARow.imgPath)
        # self.board = pygame.transform.scale(self.board, (width, height))  # 转化大小
        self.interface_rect = self.interface.get_rect()
        self.screen.blit(self.interface, (0,0))
        pygame.display.flip()
        while 1:
            event = pygame.event.wait()
            if event.type==pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_d] == 1:
                    gameMode='DoublePlayer'
                    break;
                elif pygame.key.get_pressed()[pygame.K_s] == 1:
                    gameMode = 'SimpleAI'
                    break
                elif pygame.key.get_pressed()[pygame.K_b] == 1:
                    gameMode = 'ReinforcementAI'
                    break;

        self.screen.blit(self.board, (0, 0))
        pygame.display.flip()
        game.start(gameMode)

    def playMusic(self):
        pass
        # songList=os.listdir('sounds/')
        # songPath = 'sounds/%s' % songList[1]
        # pygame.mixer.music.load(songPath)
        # pygame.mixer.music.play(3)



if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')

    game=FiveInARow()
    game.start(None)

    # print(os.listdir('./'))







