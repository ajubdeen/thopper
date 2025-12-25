#!/usr/bin/env python3
"""
Anachron Game Server

A Flask-SocketIO server that runs the game as a persistent service.
Uses Python's pty module to spawn game processes and stream I/O via WebSocket.
This approach keeps the game process alive independently of individual browser connections.
"""

import os
import sys
import pty
import select
import subprocess
import threading
import signal
import time
import logging
from flask import Flask
from flask_socketio import SocketIO, emit

logging.basicConfig(
    level=logging.DEBUG,
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

sessions = {}

class GameSession:
    """Manages a single game session with PTY"""
    
    def __init__(self, sid):
        self.sid = sid
        self.master_fd = None
        self.slave_fd = None
        self.pid = None
        self.running = False
        self.reader_thread = None
        
    def start(self):
        """Start a new game process"""
        try:
            self.master_fd, self.slave_fd = pty.openpty()
            
            self.pid = os.fork()
            
            if self.pid == 0:
                os.close(self.master_fd)
                
                os.setsid()
                
                os.dup2(self.slave_fd, 0)
                os.dup2(self.slave_fd, 1)
                os.dup2(self.slave_fd, 2)
                
                if self.slave_fd > 2:
                    os.close(self.slave_fd)
                
                env = os.environ.copy()
                env['TERM'] = 'xterm-256color'
                env['PYTHONUNBUFFERED'] = '1'
                
                game_dir = os.path.dirname(os.path.abspath(__file__))
                os.chdir(game_dir)
                
                os.execve(
                    sys.executable,
                    [sys.executable, 'game.py'],
                    env
                )
            else:
                os.close(self.slave_fd)
                self.slave_fd = None
                self.running = True
                
                self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
                self.reader_thread.start()
                
                logger.info(f"Game process started for session {self.sid}, pid={self.pid}")
                
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            self.cleanup()
            raise
    
    def _read_output(self):
        """Read output from game process and send to client"""
        try:
            while self.running and self.master_fd is not None:
                try:
                    readable, _, _ = select.select([self.master_fd], [], [], 0.1)
                    if readable:
                        try:
                            data = os.read(self.master_fd, 4096)
                            if data:
                                socketio.emit('output', {'data': data.decode('utf-8', errors='replace')}, room=self.sid)
                            else:
                                logger.info(f"Game process closed output for session {self.sid}")
                                break
                        except OSError as e:
                            if e.errno == 5:
                                logger.info(f"PTY closed for session {self.sid}")
                            else:
                                logger.error(f"Read error: {e}")
                            break
                except Exception as e:
                    logger.error(f"Select error: {e}")
                    break
        finally:
            self.running = False
            logger.info(f"Reader thread ended for session {self.sid}")
            socketio.emit('disconnected', {'reason': 'Game session ended'}, room=self.sid)
    
    def send_input(self, data):
        """Send input to game process"""
        if self.running and self.master_fd is not None:
            try:
                os.write(self.master_fd, data.encode('utf-8'))
            except OSError as e:
                logger.error(f"Write error: {e}")
                self.cleanup()
    
    def resize(self, rows, cols):
        """Resize the PTY"""
        if self.master_fd is not None:
            try:
                import fcntl
                import struct
                import termios
                winsize = struct.pack('HHHH', rows, cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            except Exception as e:
                logger.error(f"Resize error: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
                time.sleep(0.1)
                try:
                    os.waitpid(self.pid, os.WNOHANG)
                except:
                    pass
            except ProcessLookupError:
                pass
            except Exception as e:
                logger.error(f"Error killing process: {e}")
            self.pid = None
        
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except:
                pass
            self.master_fd = None
        
        if self.slave_fd is not None:
            try:
                os.close(self.slave_fd)
            except:
                pass
            self.slave_fd = None
        
        logger.info(f"Session {self.sid} cleaned up")


@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    sid = request.sid
    logger.info(f"Client connected: {sid}")
    
    session = GameSession(sid)
    sessions[sid] = session
    
    try:
        session.start()
    except Exception as e:
        logger.error(f"Failed to start game for {sid}: {e}")
        emit('error', {'message': 'Failed to start game'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    sid = request.sid
    logger.info(f"Client disconnected: {sid}")
    
    if sid in sessions:
        sessions[sid].cleanup()
        del sessions[sid]


@socketio.on('input')
def handle_input(data):
    """Handle input from client"""
    sid = request.sid
    if sid in sessions:
        sessions[sid].send_input(data.get('data', ''))


@socketio.on('resize')
def handle_resize(data):
    """Handle terminal resize"""
    sid = request.sid
    if sid in sessions:
        rows = data.get('rows', 24)
        cols = data.get('cols', 80)
        sessions[sid].resize(rows, cols)


@socketio.on('restart')
def handle_restart():
    """Handle game restart request"""
    sid = request.sid
    logger.info(f"Restart requested for {sid}")
    
    if sid in sessions:
        sessions[sid].cleanup()
        del sessions[sid]
    
    session = GameSession(sid)
    sessions[sid] = session
    
    try:
        session.start()
    except Exception as e:
        logger.error(f"Failed to restart game for {sid}: {e}")
        emit('error', {'message': 'Failed to restart game'})


from flask import request

def cleanup_all():
    """Clean up all sessions on shutdown"""
    logger.info("Cleaning up all sessions...")
    for sid, session in list(sessions.items()):
        session.cleanup()
    sessions.clear()

import atexit
atexit.register(cleanup_all)


if __name__ == '__main__':
    port = int(os.environ.get('GAME_SERVER_PORT', 5001))
    logger.info(f"Starting Anachron game server on port {port}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
