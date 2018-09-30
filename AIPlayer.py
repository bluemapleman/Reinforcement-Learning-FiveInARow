#encoding=utf-8
#Author: Tom Qian  
#Email: TomQianMaple@outlook.com
import abc #利用abc模块实现抽象类
import random
import tensorflow as tf

class AIPlayer:
    @staticmethod
    def newAIPlayer(type,pieceType):
        if type=='FollowYouPlayer':
            return FollowYouPlayer(pieceType)
        else:
            return None;



    def __init__(self,pieceType):
        self.pieceType=pieceType
        pieceTypeList=['white','black']
        pieceTypeList.remove(self.pieceType)
        self.adversarialPieceType=pieceTypeList[0]

        # Detect these mode first, if find any, then AI win for sure
        self.mustMode=['XXOXX','XXXOX','XOXXX','XXXXO','OXXXX',['.X...','.X...','XOX_X','.X...','.X...']]
        # Must caution following mode, and take relevant actions when finding any of them
        self.cautionMode=['_OXXX_','_XXXO_','_XXOX_','_XOXX_',
                          ['...._','XXXO_','..X..','.X...','X....'],['...._','XXXO_','..X..','.X...','_....'],
                          ['..._.','XXXO_','...X.','...X.','..._.'],['X...X','X..X.','X.X..','__...','O....'],
                          ['X....','X....','X....','_....','O_XXX'],['._....','_O_XX_','.X....','.X....','._....']]
        # , ['_.....', '_O_XX_', '..X...', '...X..', '...._.']
        # Useful Mode, normally two in a row without any stop
        self.usefulMode=['_XXO_','_OXX_','XXXOO','OOXXX','XXOXO','OXOXX','_XOX_','_XOOX_',
                         ['._...','_OXX_','.X...','.X...','._...'],['..._.','XXXO_','...X.','...X.','...X.'],
                         ['_._..','.XX..','..O..','..XX.','.._._'],['.O.','XXX','.O.']]

    @abc.abstractmethod
    def nextAction(self,boardStateMrx):
        pass;


    # Notice: XX.XX is also considered 4-in-a-row, X.XX or XX.X is also considered 3-in-a-row
    # All in a word, as long as for five consecutive positions, if there are N positions occupied, then this can be considered as a N-in-a-row situation.
    def detectNInARow(self,N,pieceType,boardStateMrx):
        # element format: (direction,(N point positions))
        NRowList=[]

        rowNum=len(boardStateMrx)
        columnNum=len(boardStateMrx[0])
        # right
        for i in range(rowNum):
            for j in range(columnNum):
                if boardStateMrx[i][j]==pieceType:
                    directionList = ['right', 'down', 'down-left', 'down-right']
                    for direction in directionList:
                        count = 0
                        tempx = i
                        tempy = j

                        temp=0
                        # pieceTuple=(,)
                        while tempx < rowNum and tempx >=0 and tempy < columnNum and tempy>=0:
                            temp+=1
                            if boardStateMrx[tempx][tempy] == pieceType:
                                count += 1

                            if temp==5:
                                # Find N-in-a-row
                                if count==N:
                                    NRowList.append((direction,[i, j]))
                                break

                            if direction == 'down':
                                tempy += 1
                            elif direction == 'right':
                                tempx += 1
                            elif direction == 'down-left':
                                tempx -= 1
                                tempy += 1
                            elif direction == 'down-right':
                                tempx += 1
                                tempy += 1
        if NRowList:
            return NRowList
        else:
            return False


    def getChoosablePosi(self,NRowList,boardStateMrx,N):
        for rowList in NRowList:
            direction = rowList[0]
            firstPoint = rowList[1]

            # Step back first, then see if the first two slots are filled
            # if not, fill one
            # if so, go on
            x,y=self.getNextDirectionPos(firstPoint,'reverse-%s'%direction)
            if x>=0 and x<len(boardStateMrx) and y>=0 and y<len(boardStateMrx):
                tempPoint=(x,y)
            else:
                tempPoint=firstPoint

            tempx,tempy=tempPoint
            detectStep=N+2
            slot=[]
            for i in range(detectStep):
                if tempx>=0 and tempx<len(boardStateMrx) and tempy>=0 and tempy<len(boardStateMrx):
                    if boardStateMrx[tempx][tempy]=='null':
                        slot.append([tempx,tempy])

                nextPos=self.getNextDirectionPos((tempx,tempy),direction)

                tempx,tempy=nextPos

            if len(slot)==N-1:
                return slot[1]


        return None

    def getNextDirectionPos(self,startPos,direction):
        x,y=startPos
        directionMap={}
        directionMap['right']=(1,0)
        directionMap['reverse-right'] = (-1, 0)
        directionMap['down'] = (0, 1)
        directionMap['reverse-down'] = (0, -1)
        directionMap['down-left'] = (-1, 1)
        directionMap['reverse-down-left'] = (1, -1)
        directionMap['down-right'] = (1, 1)
        directionMap['reverse-down-right'] = (-1, -1)

        x += directionMap[direction][0]
        y += directionMap[direction][1]

        return (x,y)

    def detectMode(self,boardStateMrx,pieceType,modeList):
        for mode in modeList:
            for i in range(len(boardStateMrx)):
                for j in range(len(boardStateMrx)):
                    for direction in ['right','down','down-left','down-right']:
                        if self.fitMode(mode,boardStateMrx,(i,j),direction,pieceType):
                            if isinstance(mode,list):
                                print('find complicated mode：')
                                print(mode)
                                print((i,j))
                                print(direction)

                            return (mode,(i,j),direction)

        return None



    def fitMode(self,mode,boardStateMrx,startPoint,direction,pieceType):
        # A 2d mode
        if isinstance(mode,list):
            if direction=='right':
                turnDirection='down'
            elif direction=='down':
                turnDirection = 'reverse-right'
            elif direction=='down-left':
                turnDirection = 'down-right'
            elif direction=='down-right':
                turnDirection = 'reverse-down-left'

            for modeLine in mode:
                tempx, tempy = startPoint
                for i in range(len(modeLine)):
                    modeChar = modeLine[i]
                    if modeChar == '_' or modeChar=='O':
                        if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                            if boardStateMrx[tempx][tempy] != 'null':
                                return False;
                        else:
                            return False
                    elif modeChar == 'X':
                        if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                            if boardStateMrx[tempx][tempy] != pieceType:
                                return False;
                        else:
                            return False

                    tempx, tempy = self.getNextDirectionPos((tempx, tempy), direction)
                startPoint=self.getNextDirectionPos(startPoint,turnDirection)
                tempx,tempy=startPoint
        else:
            tempx,tempy=startPoint
            for i in range(len(mode)):
                modeChar=mode[i]
                if modeChar=='_' or modeChar=='O':
                    if tempx>=0 and tempx<len(boardStateMrx) and tempy>=0 and tempy<len(boardStateMrx):
                        if boardStateMrx[tempx][tempy] != 'null':
                            return False;
                    else:
                        return False
                elif modeChar=='X':
                    if tempx>=0 and tempx<len(boardStateMrx) and tempy>=0 and tempy<len(boardStateMrx):
                        if boardStateMrx[tempx][tempy] != pieceType:
                            return False;
                    else:
                        return False

                tempx,tempy=self.getNextDirectionPos((tempx,tempy),direction)

        return True

    def getChoosablePosi(self, NRowList, boardStateMrx, N):
        for rowList in NRowList:
            direction = rowList[0]
            firstPoint = rowList[1]

            # Step back first, then see if the first two slots are filled
            # if not, fill one
            # if so, go on
            x, y = self.getNextDirectionPos(firstPoint, 'reverse-%s' % direction)
            if x >= 0 and x < len(boardStateMrx) and y >= 0 and y < len(boardStateMrx):
                tempPoint = (x, y)
            else:
                tempPoint = firstPoint

            tempx, tempy = tempPoint
            detectStep = N + 2
            slot = []
            for i in range(detectStep):
                if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                    if boardStateMrx[tempx][tempy] == 'null':
                        slot.append([tempx, tempy])

                nextPos = self.getNextDirectionPos((tempx, tempy), direction)

                tempx, tempy = nextPos
            if len(slot) == N - 1:
                return slot[1]

        return None







class FollowYouPlayer(AIPlayer):
    def nextAction(self,boardStateMrx,adverasialLastPosi):

        # Must win
        selfResult= self.detectMode(boardStateMrx,self.pieceType,self.mustMode)
        action = self.__reactToMode(selfResult)
        if action:
            print('%s:must win' % self.pieceType)
            return random.choice(action)

        # Must stop
        adversarialResult = self.detectMode(boardStateMrx,self.adversarialPieceType,self.mustMode)
        action = self.__reactToMode(adversarialResult)
        if action:
            print('%s:must stop' % self.pieceType)
            return random.choice(action)

        # Could try to win
        selfResult = self.detectMode(boardStateMrx, self.pieceType, self.cautionMode)
        action = self.__reactToMode(selfResult)
        if action:
            print('%s:try to win' % self.pieceType)
            return random.choice(action)

        # need try to stop
        adversarialResult = self.detectMode(boardStateMrx, self.adversarialPieceType, self.cautionMode)
        action=self.__reactToMode(adversarialResult)
        if action:
            print('%s:try to stop'%self.pieceType)
            return random.choice(action)


        # try to extend
        selfResult = self.detectMode(boardStateMrx, self.pieceType, self.usefulMode)
        action=self.__reactToMode(selfResult)
        if action:
            print('%s:try to extend'%self.pieceType)
            return random.choice(action)

        print('%s:randomChoice'%self.pieceType)

        return self.randomAction(boardStateMrx,adverasialLastPosi)

    def __reactToMode(self,modeDetectResult):
        actionList=[]
        if modeDetectResult:
            mode = modeDetectResult[0]
            firstPoint = modeDetectResult[1]
            x,y=firstPoint
            direction = modeDetectResult[2]
            if isinstance(mode,list):
                print('find complicated mode!')

                if direction == 'right':
                    turnDirection = 'down'
                elif direction == 'down':
                    turnDirection = 'reverse-right'
                elif direction == 'down-left':
                    turnDirection = 'down-right'
                elif direction == 'down-right':
                    turnDirection = 'reverse-down-left'

                for modeLine in mode:
                    for char in modeLine:
                        if char == 'O':
                            actionList.append((x,y))
                            # return (x, y)
                        else:
                            x, y = self.getNextDirectionPos((x, y), direction)
                    firstPoint=self.getNextDirectionPos(firstPoint,turnDirection)
                    x,y=firstPoint
            else:
                for char in mode:
                    if char == 'O':
                        actionList.append((x, y))
                        # return (x, y)
                    else:
                        x, y = self.getNextDirectionPos((x, y), direction)

        return actionList


    # random choose a position that is near the adverasialLastAction to occupy
    def randomAction(self, boardStateMrx, adverasialLastPosi):
        # First move
        if not adverasialLastPosi:
            return (len(boardStateMrx)//2,len(boardStateMrx)//2)

        occupiablePosiList = []
        x, y = adverasialLastPosi
        if x - 1 >= 0 and boardStateMrx[x - 1][y] == 'null':
            occupiablePosiList.append((x - 1, y))
        if x + 1 < len(boardStateMrx) and boardStateMrx[x + 1][y] == 'null':
            occupiablePosiList.append((x + 1, y))
        if y - 1 >= 0 and boardStateMrx[x][y - 1] == 'null':
            occupiablePosiList.append((x, y - 1))
        if y + 1 < len(boardStateMrx[0]) and boardStateMrx[x][y + 1] == 'null':
            occupiablePosiList.append((x, y + 1))

        if occupiablePosiList:
            nextPos = random.choice(occupiablePosiList)
        else:
            nextPos=self.getRandomPosiOnBoard(boardStateMrx)

        return nextPos

    def getRandomPosiOnBoard(self,boardStateMrx):
        x = random.randint(0,len(boardStateMrx)-1)
        y = random.randint(0,len(boardStateMrx)-1)
        while boardStateMrx[x][y]!='null':
            x = random.randint(0, len(boardStateMrx)-1)
            y = random.randint(0, len(boardStateMrx)-1)

        return (x,y)




class NaivePlayer(AIPlayer):
    def judge(self,boardStateMrx):
        pass
    def nextAction(self,boardStateMrx):
        pass

class miniMaxPlayer(AIPlayer):
    def nextAction(self, boardStateMrx):
        pass;

class RLPlayer(AIPlayer):
    def evaluationState(self, boardStateMrx, pieceType):
        width,height=len(boardStateMrx),len(boardStateMrx)
        from keras.models import Sequential
        from keras.layers import Dense, Activation

        # NN that
        nextMoveNetwork = Sequential([
            Dense(32, input_shape=(width*height,)),
            Activation('relu'),
            Dense(width*height),
            Activation('softmax'),
        ])

        winnerNetwork=Sequential([
            Dense(32, input_shape=(width*height,)),
            Activation('relu'),
            Dense(1),
            Activation('softmax'),
        ])



    def nextAction(self, boardStateMrx):
        pass;
