/*
 * Note: Types for client (not storing state in db) -- Some values are hidden to the client
 */

enum Suit {
    Spades='S',
    Hearts='H',
    Diamonds='D',
    Clubs='C',
}

enum Rank {
    Two='2',
    Three='3',
    Four='4',
    Five='5',
    Six='6',
    Seven='7',
    Eight='8',
    Nine='9',
    Ten='10',
    Jack='J',
    Queen='Q',
    King='K',
    Ace='A',
    Joker='R',
}

export interface Card {
    suit: Suit;
    rank: Rank;
}

export interface Player {
    hand: Card[];
    set_meld: Card[][];
    run_meld: Card[][];
    name: string;
    beg_count: number;
    score: number;
}

/**
 * Shown hand
 */
export interface PlayerShown {
    hand: Card[];
    set_meld: Card[][];
    run_meld: Card[][];
    name: string;
    beg_count: number;
    score: number;
}

/**
 * Hidden hand
 */
export interface PlayerHidden {
    hand: number;
    set_meld: Card[][];
    run_meld: Card[][];
    name: string;
    beg_count: number;
    score: number;
}

export interface Deck {
    deck_size: number;
    discard_pile_size: number;
    top_discard?: Card;
}

export interface PlayingState {
    other_players: PlayerHidden[];
    this_player: PlayerShown;
    round: number;
    dealer: number;
    current_player: number;
    beggar: number;
    deck: Deck;
}

export interface WaitingState {
    player_names: string[]
}
