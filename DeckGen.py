import random
import copy

suits = ("C", "D", "S", "H")
numbers = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "t": 10, "J": 10, "Q": 10, "K": 10}
bjPays = 2.5
def dealer_space(dealscore, cardsleft, workvals):
    """
    this will define what states the dealer can be in after it plays through as it would a hit on soft 17 (insurence is
    not accounted for)
    :param dealscore: this is andtuple of the form (int, bool) that is the score of the faceup card that the dealer has
    and the bool describes if there is an ace counting for 11
    :param cardsleft: this is a int that is how many cards in the
    :param workvals:
    :return:
    """
    odds = 1
    queue = [(dealscore, cardsleft, workvals, odds)]
    dealposs = {}
    while queue:

        dealscore, cardsleft, workvals, odds = queue.pop()
        for value in workvals:
            soft = dealscore[1]
            succdeckvals = copy.deepcopy(workvals)
            succdeckvals[value] -= 1
            nvalue = value
            if value == 11:
                if  dealscore[0] > 10:
                    nvalue = 1
                if dealscore[0] <= 10:
                    dealscore = list(dealscore)
                    dealscore[1] = True
                    dealscore = tuple(dealscore)
            succodds = float(workvals[value] / cardsleft) * odds
            # print("dealscore",dealscore)
            nscore = nvalue + dealscore[0]
            if nscore > 21 and soft:
                succscore = (nscore - 10, False)
            else:
                succscore = (nscore, soft)
            if succscore[0] > 17 or (succscore[0] == 17 and not succscore[1]):  # terminating step
                # dealer ends here
                if nscore > 21:
                    nscore = 0
                state = makescoredeckhashable(nscore, succdeckvals)
                if state not in dealposs:
                    dealposs[state] = succodds
                    continue
                dealposs[state] += succodds
                continue
            succcardscnt = cardsleft - 1
            queue.append(((nscore, soft), succcardscnt, succdeckvals, succodds))
    ####################################
    # end dealer option
    ####################################
    return dealposs

def makescoredeckhashable(score, deck):
    """
    this is going to be used so tyhat we can make the cards left in the deck and the dealer scores hashable kjso that
    we can use them for a dictionary key
    :param score: this is an int that is associated describes the dealers score
    :param deck: this is a dictionary that looks like Deck.valuesleft that describes what cards would be left in the
    deck after the dealer has reached the score that it has
    :return: a tuple of the form (int,...*10) where the first int is the s core and the subsequent ones are the cards of
     each value left in the deck
    """
    retlist = [score]
    for iii in range(2,12):
        retlist.append(deck[iii])
    return tuple(retlist)

def getscoreanddeckfromhashable(hashable):
    """
    this is an inverse of the makescoredeckhashable function it basically will work
    :param hashable:
    :return: a tuple of the form (int ,{int:int,...}) where the first element refers toi the score that dealer has and
    the disctionary is a dictionary of
    """
    deck = {}
    for iii in range(2, 12):
        deck[iii] = hashable[iii-1]
    return hashable[0], deck


def gendeck():
    """
    this will output a list of card objects that typically appear in standard 52 card decks
    :return:
    """
    deck = []
    for suit in suits:
        for number in numbers:
            deck.append(Card(suit, number))
    return deck


class Card:
    def __init__(self, suit, number):
        if suit not in suits or number not in numbers:
            raise TypeError("card not available in this space")
        self.name = number + suit
        self.number = number
        self.suit = suit
        self.value = numbers[self.number]

    def __str__(self):
        return self.name


class Deck:
    def __init__(self,numdecks):
        if not isinstance(numdecks, (int,float)):
            raise TypeError("you need a non complex number for number of decks")
        self.cardlist =[]
        for iii in range(0, numdecks):      #need each card to be an individual object here instead of duplicates
            self.cardlist += gendeck()
        random.shuffle(self.cardlist)
        self.cardlist = tuple(self.cardlist)
        self.cardsleft = len(self.cardlist)
        self.valuesleft = {2: 4 * numdecks, 3: 4 * numdecks, 4: 4 * numdecks, 5: 4 * numdecks, 6: 4 * numdecks,
                           7: 4 * numdecks, 8: 4 * numdecks, 9: 4 * numdecks, 10: 16 * numdecks, 11: 4 * numdecks}

    def draw(self):
        temp = list(self.cardlist)
        card = temp.pop()
        self.cardlist = tuple(temp)
        self.valuesleft[card.value] -= 1
        self.cardsleft -= 1
        return card

class Dealer:
    def __init__(self, deck):
        self.deck = deck
        self.faceup = deck.draw()
        self.cards = (self.faceup,)
        self.total = self.faceup.value

    def __str__(self):
        print(", ".join(self.cards))
        #return str(self.facedown) + ", " + str(self.faceup) + " " + str(self.total)

    def hit(self):
        newcard = self.deck.draw()
        self.cards = tuple(list(self.cards) + [newcard])
        self.total += newcard.value
        if self.total > 21:
            for card in self.cards:
                if card.value == 11:
                    card.value = 1
                    self.total -= 10
        return self.total

    def stay(self):
        return False

    def play(self):
        """
        this plays through all dealer choices in a row. it assumes that you hit to 16 and on soft 17 and stand otherwise
        :return:
        """
        self.hit()          #this simulates the face down card.
        alive = True
        while alive:
            if self.total > 17:
                alive = bool(self.stay())
                continue
            elif self.total < 17:
                alive = bool(self.hit())
                continue
            elif self.total == 17:
                for card in self.cards:
                    if card.value == 11:
                        alive = bool(self.hit())
                        continue
                alive = self.stay()
        printstring = ""
        for card in self.cards:
            printstring += " " + str(card)
        print(printstring, self.total)

class Player:
    def __init__(self, deck, dealer, card1=False, card2=False):
        self.deck = deck
        self.dealer = dealer
        if not card1:
            card1 = self.deck.draw()
        if not card2:
            card2 = self.deck.draw()
        self.cards = (card1, card2)
        self.total = self.cards[0].value + self.cards[1].value - \
                     10*int(self.cards[0].value == 11 and self.cards[1].value == 11)
        self.blackjack = not self.total - 21


    def getstatespace(self):
        dealer = self.dealer
        dealscore = (dealer.cards[0].value, not dealer.cards[0].value - 11)
        workvals = copy.deepcopy(self.deck.valuesleft)
        cardsleft = self.deck.cardsleft
        self.dealposs = dealer_space(dealscore, cardsleft, workvals)

    def stayodds(self):
        dealer = self.dealer
        dealposs = self.dealposs
        if self.blackjack:
            odds = 1
            if dealer.cards[0].value == 10:
                odds -= (self.deck.valuesleft[11]/self.deck.cardsleft)
            elif dealer.cards[0].value == 11:
                odds -= (self.deck.valuesleft[10]/self.deck.cardsleft)
            return odds * bjPays
        payout = 0
        winodds= 0
        for state in dealposs:
            if state[0] < self.total:
                winodds += dealposs[state]*2
            elif state[0] == self.total:
                winodds += dealposs[state]
        return winodds

    def hitodds(self):
        if self.blackjack:
            return 0 #not worring about this we all know to stay on backjack it's a lowe payout for a lower odds of winning.
        dealer, dealposs, currscore = self.dealer, self.dealposs, self.total
        prob = 0
        for item in dealposs:
            dealscore, cardposs = getscoreanddeckfromhashable(item)
            totcards = sum(cardposs.values())
            ##here we start a stocastic graph traversal to figure out who wins
            fringe = [(currscore, cardposs, totcards, dealposs[item])]
            ###items are (playerscore, dealer score, card dictionary, int of all cards, state probability)
            while fringe:
                playscore, carddict, totcards, stateprob = fringe.pop()
                for card in cardposs:
                    newscore = card + playscore
                    if newscore > 21:
                        continue
                    newprob = cardposs[card]/totcards * stateprob
                    if newscore > dealscore:
                        prob += newprob * 2
                        continue
                    if newscore == dealscore:
                        ##will figure this out later for a decision but most of the time that you have the same value
                        # as a dealer with a viable number then you probably have better odds not hitting.
                        prob += newprob
                        continue
                    ##if there was no exit case then you add your item to the fringe.
                    carddict[card] -= 1
                    fringe.append((newscore, carddict, totcards-1, newprob))

        return prob



def main():



    this = Deck(6)
    totwins = 0
    for iii in range(0, 90):
        print(iii)
        deal = Dealer(this)
        play = Player(this, deal)
        play.getstatespace()
        temp = play.stayodds()
        new = play.hitodds()
        print("Cards in play player:", play.cards[0], play.cards[1],"\nDealer:", deal.faceup, "\nStay odds:", temp, "hitodds", new)
        totwins += max(temp,new)
    print("average payout:", totwins/90)


if __name__ =="__main__":
    main()
