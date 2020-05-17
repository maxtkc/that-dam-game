import pydealer
import random


class Player:
    def __init__(self, name):
        self.hand = pydealer.Stack()
        self.meld = pydealer.Stack()
        self.name = name
        self.beg_count = 0

    def __str__(self):
        return '{}: {}'.format(self.name, self.hand)


class DamGame:
    def __init__(self, players):
        # Number of Players: at least three and up to six
        if len(players) not in range(3, 7):
            raise ValueError('Game must be played with 3 to 6 players, not {}'.format(len(players)))

        # Initalize the state
        self.players = players

        # Zero based round number
        self.round = 0

        # Create an empty discard pile
        self.discard_pile = pydealer.Stack()

        # Choose a random dealer
        self.dealer = random.randrange(len(players))

        # Set the current player to the left of the dealer
        self.current_player = self.dealer
        self.increment_player()

        # Initialize the deck with the proper number of decks
        self.deck = self.get_new_deck(self.get_num_decks())

    def __str__(self):
        return str([', '.join(str(player).split('\n')) for player in self.players])

    def is_wild(self, card):
        """Returns if the card is wild
        Wild cards are 2’s and Jokers
        """
        return card.value in ['2', 'Joker']

    def get_num_decks(self):
        """Returns the number of decks to use
        A deck contains the usual 52 cards, plus 2 Jokers. Two decks for three
        people, three decks for four or five, four decks for more.
        """
        n_players = len(self.players)
        if n_players == 3:
            return 2
        if n_players in [4, 5]:
            return 3
        return 4

    def get_new_deck(self, num_decks):  # TODO: Add jokers
        """Creates a new shuffled deck
        Creates a shuffled deck with the number of decks specified
        """
        deck = pydealer.Deck()
        for n in range(num_decks - 1):
            other_deck = pydealer.Deck()
            deck.add(other_deck.deal(52))

        deck.shuffle()
        return deck

    def deal(self):
        for player in self.players:
            player.hand = self.deck.deal(self.round + 6)

    def draw_card_from_deck(self, player_i):
        """Draw a card from the deck
        Player at index player_i draws a card from the top of the deck

        Prerequisites:
        - Must be this players turn
        - Deck must have cards
        """
        self.raise_if_out_of_turn(player_i)
        self.raise_if_empty(self.deck)
        self.players[player_i].hand.add(self.deck.deal(1))

    def draw_card_from_discard(self, player_i):
        """Draw a card from the deck
        Player at index player_i draws a card from the top of the deck

        Prerequisites:
        - Must be this players turn
        - Discard pile must have cards
        """
        self.raise_if_out_of_turn(player_i)
        self.raise_if_empty(self.discard_pile)
        self.players[player_i].hand.add(self.discard_pile.deal(1))

    def discard_card(self, player_i, card_i):
        """Discard a card from the a players hand
        Player at index player_i discards card_i from their hand

        Prerequisites:
        - Must be this players turn
        - Must have a card at card_i

        It will be another persons turn after this player discards
        """
        self.raise_if_out_of_turn(player_i)
        self.raise_if_no_card(player_i, card_i)
        card = self.players[player_i].hand.get(card_i)
        self.discard_pile.add(card)

        self.increment_player()

    def raise_if_out_of_turn(self, player_i):
        if self.current_player != player_i:
            raise ValueError('Player {} tried to play out of turn'.format(player_i))

    def raise_if_empty(self, stack: pydealer.Stack):
        if stack.size < 1:
            raise ValueError('Stack has no cards')

    def raise_if_no_card(self, player_i, card_i):
        if self.players[player_i].hand.size <= card_i:
            raise ValueError('Player {} has no card {}'.format(player_i, card_i))

    def increment_player(self):
        self.current_player = self.increment_within_players(self.current_player)

    def increment_dealer(self):
        self.dealer = self.increment_within_players(self.dealer)

    def increment_within_players(self, num):
        """Increment a number within self.players
        """
        num += 1
        num %= len(self.players)
        return num


if __name__ == '__main__':
    game = DamGame([Player('Claire'), Player('Max'), Player('Dorothy')])
    game.deal()
    print(game.players[0])
    game.draw_card_from_deck(0)
    print(game.players[0])
    game.discard_card(0, 0)
    print(game.players[0])
