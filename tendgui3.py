import tkinter
import tends

class Window(tkinter.Toplevel):
    def __init__(self, gameboard, player, opponent):
        super().__init__()
        self.board = Board(self, gameboard, player, opponent)
        self.board.pack()

class MainWindow(tkinter.Tk):
    def __init__(self, gameboard):
        super().__init__()
        self.gameboard = gameboard
        p = gameboard.curr_player
        p2 = gameboard.other_player

        self.window1 = Window(gameboard, p , p2)
        self.window2 = Window(gameboard, p2 , p)
        
        self.after(1000, self.tick)

    def tick(self):
        self.gameboard.tick()
        self.window1.board.updurp()
        self.window2.board.updurp()
        self.after(1000, self.tick)
        
        


class Board(tkinter.Canvas):
    def __init__(self, parent, gameboard, player, opponent):
        super().__init__(parent, width = 800, height = 800)
        self.size = (800,800)
        self.bind("<Button-1>", self.on_click)
        self.parent = parent

        self.gameboard = gameboard
        self.player = player
        self.opponent = opponent
       # player.mana[tends.Color.blue] = 100
        
        self.cards = []
        self.monsters = []
        self.op_monsters = []
        self.attacker_index = None
        
        self.updurp()
        #self.parent.after(1000,self.tick)

    def tick(self):
        self.gameboard.tick()
        self.updurp()
        self.parent.after(1000,self.tick)

    def updurp(self):
        self.delete("all")
        self.cards = []
        self.monsters = []
        self.op_monsters = []

        self.create_text(200, 420, text = f"mana: {self.player.mana[tends.Color.blue]}", anchor = "w")
        
        for pos, val in enumerate(self.player.hand.card_list):
            self.cards.append(Card(self, pos, val))
            #print("card")

        for pos, val in enumerate(self.player.board.minions):
            self.monsters.append(Monster(self, pos, val))
            #print("monst")

        for pos, val in enumerate(self.opponent.board.minions):
            self.monsters.append(Monster(self, pos, val, True))
            #print("emeni")

    def on_click(self, event):
        if (event.x - 10) % 100 > 90: return

        index = (event.x - 10)//100
        
        if 50 < event.y < 190:
            lis = self.op_monsters
            if self.attacker_index is not None:
                self.gameboard.attack(self.player,self.attacker_index,index)
        elif 200 < event.y < 340:
            lis = self.monsters
            self.attacker_index = index
        elif 500 < event.y < 650:
            lis = self.cards
            self.gameboard.play_card(self.player, index)
        else:
            return

        
        print(lis,index)
        self.updurp()

class Card:
    def __init__(self, parent, pos, card):
        self.card = card
        parent.create_rectangle(pos*100 + 10 , 500, pos*100 + 100, 650 )
        parent.create_text(pos*100 + 20, 550, text= card.name, anchor = "w")
        parent.create_text(pos*100 + 20, 600, text= card.get_stats(), anchor = "w")
    
        

class Monster:
    def __init__(self, parent, pos, monster, opponent = False):
        self.monster = monster
        if opponent:
            y = 50
        else:
            y = 200
        self.oval = parent.create_oval(pos*100 + 10, y, pos*100 + 100, y+140 )
        parent.create_text(pos*100 + 20, y+50, text= monster.name, anchor = "w")
        parent.create_text(pos*100 + 20, y+100, text= monster.get_stats(), anchor = "w")

        self.parent = parent
        self.pos = pos
        self.y = y

    def attack(self, index): pass


    def move(self, direction, n):
        self.parent.coords(self.oval)

gb = tends.gb

window = MainWindow(gb)
window.mainloop()
