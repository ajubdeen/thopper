#!/usr/bin/env python3
"""
Anachron Game Server

Flask-SocketIO server that wraps the GameSession API.
Emits structured JSON messages to connected clients.
"""

import os
import sys
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET') or os.urandom(24).hex()

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

from game_api import GameSession

sessions = {}


@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    sid = request.sid
    logger.info(f"Client connected: {sid}")
    
    session = GameSession()
    sessions[sid] = session
    
    messages = session.start()
    for msg in messages:
        emit('message', msg)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    sid = request.sid
    logger.info(f"Client disconnected: {sid}")
    
    if sid in sessions:
        del sessions[sid]


@socketio.on('set_name')
def handle_set_name(data):
    """Set player name"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    name = data.get('name', 'Traveler')
    messages = sessions[sid].set_name(name)
    for msg in messages:
        emit('message', msg)


@socketio.on('set_region')
def handle_set_region(data):
    """Set region preference"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    region = data.get('region', 'worldwide')
    messages = sessions[sid].set_region(region)
    for msg in messages:
        emit('message', msg)


@socketio.on('enter_first_era')
def handle_enter_first_era():
    """Enter the first era"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    messages = sessions[sid].enter_first_era()
    for msg in messages:
        emit('message', msg)


@socketio.on('choose')
def handle_choose(data):
    """Make a choice"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    choice = data.get('choice', 'A')
    messages = sessions[sid].choose(choice)
    for msg in messages:
        emit('message', msg)


@socketio.on('continue_to_next_era')
def handle_continue_to_next_era():
    """Continue to next era after departure"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    messages = sessions[sid].continue_to_next_era()
    for msg in messages:
        emit('message', msg)


@socketio.on('get_state')
def handle_get_state():
    """Get current game state"""
    sid = request.sid
    if sid not in sessions:
        emit('message', {'type': 'error', 'data': {'message': 'Session not found'}})
        return
    
    state = sessions[sid].get_state()
    emit('message', {'type': 'state', 'data': state})


@socketio.on('restart')
def handle_restart():
    """Restart the game"""
    sid = request.sid
    logger.info(f"Restart requested for {sid}")
    
    session = GameSession()
    sessions[sid] = session
    
    messages = session.start()
    for msg in messages:
        emit('message', msg)


if __name__ == '__main__':
    port = int(os.environ.get('GAME_SERVER_PORT', 5001))
    logger.info(f"Starting Anachron game server on port {port}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
