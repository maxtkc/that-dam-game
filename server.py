#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import re
import sqlite3
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = {}

GAMES = []

# Dict
# {'<cookie>': {
#   'socket': websocket,
#   'game-player': (index_of_game, index_of_player),
# }
SESSIONS = {}


# Connect to db
conn = sqlite3.connect('game.db')


def get_cursor():
    return conn.cursor()


def commit_db():
    conn.commit()


def state_event():
    # Get state for a specific user:
    # for each player, if the player is not this player, get public data, else
    # get private data
    return json.dumps({"type": "state", **STATE})


def users_event():
    # Get open games
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_waiting():
    c = get_cursor()
    c.execute(''' SELECT cookie,name FROM users WHERE game IS NULL AND player IS NULL ''')
    response = c.fetchall()
    cookies, names = zip(*response)

    for websocket in [USERS[cookie] for cookie in cookies]:
        websocket.send(names)

    # if USERS:  # asyncio.wait doesn't accept an empty list
    #     message = users_event()
    #     await asyncio.wait([user.send(message) for user in USERS])


async def send_error(websocket, msg):
    websocket.send(json.dumps({'type': 'error', 'reason': msg}))


async def register(cookie, name, websocket):
    # Verify cookie is 32 hex chars:
    assert re.match('^[0-9a-fA-F]{32}$', cookie)

    # If already connected, close this additional connection
    # if cookie in USERS:
    #     logging.warn('Closing second connection with cookie: {}'.format(cookie))
    #     await send_error(websocket, 'already connected')
    #     websocket.close()
    #     return

    logging.info('Registering websocket with cookie: {}'.format(cookie))

    # Register websocket
    USERS[cookie] = websocket

    c = get_cursor()
    # Register users cookie in db
    c.execute(''' INSERT INTO users(cookie,name) VALUES(?,?) ''', cookie, name)
    await notify_waiting()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_all()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif data["action"] == "plus":
                STATE["value"] += 1
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
            commit_db()
    finally:
        await unregister(websocket)


async def serve(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'register_cookie':
                await register(data['cookie'], data['name'], websocket)
    finally:
        await unregister(websocket)


# Create table if it does not exist
def create_table():
    c = get_cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' ''')
    if c.fetchone()[0] == 0:
        c.execute(''' CREATE TABLE users (cookie TEXT NOT NULL UNIQUE PRIMARY KEY, name TEXT NOT NULL, game INTEGER, player INTEGER) ''')
    commit_db()


# Serve
start_server = websockets.serve(serve, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
