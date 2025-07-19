"""
Client management system for the Telegram Email Bot
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import config

class ClientManager:
    def __init__(self):
        self.clients_file = config.CLIENTS_FILE
        self.clients_data = self._load_clients()
    
    def _load_clients(self) -> Dict:
        """Load clients data from JSON file"""
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.clients_file):
            return {'next_id': 1, 'clients': {}}
        
        try:
            with open(self.clients_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {'next_id': 1, 'clients': {}}
    
    def _save_clients(self):
        """Save clients data to JSON file"""
        try:
            with open(self.clients_file, 'w') as file:
                json.dump(self.clients_data, file, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save clients data: {e}")
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def add_client(self, user_id: int, name: str, email: str) -> int:
        """Add a new client for a user"""
        # Validate input
        if not name or not name.strip():
            raise ValueError("Client name cannot be empty")
        
        if not email or not email.strip():
            raise ValueError("Client email cannot be empty")
        
        email = email.strip().lower()
        name = name.strip()
        
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        # Check if user exists in clients data
        user_key = str(user_id)
        if user_key not in self.clients_data['clients']:
            self.clients_data['clients'][user_key] = []
        
        user_clients = self.clients_data['clients'][user_key]
        
        # Check client limit
        if len(user_clients) >= config.MAX_CLIENTS_PER_USER:
            raise ValueError(f"Maximum {config.MAX_CLIENTS_PER_USER} clients allowed per user")
        
        # Check for duplicate email
        for client in user_clients:
            if client['email'] == email:
                raise ValueError(f"Client with email {email} already exists")
        
        # Create new client
        client_id = self.clients_data['next_id']
        new_client = {
            'id': client_id,
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        # Add client and update next_id
        user_clients.append(new_client)
        self.clients_data['next_id'] += 1
        
        # Save to file
        self._save_clients()
        
        return client_id
    
    def get_user_clients(self, user_id: int) -> List[Dict]:
        """Get all clients for a user"""
        user_key = str(user_id)
        return self.clients_data['clients'].get(user_key, [])
    
    def get_client(self, user_id: int, client_id: int) -> Optional[Dict]:
        """Get a specific client by ID for a user"""
        user_clients = self.get_user_clients(user_id)
        
        for client in user_clients:
            if client['id'] == client_id:
                return client
        
        return None
    
    def remove_client(self, user_id: int, client_id: int) -> Dict:
        """Remove a client by ID for a user"""
        user_key = str(user_id)
        user_clients = self.clients_data['clients'].get(user_key, [])
        
        for i, client in enumerate(user_clients):
            if client['id'] == client_id:
                removed_client = user_clients.pop(i)
                self._save_clients()
                return removed_client
        
        raise ValueError(f"Client with ID {client_id} not found")
    
    def update_client(self, user_id: int, client_id: int, name: str = None, email: str = None) -> Dict:
        """Update a client's information"""
        client = self.get_client(user_id, client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        user_key = str(user_id)
        user_clients = self.clients_data['clients'][user_key]
        
        # Find and update the client
        for i, c in enumerate(user_clients):
            if c['id'] == client_id:
                if name is not None:
                    if not name.strip():
                        raise ValueError("Client name cannot be empty")
                    c['name'] = name.strip()
                
                if email is not None:
                    email = email.strip().lower()
                    if not self._validate_email(email):
                        raise ValueError("Invalid email format")
                    
                    # Check for duplicate email (excluding current client)
                    for other_client in user_clients:
                        if other_client['id'] != client_id and other_client['email'] == email:
                            raise ValueError(f"Client with email {email} already exists")
                    
                    c['email'] = email
                
                c['updated_at'] = datetime.now().isoformat()
                self._save_clients()
                return c
        
        raise ValueError(f"Client with ID {client_id} not found")
    
    def search_clients(self, user_id: int, query: str) -> List[Dict]:
        """Search clients by name or email"""
        user_clients = self.get_user_clients(user_id)
        query = query.lower().strip()
        
        if not query:
            return user_clients
        
        results = []
        for client in user_clients:
            if (query in client['name'].lower() or 
                query in client['email'].lower()):
                results.append(client)
        
        return results
    
    def get_total_clients(self) -> int:
        """Get total number of clients across all users"""
        total = 0
        for user_clients in self.clients_data['clients'].values():
            total += len(user_clients)
        return total
