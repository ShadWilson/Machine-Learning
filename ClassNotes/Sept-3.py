import sys

class Gameboard:
    def __init__(self):
        self.entires = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.state = 0
        #state 0 = game playing
        #state 1 = player 1 wins
        #state 2 = player 2 wins
        #state 3 = draw

    def print(self):
        for i in range(3):
            for j in range(3):
                print(self.entires[i][j], end='')
            print('')



    def checkwin(self) -> int:
        
        return 0
    
gb = Gameboard
gb.print