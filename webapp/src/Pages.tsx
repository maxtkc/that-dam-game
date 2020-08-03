import React from 'react';
import { RouteComponentProps, } from 'react-router-dom'
import { Convert, PlayingState, PlayerShown, PlayerHidden, Deck, Card, } from "./Types";

import { makeStyles, createStyles, Theme, } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            flexGrow: 1,
        },
        paper: {
            padding: theme.spacing(2),
            textAlign: 'center',
            color: theme.palette.text.secondary,
        },
    }),
);

export const EntryView = () => {
    return (
        <span>Welcome</span>
    );
}

type Props = { game_id: string };

export const GameView = ({ match }: RouteComponentProps<Props>) => {
    return (
        <div>
            <span>game_id is {match.params.game_id}</span>
            <br />
            <PlayingView state={Convert.toPlayingState('{"other_players":[{"hand":0,"set_meld":[],"run_meld":[],"name":"other player 1","beg_count":0,"score":0},{"hand":0,"set_meld":[],"run_meld":[],"name":"other player 2","beg_count":0,"score":0}],"this_player":{"hand":[],"set_meld":[],"run_meld":[],"name":"my name","beg_count":0,"score":0},"round":2,"dealer":0,"current_player":0,"beggar":0,"deck":{"deck_size":0,"discard_pile_size":0,"top_discard":{"suit":"D","rank":"A"}}}')} />
        </div>
    );
}

export interface PlayingViewProps {
    state: PlayingState;
}

export const PlayingView: React.FC<PlayingViewProps> = ({ state }) => {
    const classes = useStyles();

    return (
        <div className={classes.root}>
            <span>Playing Game (round {state.round})</span>
            <Grid
                container
                spacing={3}
                justify="center"
                alignItems="center">
                {state.other_players.map((player) => (
                    <Grid item xs={4}>
                        <OtherPlayer player={player} />
                    </Grid>
                ))}
                <Grid item xs={12}>
                    <DeckView deck={state.deck} />
                </Grid>
                <Grid item xs={12}>
                    <ThisPlayer player={state.this_player} />
                </Grid>
            </Grid>
        </div>
    );
}

export interface ThisPlayerProps {
    player: PlayerShown;
}

export const ThisPlayer: React.FC<ThisPlayerProps> = ({ player }) => {
    const classes = useStyles();

    return (
        <Paper className={classes.paper}>{JSON.stringify(player)}</Paper>
    );
}

export interface OtherPlayerProps {
    player: PlayerHidden;
}

export const OtherPlayer: React.FC<OtherPlayerProps> = ({ player }) => {
    const classes = useStyles();

    return (
        <Paper className={classes.paper}>{JSON.stringify(player)}</Paper>
    );
}

export interface DeckProps {
    deck: Deck;
}

export const DeckView: React.FC<DeckProps> = ({ deck }) => {
    const classes = useStyles();

    return (
        <Paper className={classes.paper}>Cards Left: {deck.deck_size}, Cards Discarded: {deck.discard_pile_size}, Top Discard: {deck.top_discard !== undefined ? (<CardView card={deck.top_discard} />) : "None"}</Paper>
    );
}

export interface CardView {
    card: Card;
}

export const CardView: React.FC<CardView> = ({ card }) => {
    const classes = useStyles();

    return (
        <Paper className={classes.paper}>Suit: {card.suit}, Rank: {card.rank}</Paper>
    );
}
