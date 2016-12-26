import random
import math
from enum import Enum

class Color(Enum):
    blue = 1
    red = 2
    green = 3
    pink = 4

class Stats:
    def __str__(self):
        return ("({}  {})").format(
            self.name , "  ".join(str(i) for i in self.get_stats()))

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


class TimeCounter:
    def __init__(self, time, auto_reset, func = lambda: None):
        self.start_time = time
        self.counter = time
        self.func = func
        self.auto_reset = auto_reset

    def tick(self):
        if self.counter > 0:
            self.counter -= 1
        else:
            self.func()
            if self.auto_reset:
                self.reset()

    def reset(self):
        self.counter = self.start_time

    def __str__(self):
        return str(self.counter)
        
        

class Effect:
    def __init__(self, function, trigger = None):
        self.func = function
        self.trigger = trigger

    def __eq__(self,other):
        return self.trigger == other.trigger

class Card(Stats):
    def __init__(self , name , mana, color, effects = ()):
        self.name = name
        self.mana = mana
        self.color = color
        self.effects = effects


    def add_effect(self, effect):
        self.effects = self.effects + (effect,)

    def trigger(self, name, args, kwargs):
        for eff in self.effects:
            if eff.trigger == name:
                eff.func(args[0], self, *args[1:], **kwargs)

    def get_stats(self):
        return (self.mana, self.color.name)

    

class MinionCard(Card):
    def __init__(self , name , mana , color , attack, health, rest_time, effects = ()):
        super().__init__(name, mana, color , effects)
        self.attack = attack
        self.health = health
        self.rest_time = rest_time
        

    def get_stats(self):
        eff = None if len(self.effects) == 0 else self.effects[0].trigger
        return (self.mana , (self.attack, self.health, self.rest_time) )#, self.color.name, eff)


class Minion(Stats):
    @hierarchy_dec
    def __init__(self, card):
        self.card = card
        self.name = self.card.name
        self.attack = self.card.attack
        self.health = self.card.health
        self.rest_timer = TimeCounter(self.card.rest_time, False)
        #print(self.parents)
        
    def rest(self):
        self.rest_timer.reset()
        
    def attack_minion(self, other):
        #self.health -= other.attack
        if self.rest_timer.counter <= 0:
            print("attack!")
            other.health -= self.attack
            self.rest()
        else: print("attak fial")

    def damage(self, dam):
        self.health -= dam

    def heal(self, health):
        self.health = min(self.card.health, self.health + health)


    def tick(self):
        self.rest_timer.tick()
            

    def trigger(self, name, args, kwargs):
        for eff in self.card.effects:
            if eff.trigger == name:
                eff.func(self.parents["Player"], *args, **kwargs)
    
    
    def get_stats(self):
        return (self.attack, self.health, self.rest_timer.counter)
        


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
        dead.reverse()
        for i in dead:
            ret += [self.minions.pop(i)]
        return tuple(ret)

    def tick(self):
        for minion in self.minions:
            minion.tick()
            

    def __str__(self):
        ret = "Minion\t\tAttack\tHealth\n"
        return ret + "\n".join((str(i) for i in self.minions))

class Player:
    @hierarchy_dec
    def __init__(self , deck):
        self.deck = deck
        self.hand = Hand(parent = self)
        self.board = PlayerBoard(parent = self)

        self.mana = {Color.blue: 0, Color.red: 0, Color.green: 0, Color.pink: 0}
        self.total_mana = {Color.blue: 0, Color.red: 0, Color.green: 0, Color.pink: 0}
        self.mana_counter = {Color.blue: 10, Color.red: 10, Color.green: 10, Color.pink: 10}
        self.mana_level = {Color.blue: 1, Color.red: 1, Color.green: 1, Color.pink: 1}
        
##        self.total_mana = 1
##        self.mana_time = 10
##        self.mana_counter = 10
##        self.mana = 1


    def check_deaths(self):
        return self.board.check_deaths()

    def tick(self):
        
        for key in self.mana_counter:
            self.mana_counter[key] -= 1
            if self.mana_counter[key] <= 0:
                self.mana_counter[key] = 10/(self.mana_level[key])
                self.mana[key] = self.mana[key]+1
        self.board.tick()

    @trigger_dec
    def draw(self, index = 0):
        self.hand.add_card(self.deck.pop(index))

    @trigger_dec
    def attack(self, other, index1, index2):
        self.board.attack(other.board, index1, index2)

    @trigger_dec
    def play_card(self, index):
        card = self.hand.card_list[index]
        if card.mana > self.mana[card.color]:
            print('manaaaa')
            return
        card = self.hand.pop(index)
        gameboard = self.parents["GameBoard"]

        self.mana[card.color] -= card.mana
        self.mana_level[card.color] += 1
        card.trigger("on_play", [self], {})
        
        if isinstance(card, MinionCard):
            minion = Minion(card, parent = self)
            self.board.add_minion(minion)
            for i in card.effects:
                gameboard.effects[i.trigger] = [minion]
            #print(gb.effects)

    def gain_total_mana(self, amount = 1):
        self.total_mana += amount




class GameBoard:
    def __init__(self):
        self.parents = {}
        self.players = ( Player(gen_deck(), parent = self), Player(gen_deck(), parent = self) )

        self.curr_player, self.other_player = self.players
        
        self.effects = {} # name : list of minions

        self.draw_timer = TimeCounter(15, True, self.new_turn)


    def initialize(self):
        for i in range(5):
            for p in self.players:
                p.draw()

    def check_deaths(self):
        return (self.players[0].check_deaths() , self.players[1].check_deaths())

    def tick(self):
        self.draw_timer.tick()
        for p in self.players:
            p.tick()

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
        #self.initialize()
        
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
        self.curr_player.gain_total_mana()
        self.curr_player.mana = self.curr_player.total_mana

    @trigger_dec
    def end_turn(self):
        self.curr_player, self.other_player = self.other_player, self.curr_player

    def play_card(self, player, index):
        player.play_card(index)
 
    def attack(self, attacker, index1, index2):
        attacker.attack(self.other_p(attacker), index1 , index2)
        self.check_deaths()

    def other_p(self, player):
        return self.other_player if player is self.curr_player else self.curr_player

    def new_turn(self):
        for p in self.players:
            #p.gain_total_mana()
            p.draw()
        
    def __str__(self):
        ret = "---------------------\nBoard: \n"
        ret += str(self.curr_player.board) + "\n\n"
        ret += str(self.other_player.board) + "\n\n"
        ret += "Mana: " + str(self.curr_player.mana) + "\n"
        ret += "Hand: \n"
        ret += str(self.curr_player.hand)
        return ret
        
        

def gen_deck(): 
    names = ["koopa", "goomba", "zoomer", "octorock", "waddle doo" , "kremling" , "ridley"]
    cartas = []
    for pos, val in enumerate(names):
        cartas.append( MinionCard(val, pos+1, Color.blue, pos+1, (pos+1)*2, (pos+1)*2 ) )

    eff = Effect(test_effect, "on_play")
    eff2 = Effect(test2, "on_play")
    cartas[1].add_effect(eff)
    cartas[3].add_effect(eff2)
    
    deck1 = Deck()

    for i in range(30):
        deck1.add_card(cartas[int(i**1.3/12)])

    return deck1

def test_effect(owner, card):
    gameboard = owner.parents["GameBoard"]
    for minion in gameboard.other_p(owner).board.minions:
        minion.damage(1)

def test2(owner, card):
    gameboard = owner.parents["GameBoard"]
    for minion in owner.board.minions:
        #minion.trigger('on_play' , (minion.card,) , {})
        minion.heal(2)
        
gb = GameBoard()
gb.initialize()
#gb.run()
    
