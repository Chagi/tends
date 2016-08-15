import random

class Stats:
    def __str__(self):
        tabs = "\t"*((23 - len(self.name))//8)
        return ("({}"+tabs+"{})").format(
            self.name , "\t".join(str(i) for i in self.get_stats()))

class TriggerData:
    def __init__(self, name, args, kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs


def trigger_dec(f):
    name = f.__name__
    def wrapper(*args, **kwargs):
        self = args[0]
        ret = f(*args,**kwargs)
        if isinstance(self,GameBoard):
            gameboard = self
        else:
            gameboard = self.parents["GameBoard"]
        gameboard.trigger( TriggerData(name, args, kwargs) )
        return ret
    return wrapper

def hierarchy_dec(f):
    def wrapper(*args , parent = None , **kwargs):
        if parent is not None:
            self = args[0]
            self.parents = parent.parents.copy()
            self.parents[parent.__class__.__name__] = parent
        f(*args, **kwargs)
    return wrapper

        
        

class Effect:
    def __init__(self, function, trigger = None):
        self.func = function
        self.trigger = trigger

    def __eq__(self,other):
        return self.trigger == other.trigger

class Card(Stats):
    def __init__(self , name , mana, effects = ()):
        self.name = name
        self.mana = mana
        self.effects = effects


    def add_effect(self, effect):
        self.effects = self.effects + (effect,)

    def trigger(self, name, args, kwargs):
        for eff in self.effects:
            if eff.trigger == name:
                eff.func(args[0], self, *args[1:], **kwargs)

    def get_stats(self):
        return (self.mana)

    

class MinionCard(Card):
    def __init__(self , name , mana , attack, health, effects = ()):
        super().__init__(name, mana, effects)
        self.attack = attack
        self.health = health
        

    def get_stats(self):
        eff = None if len(self.effects) == 0 else self.effects[0].trigger
        return (self.mana , (self.attack, self.health) , eff)


class Minion(Stats):
    @hierarchy_dec
    def __init__(self, card):
        self.card = card
        self.name = self.card.name
        self.attack = self.card.attack
        self.health = self.card.health

        #print(self.parents)

    def attack_minion(self, other):
        #self.health -= other.attack
        other.health -= self.attack

    def damage(self, dam):
        self.health -= dam

    def trigger(self, name, args, kwargs):
        for eff in self.card.effects:
            if eff.trigger == name:
                eff.func(self.parents["Player"], *args, **kwargs)
    
    
    def get_stats(self):
        return (self.attack, self.health)
        


class CardContainer:
    @hierarchy_dec
    def __init__(self, cards = []):
        for i in cards:
            if not isinstance(i,Card):
                raise TypeError("not card")

        self.card_list = cards[::]
        
    def add_card(self, card, index = None):
        if not isinstance(card, Card):
            raise TypeError("not carde")
        if index is None:
            index = self.default_index()
        self.card_list.insert(index , card)

        return self.add_card_trigger
        
    def pop(self, index = 0):
        return self.card_list.pop(index)

    def __str__(self):
        ret = "Card\t\tMana\tStats\tEffecs\n"
        return ret + "\n".join((str(i) for i in self.card_list))

class Deck(CardContainer):
    add_card_trigger = "draw_deck"
    def default_index(self):
        return random.randint( 0 , len(self.card_list) )
    

class Hand(CardContainer):
    add_card_trigger = "play_card"
    
    def default_index(self):
        return len(self.card_list)


class PlayerBoard:
    @hierarchy_dec
    def __init__(self):
        self.minions = []

    @trigger_dec
    def add_minion(self, minion):
        if not isinstance(minion, Minion):
            raise TypeError("not minion!!")
        self.minions.append(minion)

    def attack(self, other, index1, index2):
        self.minions[index1].attack_minion(other.minions[index2])

    def check_deaths(self):
        dead = []
        ret = []
        for i in range(len(self.minions)):
            if self.minions[i].health <= 0:
                dead.append(i)
        dead.reverse
        for i in dead:
            ret += [self.minions.pop(i)]
        return tuple(ret)
            

    def __str__(self):
        ret = "Minion\t\tAttack\tHealth\n"
        return ret + "\n".join((str(i) for i in self.minions))

class Player:
    @hierarchy_dec
    def __init__(self , deck):
        self.deck = deck
        self.hand = Hand(parent = self)
        self.board = PlayerBoard(parent = self)

        

    def check_deaths(self):
        return self.board.check_deaths()

    @trigger_dec
    def draw(self, index = 0):
        self.hand.add_card(self.deck.pop(index))

    @trigger_dec
    def attack(self, other, index1, index2):
        self.board.attack(other.board, index1, index2)

    @trigger_dec
    def play_card(self, index):
        card = self.hand.pop(index)
        gameboard = self.parents["GameBoard"]

        card.trigger("on_play", [self], {})
        
        if isinstance(card, MinionCard):
            minion = Minion(card, parent = self)
            self.board.add_minion(minion)
            for i in card.effects:
                gameboard.effects[i.trigger] = [minion]
            #print(gb.effects)






class GameBoard:
    def __init__(self):
        self.parents = {}
        self.players = ( Player(gen_deck(), parent = self), Player(gen_deck(), parent = self) )

        self.curr_player, self.other_player = self.players
        
        self.effects = {} # name : list of minions


    def initialize(self):
        for i in range(5):
            for p in self.players:
                p.draw()

    def check_deaths(self):
        return (self.players[0].check_deaths() , self.players[1].check_deaths())

    def trigger(self, data):
        for minion in self.curr_player.board.minions + self.other_player.board.minions:
            minion.trigger(data.name, data.args, data.kwargs)
    
    def trigger2(self, data):
        try:
            minions = self.effects[data.name]
        except(KeyError):
            pass
            #print("fauil")
        else:
            #print("success")
            for minion in minions:
                for effect in minion.card.effects:
                    if effect.trigger == data.name:
                        effect.func(minion.parents["Player"], *data.args, **data.kwargs )
                        self.check_deaths()

    def run(self):
        self.initialize()
        
        inp = ""
        while inp != "quit":
            self.start_turn()
            inp = ""
            
            while inp != "pass" and inp != "quit":
                print(self)
                inp = input("action:\n")
                if inp == "att":
                    self.attack(self.curr_player , int(input()), int(input()))
                if inp == "play":
                    self.play_card(self.curr_player , int(input()))
                self.check_deaths()
            
            self.end_turn()

    @trigger_dec
    def start_turn(self):
        self.curr_player.draw()

    @trigger_dec
    def end_turn(self):
        self.curr_player, self.other_player = self.other_player, self.curr_player

    def play_card(self, player, index):
        player.play_card(index)
 
    def attack(self, attacker, index1, index2):
        attacker.attack(self.other_p(attacker), index1 , index2)

    def other_p(self, player):
        return self.other_player if player is self.curr_player else self.curr_player
        
    def __str__(self):
        ret = "---------------------\nBoard: \n"
        ret += str(self.curr_player.board) + "\n\n"
        ret += str(self.other_player.board) + "\n\n"
        ret += "Hand: \n"
        ret += str(self.curr_player.hand)
        return ret
        
        

def gen_deck(): 
    names = ["koopa", "goomba", "zoomer", "octorock"]
    cartas = []
    for pos, val in enumerate(names):
        cartas.append( MinionCard(val, pos+1, pos+1, pos+2) )

    eff = Effect(test_effect, "on_play")
    cartas[1].add_effect(eff)
    
    deck1 = Deck()

    for i in range(30):
        deck1.add_card(cartas[i%4])

    return deck1

def test_effect(owner, card):
    gameboard = owner.parents["GameBoard"]
    for minion in gameboard.other_p(owner).board.minions:
        minion.damage(1)

    
gb = GameBoard()
gb.initialize()
#gb.run()
    
