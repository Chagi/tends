import tkinter
import tends
import time


class Window(tkinter.Tk):

    def __init__(self, gameboard):
        super().__init__()
        
        self.gameboard = gameboard

        self.hands = []
        self.boards = []

        self.handlisty = [HandListy(self,[],0) , HandListy(self,[] , 1)]
        self.boardlisty = [BoardListy(self,[],0) , BoardListy(self,[], 1)]

        self.lframe = tkinter.Frame(self)
        self.lframe.grid(row = 1, column = 0)

        self.status_label = [None,None]
        self.status_label[0] = tkinter.Label(self.lframe, text = "mana: 0/0")
        self.status_label[0].pack(side = "left")

        att_button1 = tkinter.Button(self.lframe, text = "attack v")
        att_button1.pack(side = "left")
        att_button1["command"] = lambda: self.att_b(0)

        att_button2 = tkinter.Button(self.lframe, text = "attack ^")
        att_button2.pack(side = "left")
        att_button2["command"] = lambda: self.att_b(1)

        self.status_label[1] = tkinter.Label(self.lframe, text = "mana: 0/0")
        self.status_label[1].pack(side = "left")

        for pos, val in enumerate(self.boardlisty):
            val.grid(row = pos*2, column = 0)
        for pos, val in enumerate(self.handlisty):
            val.grid(row = pos*2, column = 1)

        self.updurp()
        self.after(1000, self.tick)
        #self.after(5000, self.timed_draw)

    def updurp(self):
        self.ready_attack = False
        self.hands = []
        self.boards = []
        for i in self.gameboard.players:
            self.hands += [i.hand.card_list]
            self.boards += [i.board.minions]

        for i in range(2):
            self.handlisty[i].updurp(self.hands[i])
            self.boardlisty[i].updurp(self.boards[i])
            p = self.gameboard.players[i]
            self.status_label[i]["text"] = f"mana: {p.mana[tends.Color.blue]}/{p.total_mana[tends.Color.blue]}"

        

    def play(self, ply, index):
        self.gameboard.play_card(self.gameboard.players[ply],index)
        self.gameboard.check_deaths()
        self.updurp()

    def att_b(self, attacker):
        g = self.gameboard
        index1 = self.boardlisty[attacker].curselection()[0]
        index2 = self.boardlisty[1-attacker].curselection()[0]
        g.attack(g.players[attacker], index1, index2 )

        self.updurp()

    def tick(self):
        self.gameboard.tick()
        self.updurp()
        self.after(1000,self.tick)
        
    def timed_draw(self):
        print("hej")
        for p in self.gameboard.players:
            #p.draw()
            #p.gain_total_mana()
            #p.mana = p.total_mana
            #p.mana = 100
            #print(p.mana)
            pass
        self.updurp()
        self.after(30000, self.timed_draw)

class Listy(tkinter.Listbox):
    def __init__(self, window, lis, index):
        super().__init__(window, width = 40)
        self["exportselection"] = False
        self.updurp(lis)
        self.window = window
        self.index = index
        self.bind('<<ListboxSelect>>', self.select)

    def updurp(self,lis):
        sel = self.curselection()
        index = sel[0] if len(sel) > 0 else None
        self.delete(0, tkinter.END)
        for i in lis:
            self.insert(tkinter.END,i)
        if index is not None and len(lis) > index:
            self.selection_set(index)

    def select(self, evt):
        index = self.curselection()[0]

class HandListy(Listy):
    def __init__(self, frame, lis, index):
        super().__init__(frame, lis, index)

    def select(self, evt):
        index = self.curselection()[0]
        self.window.play(self.index, index)

class BoardListy(Listy):
    def __init__(self, frame, lis, index):
        super().__init__(frame , lis, index)

        
        
a = Window(tends.gb)
a.mainloop()
