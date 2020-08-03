// To parse this data:
//
//   import { Convert, Suit, Rank, Card, Player, PlayerShown, PlayerHidden, Deck, PlayingState, WaitingState } from "./file";
//
//   const suit = Convert.toSuit(json);
//   const rank = Convert.toRank(json);
//   const card = Convert.toCard(json);
//   const player = Convert.toPlayer(json);
//   const playerShown = Convert.toPlayerShown(json);
//   const playerHidden = Convert.toPlayerHidden(json);
//   const deck = Convert.toDeck(json);
//   const playingState = Convert.toPlayingState(json);
//   const waitingState = Convert.toWaitingState(json);
//
// These functions will throw an error if the JSON doesn't
// match the expected interface, even if the JSON is valid.

export interface Player {
    beg_count: number;
    hand:      Card[];
    name:      string;
    run_meld:  Array<Card[]>;
    score:     number;
    set_meld:  Array<Card[]>;
}

export interface Card {
    rank: Rank;
    suit: Suit;
}

export enum Rank {
    A = "A",
        J = "J",
        K = "K",
        Q = "Q",
        R = "R",
        The10 = "10",
        The2 = "2",
        The3 = "3",
        The4 = "4",
        The5 = "5",
        The6 = "6",
        The7 = "7",
        The8 = "8",
        The9 = "9",
}

export enum Suit {
    C = "C",
        D = "D",
        H = "H",
        S = "S",
}

export interface PlayingState {
    beggar:         number;
    current_player: number;
    dealer:         number;
    deck:           Deck;
    other_players:  PlayerHidden[];
    round:          number;
    this_player:    PlayerShown;
}

export interface Deck {
    deck_size:         number;
    discard_pile_size: number;
    top_discard?:      Card;
}

/**
 * Hidden hand
 */
export interface PlayerHidden {
    beg_count: number;
    hand:      number;
    name:      string;
    run_meld:  Array<Card[]>;
    score:     number;
    set_meld:  Array<Card[]>;
}

/**
 * Shown hand
 */
export interface PlayerShown {
    beg_count: number;
    hand:      Card[];
    name:      string;
    run_meld:  Array<Card[]>;
    score:     number;
    set_meld:  Array<Card[]>;
}

export interface WaitingState {
    player_names: string[];
}

// Converts JSON strings to/from your types
// and asserts the results of JSON.parse at runtime
export class Convert {
    public static toSuit(json: string): Suit {
        return cast(JSON.parse(json), r("Suit"));
    }

    public static suitToJson(value: Suit): string {
        return JSON.stringify(uncast(value, r("Suit")), null, 2);
    }

    public static toRank(json: string): Rank {
        return cast(JSON.parse(json), r("Rank"));
    }

    public static rankToJson(value: Rank): string {
        return JSON.stringify(uncast(value, r("Rank")), null, 2);
    }

    public static toCard(json: string): Card {
        return cast(JSON.parse(json), r("Card"));
    }

    public static cardToJson(value: Card): string {
        return JSON.stringify(uncast(value, r("Card")), null, 2);
    }

    public static toPlayer(json: string): Player {
        return cast(JSON.parse(json), r("Player"));
    }

    public static playerToJson(value: Player): string {
        return JSON.stringify(uncast(value, r("Player")), null, 2);
    }

    public static toPlayerShown(json: string): PlayerShown {
        return cast(JSON.parse(json), r("PlayerShown"));
    }

    public static playerShownToJson(value: PlayerShown): string {
        return JSON.stringify(uncast(value, r("PlayerShown")), null, 2);
    }

    public static toPlayerHidden(json: string): PlayerHidden {
        return cast(JSON.parse(json), r("PlayerHidden"));
    }

    public static playerHiddenToJson(value: PlayerHidden): string {
        return JSON.stringify(uncast(value, r("PlayerHidden")), null, 2);
    }

    public static toDeck(json: string): Deck {
        return cast(JSON.parse(json), r("Deck"));
    }

    public static deckToJson(value: Deck): string {
        return JSON.stringify(uncast(value, r("Deck")), null, 2);
    }

    public static toPlayingState(json: string): PlayingState {
        return cast(JSON.parse(json), r("PlayingState"));
    }

    public static playingStateToJson(value: PlayingState): string {
        return JSON.stringify(uncast(value, r("PlayingState")), null, 2);
    }

    public static toWaitingState(json: string): WaitingState {
        return cast(JSON.parse(json), r("WaitingState"));
    }

    public static waitingStateToJson(value: WaitingState): string {
        return JSON.stringify(uncast(value, r("WaitingState")), null, 2);
    }
}

function invalidValue(typ: any, val: any): never {
    throw Error(`Invalid value ${JSON.stringify(val)} for type ${JSON.stringify(typ)}`);
}

function jsonToJSProps(typ: any): any {
    if (typ.jsonToJS === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.json] = { key: p.js, typ: p.typ });
        typ.jsonToJS = map;
    }
    return typ.jsonToJS;
}

function jsToJSONProps(typ: any): any {
    if (typ.jsToJSON === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.js] = { key: p.json, typ: p.typ });
        typ.jsToJSON = map;
    }
    return typ.jsToJSON;
}

function transform(val: any, typ: any, getProps: any): any {
    function transformPrimitive(typ: string, val: any): any {
        if (typeof typ === typeof val) return val;
        return invalidValue(typ, val);
    }

    function transformUnion(typs: any[], val: any): any {
        // val must validate against one typ in typs
        const l = typs.length;
        for (let i = 0; i < l; i++) {
            const typ = typs[i];
            try {
                return transform(val, typ, getProps);
            } catch (_) {}
        }
        return invalidValue(typs, val);
    }

    function transformEnum(cases: string[], val: any): any {
        if (cases.indexOf(val) !== -1) return val;
        return invalidValue(cases, val);
    }

    function transformArray(typ: any, val: any): any {
        // val must be an array with no invalid elements
        if (!Array.isArray(val)) return invalidValue("array", val);
        return val.map(el => transform(el, typ, getProps));
    }

    function transformDate(val: any): any {
        if (val === null) {
            return null;
        }
        const d = new Date(val);
        if (isNaN(d.valueOf())) {
            return invalidValue("Date", val);
        }
        return d;
    }

    function transformObject(props: { [k: string]: any }, additional: any, val: any): any {
        if (val === null || typeof val !== "object" || Array.isArray(val)) {
            return invalidValue("object", val);
        }
        const result: any = {};
        Object.getOwnPropertyNames(props).forEach(key => {
            const prop = props[key];
            const v = Object.prototype.hasOwnProperty.call(val, key) ? val[key] : undefined;
            result[prop.key] = transform(v, prop.typ, getProps);
        });
        Object.getOwnPropertyNames(val).forEach(key => {
            if (!Object.prototype.hasOwnProperty.call(props, key)) {
                result[key] = transform(val[key], additional, getProps);
            }
        });
        return result;
    }

    if (typ === "any") return val;
    if (typ === null) {
        if (val === null) return val;
        return invalidValue(typ, val);
    }
    if (typ === false) return invalidValue(typ, val);
    while (typeof typ === "object" && typ.ref !== undefined) {
        typ = typeMap[typ.ref];
    }
    if (Array.isArray(typ)) return transformEnum(typ, val);
    if (typeof typ === "object") {
        return typ.hasOwnProperty("unionMembers") ? transformUnion(typ.unionMembers, val)
            : typ.hasOwnProperty("arrayItems")    ? transformArray(typ.arrayItems, val)
            : typ.hasOwnProperty("props")         ? transformObject(getProps(typ), typ.additional, val)
            : invalidValue(typ, val);
    }
    // Numbers can be parsed by Date but shouldn't be.
    if (typ === Date && typeof val !== "number") return transformDate(val);
    return transformPrimitive(typ, val);
}

function cast<T>(val: any, typ: any): T {
    return transform(val, typ, jsonToJSProps);
}

function uncast<T>(val: T, typ: any): any {
    return transform(val, typ, jsToJSONProps);
}

function a(typ: any) {
    return { arrayItems: typ };
}

function u(...typs: any[]) {
    return { unionMembers: typs };
}

function o(props: any[], additional: any) {
    return { props, additional };
}

function m(additional: any) {
    return { props: [], additional };
}

function r(name: string) {
    return { ref: name };
}

const typeMap: any = {
    "Player": o([
        { json: "beg_count", js: "beg_count", typ: 3.14 },
        { json: "hand", js: "hand", typ: a(r("Card")) },
        { json: "name", js: "name", typ: "" },
        { json: "run_meld", js: "run_meld", typ: a(a(r("Card"))) },
        { json: "score", js: "score", typ: 3.14 },
        { json: "set_meld", js: "set_meld", typ: a(a(r("Card"))) },
    ], "any"),
    "Card": o([
        { json: "rank", js: "rank", typ: r("Rank") },
        { json: "suit", js: "suit", typ: r("Suit") },
    ], "any"),
    "PlayingState": o([
        { json: "beggar", js: "beggar", typ: 3.14 },
        { json: "current_player", js: "current_player", typ: 3.14 },
        { json: "dealer", js: "dealer", typ: 3.14 },
        { json: "deck", js: "deck", typ: r("Deck") },
        { json: "other_players", js: "other_players", typ: a(r("PlayerHidden")) },
        { json: "round", js: "round", typ: 3.14 },
        { json: "this_player", js: "this_player", typ: r("PlayerShown") },
    ], "any"),
    "Deck": o([
        { json: "deck_size", js: "deck_size", typ: 3.14 },
        { json: "discard_pile_size", js: "discard_pile_size", typ: 3.14 },
        { json: "top_discard", js: "top_discard", typ: u(undefined, r("Card")) },
    ], "any"),
    "PlayerHidden": o([
        { json: "beg_count", js: "beg_count", typ: 3.14 },
        { json: "hand", js: "hand", typ: 3.14 },
        { json: "name", js: "name", typ: "" },
        { json: "run_meld", js: "run_meld", typ: a(a(r("Card"))) },
        { json: "score", js: "score", typ: 3.14 },
        { json: "set_meld", js: "set_meld", typ: a(a(r("Card"))) },
    ], "any"),
    "PlayerShown": o([
        { json: "beg_count", js: "beg_count", typ: 3.14 },
        { json: "hand", js: "hand", typ: a(r("Card")) },
        { json: "name", js: "name", typ: "" },
        { json: "run_meld", js: "run_meld", typ: a(a(r("Card"))) },
        { json: "score", js: "score", typ: 3.14 },
        { json: "set_meld", js: "set_meld", typ: a(a(r("Card"))) },
    ], "any"),
    "WaitingState": o([
        { json: "player_names", js: "player_names", typ: a("") },
    ], "any"),
    "Rank": [
        "A",
        "J",
        "K",
        "Q",
        "R",
        "10",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    ],
    "Suit": [
        "C",
        "D",
        "H",
        "S",
    ],
};
