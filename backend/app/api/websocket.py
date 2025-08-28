"""
WebSocket API endpoints for real-time communication.
"""

import json
import threading
from collections import defaultdict
from flask import Blueprint, request, current_app, jsonify
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user
from datetime import datetime

websocket_bp = Blueprint('websocket', __name__)

# Thread-safe connection management
_connection_lock = threading.RLock()
active_connections = set()
subscribed_channels = defaultdict(set)

@websocket_bp.route('/')
def websocket_endpoint():
    """WebSocket endpoint for real-time communication."""
    return jsonify({
        'status': 'available',
        'message': 'WebSocket endpoint is available',
        'socketio_url': '/socket.io/',
        'connections': len(active_connections)
    })

@websocket_bp.route('/status')
def websocket_status():
    """Get WebSocket connection status."""
    with _connection_lock:
        return jsonify({
            'status': 'active',
            'connections': len(active_connections),
            'channels': list(subscribed_channels.keys())
        })

def setup_socketio_handlers(socketio):
    """Setup SocketIO event handlers."""
    
    @socketio.on('connect')
    def handle_connect(auth=None):
        """Handle client connection."""
        try:
            client_id = request.sid
            with _connection_lock:
                active_connections.add(client_id)
            
            current_app.logger.info(f'Client {client_id} connected')
            
            # Send connection confirmation
            emit('connected', {
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            })
            
            return True
        except Exception as e:
            current_app.logger.error(f'Connection error: {e}')
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        try:
            client_id = request.sid
            with _connection_lock:
                active_connections.discard(client_id)
                
                # Remove from all subscribed channels
                for channel, subscribers in subscribed_channels.items():
                    subscribers.discard(client_id)
                
                # Clean up empty channels
                empty_channels = [channel for channel, subscribers in subscribed_channels.items() if not subscribers]
                for channel in empty_channels:
                    del subscribed_channels[channel]
            
            current_app.logger.info(f'Client {client_id} disconnected')
        except Exception as e:
            current_app.logger.error(f'Disconnection error: {e}')
    
    @socketio.on('message')
    def handle_message(data):
        """Handle incoming messages."""
        try:
            client_id = request.sid
            current_app.logger.info(f'Received message from {client_id}: {data}')
            
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    emit('error', {'message': 'Invalid JSON format'})
                    return
            
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                handle_subscribe(data)
            elif message_type == 'unsubscribe':
                handle_unsubscribe(data)
            elif message_type == 'ping':
                emit('pong', {'timestamp': datetime.now().isoformat()})
            elif message_type == 'test':
                emit('test_response', {
                    'status': 'success',
                    'message': 'WebSocket test successful',
                    'timestamp': datetime.now().isoformat(),
                    'data': data.get('data', 'No test data')
                })
            else:
                # Echo unknown messages back for debugging
                emit('echo', {
                    'original_message': data,
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            current_app.logger.error(f'Message handling error: {e}')
            emit('error', {'message': f'Error processing message: {str(e)}'})
    
    def handle_subscribe(data):
        """Handle channel subscription."""
        try:
            client_id = request.sid
            channel = data.get('channel')
            
            if not channel:
                emit('error', {'message': 'Channel name required for subscription'})
                return
            
            with _connection_lock:
                # Add client to channel (defaultdict handles creation)
                subscribed_channels[channel].add(client_id)
            
            join_room(channel)
            
            current_app.logger.info(f'Client {client_id} subscribed to {channel}')
            
            emit('subscribed', {
                'channel': channel,
                'status': 'subscribed',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            current_app.logger.error(f'Subscription error: {e}')
            emit('error', {'message': f'Error subscribing to channel: {str(e)}'})
    
    def handle_unsubscribe(data):
        """Handle channel unsubscription."""
        try:
            client_id = request.sid
            channel = data.get('channel')
            
            if not channel:
                emit('error', {'message': 'Channel name required for unsubscription'})
                return
            
            with _connection_lock:
                # Remove client from channel
                if channel in subscribed_channels:
                    subscribed_channels[channel].discard(client_id)
                    if not subscribed_channels[channel]:
                        del subscribed_channels[channel]
            
            leave_room(channel)
            
            current_app.logger.info(f'Client {client_id} unsubscribed from {channel}')
            
            emit('unsubscribed', {
                'channel': channel,
                'status': 'unsubscribed',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            current_app.logger.error(f'Unsubscription error: {e}')
            emit('error', {'message': f'Error unsubscribing from channel: {str(e)}'})
    
    @socketio.on('connect_error')
    def handle_connect_error(data):
        """Handle connection errors."""
        current_app.logger.error(f'Connection error: {data}')
    
    # Add utility functions for broadcasting messages
    def broadcast_to_channel(channel, message):
        """Broadcast a message to all subscribers of a channel."""
        try:
            socketio.emit('message', message, room=channel)
            current_app.logger.info(f'Broadcast to {channel}: {message}')
        except Exception as e:
            current_app.logger.error(f'Broadcast error: {e}')
    
    # Store broadcast function in app context for use by other modules
    current_app.broadcast_to_channel = broadcast_to_channel
    
    return socketio

def get_connection_stats():
    """Get current connection statistics."""
    with _connection_lock:
        return {
            'active_connections': len(active_connections),
            'subscribed_channels': {channel: len(subscribers) for channel, subscribers in subscribed_channels.items()},
            'total_channels': len(subscribed_channels)
        }
