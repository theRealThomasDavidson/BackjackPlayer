import random
import copy
import json
import datetime

suits = ("C", "D", "S", "H")
numbers = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "t": 10, "J": 10, "Q": 10, "K": 10}
bjPays = 1.5
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

    def playpct(self, playerscore, deck):
        """
        this method is to see what the percentage chance that the dealer beats a particular score this will be based on
        hit til 16, hit soft 17, ties are even not losses.
        :param playerscore: this is the number that the player has on the table
        :param deck: is a dict in the form {"cardsleft": int, "valuesleft":{1:int, 2:int, ...10:int} this will be the
        deck that is left over
        :return: a float that reflects the propotion (between 0 and 1) of games where the player wins minus the proportion
        when they  lose. This should give a number between -1 and 1 always.
        ####TESTING####
        2019 8 24
        appears to be working had a problem for a bit with shallow copies instead of deep copies but appears to work now.
        parameters:
        I basically made dealers with the first 12 cards drawn from a size 6 deck. (might be more rigorous if this
        doesn't appear to work)
        I asked each of them to do this procedure with 12,14(both under any dealer stop so they should report the same
        numbers.) and 17,18,19,20, and 21. with each of my test cases the first 2 win rates were appropriately the
        lowest and repeated for 12 and 14. the other win rates were each larger than the last one.

        all reported winnings were between -1 and 1.
        ###############
        """
        total = 0.
        fringe = [(self.faceup.value, self.faceup.value == 11, 1., deck)]
        while fringe:
            currval, soft, currprop, currdeck = fringe.pop()
            if currval >= 17:
                if currval > 21:
                    if soft:
                        fringe.append((currval-10, False, currprop, currdeck))
                        continue
                    else:
                        total += currprop
                        continue
                if currval == 17 and soft:
                    for cardval in currdeck["valuesleft"]:
                        if not currdeck["valuesleft"][cardval]:
                            continue
                        newprop = currprop * currdeck["valuesleft"][cardval] / currdeck["cardsleft"]
                        newval = currval + cardval - ((cardval == 11) * 10)
                        newdeck = copy.deepcopy(deck)
                        newdeck["cardsleft"] -= 1
                        newdeck["valuesleft"][cardval] -= 1
                        fringe.append((newval, True, newprop, newdeck))
                        continue
                    continue
                if currval > playerscore:
                    total -= currprop
                    continue
                elif currval < playerscore:
                    total += currprop
                    continue
                else:
                    continue
            for cardval in currdeck["valuesleft"]:
                if not currdeck["valuesleft"][cardval]:
                    continue
                newprop = currprop * currdeck["valuesleft"][cardval] / currdeck["cardsleft"]
                newval = currval + cardval
                newdeck = copy.deepcopy(deck)
                newdeck["cardsleft"] -= 1
                newdeck["valuesleft"][cardval] -= 1
                fringe.append((newval, soft or cardval == 11, newprop, newdeck))
        return total
    def surrenderpct(self):
        """
        this is just a method so that the odds calculations are consistent in calling methods this just
        returns the payout of a surrender for your first move.
        :return: a float equal to -0.5
        """
        return -0.5
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

    def hit(self):
        newcard = self.deck.draw()
        self.cards = tuple(list(self.cards) + [newcard])
        self.total += newcard.value
        if self.total > 21:
            for card in self.cards:
                if card.value == 11:
                    card.value = 1
                    self.total -= 10
        return None

    def getstatespace(self):
        dealer = self.dealer
        dealscore = (dealer.cards[0].value, not dealer.cards[0].value - 11)
        workvals = copy.deepcopy(self.deck.valuesleft)
        cardsleft = self.deck.cardsleft
        self.dealposs = dealer_space(dealscore, cardsleft, workvals)

    def stayOdds(self):
        """
        this gives the payout from -1 to 1 of staying at a given gamestate. it uses the expectimax from the dealers
        playpct method.
        :param self.cards: this is the cards that are already in the players hands and will be used to get the players
        current score
        :param self.dealer: this is the dealer and must be used to ge the playpct payout for the player.
        :return: will return the payout as a float between -1 and 1.

        ####TESTING####
        appears to work done along with playpct and will return the value expected with both 2 and 3 card draws.totals
        under 17 will give the same odds as a playpcty that is under 17, from 17 to 21 they appear to give the same odds
        as their corresponding score and for values over 21 they give -1.
        ###############
        """
        soft = False
        score = 0
        for card in self.cards:
            val = card.value
            if val == 11:
                if not soft:
                    soft = True
                else:
                    val = 1
            score += val
        if score > 21 and soft:
            score -= 10
        if score > 21:
            return -1.
        else:
            deck = {"cardsleft": copy.copy(self.deck.cardsleft), "valuesleft":copy.deepcopy(self.deck.valuesleft)}
            return self.dealer.playpct(score, deck)

    def doubleOdds(self):
        """
        this will return the payout on doubleing down.
        :return: the payout for doubling down (not that bets are doubled here so your payout range is between -2 and 2
        of your original bet.

        ####TESTING####
        went through debugging and it seems to work fine. the below dealer hit threshold seems to work fine and I think
        that should speed it up a bit, but look in the future for better uses of cyles here.
        ###############
        ##TODO: make it so we only have to calculate the score once before we add the new cards
        """

        payout = 0
        deck = {"cardsleft": copy.copy(self.deck.cardsleft), "valuesleft": copy.deepcopy(self.deck.valuesleft)}
        belowhit = 0.
        for newcard in deck["valuesleft"]:
            prob = self.deck.valuesleft[newcard]/self.deck.cardsleft
            soft = newcard == 11
            score = newcard
            for card in self.cards:
                val = card.value
                if val == 11:
                    if not soft:
                        soft = True
                    else:
                        val = 1
                score += val
            if score > 21 and soft:
                score -= 10
            if score > 21:
                payout -= prob
            elif score < 17:
                belowhit += prob
            else:
                payout += self.dealer.playpct(score, deck) * prob
        payout += belowhit * self.dealer.playpct(11, deck)
        return payout*2
    def hitOdds(self):
        """
        this method should give the odds of hitting recursively(using while loop instead because using expetimax.
        it should also return "hit" or "stay" if hitting or staying
        :param self.cards: this is the cards that are already in the players hands and will be used to get the players
        current
        :param self.deck.cardsleft: this is an int that shows how many cards are in the deck
        :param self.deck.valuesleft: this is a dict of the form {2:int, 3: int,...,11:int}that shows how many cards of
        each value are left in the deck, with 11 being the ace.
        :return: a tuple of tghe form (float, str) where the float is the winning payout of the current condition given
        ideal play(between -1 and 1), and the string is either "hit" or "stay" or "bust" based on what ideal play dictates.
        """
        soft = False
        score = 0
        for card in self.cards:
            val = card.value
            if val == 11:
                if not soft:
                    soft = True
                else:
                    val = 1
            score += val
        if score > 21:
            if soft:
                score -= 10
                soft = False
            else:
                return "Bust", -1.
        play = "stay"
        deck = {"cardsleft": copy.copy(self.deck.cardsleft), "valuesleft": copy.deepcopy(self.deck.valuesleft)}
        prob = self.stayOdds()
        hitprob = 0.
        fringe = [(score, soft, deck, 1., prob)]
        while fringe:
            currscore, soft,  currdeck, stateprob, stayprob = fringe.pop()
            newHitProb = 0.
            if currscore > 21 and soft:
                currscore -= 10
                soft = False
            if currscore > 21:
                hitprob -= stateprob
                continue
            if currscore == 21:
                hitprob += stayprob
                continue
            drawnCardStates = []
            for card in [11, 2, 3, 4, 5, 6, 7, 8, 9, 10]: #this is changed because of how soft bids workdeck["valuesleft"]:
                if not deck["valuesleft"][card]:
                    continue
                newscore = currscore + card
                newStateProb = stateprob * deck["valuesleft"][card] / deck["cardsleft"]
                newSoft = soft
                if soft:
                    if card == 11:
                        newscore -= 10
                    elif newscore > 21:
                        newscore -= 10
                        newSoft = False
                elif card == 11:
                    if newscore > 21:
                        newscore -= 10
                    else:
                        newSoft = True
                if newscore > 21:
                    newHitProb -= newStateProb
                newDeck = deck = {"cardsleft": copy.copy(self.deck.cardsleft), "valuesleft": copy.deepcopy(self.deck.valuesleft)}
                newDeck["valuesleft"][card] -= 1
                newDeck["cardsleft"] -= 1
                newStay = self.dealer.playpct(newscore, newDeck) * newStateProb
                newHitProb += newStay * newStateProb
                drawnCardStates.append((newscore, newSoft, newDeck, newStateProb, newStay))

            ####
            #basically I can expalin this by you never want to queue up two hits as being more likely to win
            #if the first one is not more likely to win.
            if newHitProb >= stayprob:
                fringe += drawnCardStates
            else:
                hitprob += stayprob

        if hitprob > prob:
            return "hit", hitprob
        return "stay", prob



def main():
    start = datetime.datetime.now()

    this = Deck(6)
    for iii in range (1,15):
        deal = Dealer(this)
        play = Player(this, deal)
        print("plyercards:", tuple(str(card) for card in play.cards))
        print("dealer card:", deal.faceup)
        print("player odds:", play.stayOdds())
        print("player double down odds:", play.doubleOdds())
        print("player hit odds:", play.hitOdds())
        deck = {"cardsleft": this.cardsleft, "valuesleft": this.valuesleft}
        print("with 14 player gets:", deal.playpct(14, deck))
        print("with 17 player gets:", deal.playpct(17, deck))
        print("with 18 player gets:", deal.playpct(18, deck))
        print("with 19 player gets:", deal.playpct(19, deck))
        print("with 20 player gets:", deal.playpct(20, deck))
        print("with 21 player gets:", deal.playpct(21, deck),"\n")

    print(datetime.datetime.now() - start)
    """
    payoutlist = []

    for jjj in range(400):
        this = Deck(6)
        totwins = 0
        for iii in range(0, 90):
            #print(iii)
            deal = Dealer(this)
            play = Player(this, deal)
            play.getstatespace()
            temp = play.stayodds()
            new = play.hitodds()
            #print("Cards in play player:", play.cards[0], play.cards[1],"\nDealer:", deal.faceup, "\nStay odds:", temp, "hitodds", new)
            #if max(temp, new) > 2.5:
            #    raise Exception
            totwins += max(temp, new)
        #print("average payout:", totwins/90)
        payoutlist.append(totwins/90)
        print("Deck", jjj, "finished.")
    json.dump({"payoutlists":payoutlist}, open("400deckspayouts.json","w"))
    """
if __name__ == "__main__":
    main()
