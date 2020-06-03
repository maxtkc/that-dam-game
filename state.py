import pydealer
import random


class Player:
    def __init__(self, name):
        self.hand = pydealer.Stack()
        self.set_meld = []
        self.run_meld = []
        self.name = name
        self.beg_count = 0
        self.score = 0

    def __str__(self):
        return '{}: {}'.format(self.name, self.hand)


class DamGame:
    # {  # ROUND <round number>
    # 'sets': (<sets>, <cards in each set>),
    # 'runs': (<runs>, <cards in each run>, <allowed wildcards in each run>),
    # },
    ROUNDS = [
        {  # ROUND 1
            'sets': (2, 3),
            'runs': (0, 0, 0),
        },
        {  # ROUND 2
            'sets': (1, 3),
            'runs': (1, 4, 1),
        },
        {  # ROUND 3
            'sets': (0, 0),
            'runs': (2, 4, 1),
        },
        {  # ROUND 4
            'sets': (3, 3),
            'runs': (0, 0, 0),
        },
        {  # ROUND 5
            'sets': (1, 3),
            'runs': (1, 7, 3),
        },
        {  # ROUND 6
            'sets': (2, 3),
            'runs': (1, 5, 2),
        },
        {  # ROUND 7
            'sets': (0, 0),
            'runs': (3, 4, 1),
        },
        {  # ROUND 8
            'sets': (1, 3),
            'runs': (1, 10, 4),
        },
        {  # ROUND 9
            'sets': (2, 3),
            'runs': (2, 4, 1),
        },
        {  # ROUND 10
            'sets': (0, 0),
            'runs': (3, 5, 2),
        },
    ]

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

        # Index of the begging player (-1 is none)
        self.beggar = -1

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

    def get_new_deck(self, num_decks):
        """Creates a new shuffled deck
        Creates a shuffled deck with the number of decks specified
        """
        deck = pydealer.Deck(jokers=True, num_jokers=2)
        for n in range(num_decks - 1):
            other_deck = pydealer.Deck(jokers=True, num_jokers=2)
            deck.add(other_deck.deal(54))

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

        # If there is a beggar, deal the top two discard cards to them
        if self.beggar != -1:
            beggar = self.players[self.beggar]
            beggar.hand.add(self.discard_pile.deal(2))
            beggar.beg_count += 1

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

        # Clear the unsuccessful begging attempt
        self.beggar = -1

    def discard_card(self, player_i, card_i):
        """Discard a card from the a players hand
        Player at index player_i discards card_i from their hand. If there is a
        winner for the round, set up for the next round

        Prerequisites:
        - Must be this players turn
        - Must have a card at card_i

        It will be another persons turn after this player discards
        """
        self.raise_if_out_of_turn(player_i)
        self.raise_if_no_card(player_i, card_i)
        card = self.players[player_i].hand.get(card_i)
        self.discard_pile.add(card)

        # If the round is over
        if len(self.players[player_i].hand) < 1:
            self.increment_round()
        else:
            self.increment_player()

    def request_beg(self, player_i):
        """Set a player to be the beggar
        Player at index player_i is to be the beggar so that they will be able
        to recieve cards if the current player draws from the top of the deck

        Prerequisites:
        - Discard pile must have at least 2 cards
        - Must not be this players turn
        """
        self.raise_if_turn(player_i)
        self.raise_if_empty(self.discard_pile, min_size=2)
        self.raise_if_no_begs_left(player_i)
        if self.beggar == -1 or player_i - self.current_player < self.beggar - self.current_player:
            self.beggar = player_i

    def meld(self, player_i, sets=[], runs=[]):
        """Place down the cards for this round
        Player at index player_i places down the cards, if meld is correct for
        the current round

        Args:
            player_i (int): the index of the player
            sets (list<list<int>>): list of sets, each set containing the card
            indices for the set
            runs (list<list<int>>): list of runs, each run containing the card
            indices for the run

        Prerequisites:
        - Must be this players turn
        - Must have proper number of sets and runs for round
        - All cards must be valid and not duplicates
        - Each set and each run must be correct
        """
        self.raise_if_out_of_turn(player_i)

        # Flatten sets and runs to get one list of all card indices
        all_sets = [item for sublist in sets for item in sublist]
        all_runs = [item for sublist in runs for item in sublist]
        all_cards = all_sets + all_runs
        self.raise_if_duplicates(all_cards)

        spec = self.ROUNDS[self.round]
        cur_hand = self.players[player_i].hand
        self.raise_if_bad_sets(cur_hand, sets, spec['sets'])
        self.raise_if_bad_runs(cur_hand, runs, spec['runs'])

        # Assumes correct sets and runs

        # Add sets to meld
        set_meld = self.players[player_i].set_meld
        for s in sets:
            cards = pydealer.Stack()
            for i in s:
                cards.add(cur_hand.get(i))
            set_meld.append(cards)

        # Add runs to meld
        run_meld = self.players[player_i].run_meld
        for r in runs:
            cards = pydealer.Stack()
            for i in r:
                cards.add(cur_hand.get(i))
            run_meld.append(cards)

    def raise_if_bad_sets(self, hand, sets, spec):
        n, size = spec
        if len(sets) != n:
            raise ValueError('Sets {} does not have proper number {}'.format(sets, n))
        for s in sets:
            if len(s) != size:
                raise ValueError('Set {} does not have exactly {} cards'.format(s, size))
            if len(set([hand[card_i].value for card_i in s])) > 1:
                raise ValueError('Set {} is not a valid set'.format(s))

    def raise_if_bad_runs(self, hand, runs, spec):
        n, size, max_wild = spec
        if len(runs) != n:
            raise ValueError('Runs {} does not have proper number {}'.format(runs, n))
        for r in runs:
            if len(r) != size:
                raise ValueError('Run {} does not have exactly {} cards'.format(r, size))

            # Create a list of card objects from the hand
            cards = [hand[card_i] for card_i in r]

            # Get values and ranks, and remove wild cards
            card_vals = [card.value for card in cards if not self.is_wild(card)]
            card_suits = [card.suit for card in cards if not self.is_wild(card)]

            # Check suits are all the same
            if len(set(card_suits)) > 1:
                raise ValueError('Run {} is not all the same suit'.format(r))

            # Num wild is num removed from cards to card_vals
            num_wild = len(card_vals) - len(cards)
            if num_wild > max_wild:
                raise ValueError('Run {} has more than {} wild cards'.format(r, max_wild))

            # Get card ranks
            card_ranks = [pydealer.DEFAULT_RANKS['values'][val] for val in card_vals]

            # card_ranks must not contain duplicates
            if len(card_ranks) != len(set(card_ranks)):
                raise ValueError('Run {} contains duplicate values'.format(r))

            # Check number of cards spans the entire range
            if len(cards) < max(card_ranks) - min(card_ranks):
                raise ValueError('Run {} is not valid'.format(r))

    def score(self, hand):
        for card in hand:
            rank = pydealer.DEFAULT_RANKS['values'][card.value]
            # Ace: 15 points
            if rank == 13:
                return 15
            # Ten to king: 10 points
            if rank in range(9, 13):
                return 10
            # Three to nine: 5 points
            if rank in range(2, 9):
                return 5
            # Two: 20 points
            if rank == 1:
                return 20
            # Joker: 50 points
            if rank == 0:
                return 50
            raise ValueError('Bad card {} in hand {}'.format(card, hand))

    def raise_if_not_len(self, items, length):
        if len(items) != length:
            raise ValueError('List of items {} not proper length {}'.format(items, length))

    def raise_if_duplicates(self, cards):
        if len(cards) != len(set(cards)):
            raise ValueError('List of cards {} has duplicates'.format(cards))

    def raise_if_out_of_turn(self, player_i):
        if self.current_player != player_i:
            raise ValueError('Player {} tried to play out of turn'.format(player_i))

    def raise_if_turn(self, player_i):
        if self.current_player == player_i:
            raise ValueError('Player {} tried to beg on their own turn'.format(player_i))

    def raise_if_empty(self, stack: pydealer.Stack, min_size=1):
        if stack.size < min_size:
            raise ValueError('Stack has no cards')

    def raise_if_no_card(self, player_i, card_i):
        if self.players[player_i].hand.size <= card_i:
            raise ValueError('Player {} has no card {}'.format(player_i, card_i))

    def raise_if_no_begs_left(self, player_i):
        if self.players[player_i].beg_count >= 3:
            raise ValueError('Player {} has no begs left'.format(player_i))

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

    def increment_round(self):
        # Also does the reset of the cards, players, etc
        if self.round < len(self.ROUNDS):
            for player in self.players:
                player.score += self.score(player.hand)
            self.round += 1
            self.increment_dealer()

            # Reset the deck and discard pile
            self.deck = self.get_new_deck(self.get_num_decks())
            self.discard_pile = pydealer.Stack()

            # Set the current player to the left of the dealer
            self.current_player = self.dealer
            self.increment_player()

            # Reset the index of the begging player (-1 is none)
            self.beggar = -1
        else:
            # End of game
            raise Exception('Handle end of game!')


if __name__ == '__main__':
    game = DamGame([Player('Claire'), Player('Max'), Player('Dorothy')])
    game.deal()
    print(game.players[0])
    game.draw_card_from_deck(0)
    print(game.players[0])
    game.increment_round()
    print(game)
    # game.discard_card(0, 0)
    # print(game.players[0])
