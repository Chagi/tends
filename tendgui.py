import tkinter
import tends
import threading
import time

class Window(tkinter.Tk):

    def __init__(self, gameboard):
        super().__init__()
        
        draw_thread = threading.Thread(target = self.timed_draw)
        draw_thread.start()

        self.gameboard = gameboard

        self.hands = []
        self.boards = []

        self.handlists = [HandListy(self,[],0) , HandListy(self,[] , 1)]
        self.boardlists = [BoardListy(self,[],0) , BoardListy(self,[], 1)]

        self.lframe = tkinter.Frame(self)
        self.lframe.grid(row = 1, column = 0)

        att_button = tkinter.Button(self.lframe, text = "attack")
        att_button.pack(side = "left")
        att_button["command"] = self.att_b
        
        
        for pos, val in enumerate(self.boardlists):
            val.grid(row = pos*2, column = 0)
        for pos, val in enumerate(self.handlists):
            val.grid(row = pos*2, column = 1)
            
        self.updurp()

    def updurp(self):
        self.ready_attack = False
        self.hands = []
        self.boards = []
        for i in self.gameboard.players:
            self.hands += [i.hand.card_list]
            self.boards += [i.board.minions]

        for i in range(2):
            self.handlists[i].updurp(self.hands[i])
            self.boardlists[i].updurp(self.boards[i])

    def play(self, ply, index):
        
        self.gameboard.play_card(self.gameboard.players[ply],index)
        self.updurp()

    def attack(self, ply, index):
        if self.ready_attack:
            if ply != self.attacker[0]:
                g = self.gameboard
                attacker = self.attacker[0]
                index1 = self.attacker[1]
                g.attack(g.players[attacker], index1, index)
                g.check_deaths()
            else:
                self.ready_attack = False
        else:
            self.attacker = (ply, index)
        
        self.updurp()

    def att_b(self):
        self.ready_attack = True

    def timed_draw(self):
        while(True):
            time.sleep(10)
            for p in self.gameboard.players:
                p.draw()
            self.updurp()


class Listy(tkinter.Listbox):
    def __init__(self, window, lis, index):
        super().__init__(window, width = 40)
        self.updurp(lis)
        self.window = window
        self.index = index
        self.bind('<<ListboxSelect>>', self.select)

    def updurp(self,lis):
        self.delete(0, tkinter.END)
        for i in lis:
            self.insert(tkinter.END,i)

    def select(self, evt):
        index = self.curselection()[0]
        print(self.get(index))

class HandListy(Listy):
    def __init__(self, frame, lis, index):
        super().__init__(frame, lis, index)

    def select(self, evt):
        index = self.curselection()[0]
        self.window.play(self.index, index)

class BoardListy(Listy):
    def __init__(self, frame, lis, index):
        super().__init__(frame , lis, index)

    def select(self, evt):
        index = self.curselection()[0]
        self.window.attack(self.index, index)
        
a = Window(tends.gb)
a.mainloop()
