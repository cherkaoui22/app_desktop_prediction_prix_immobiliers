"""
=============================================================================
FICHIER : src/database.py
RÔLE    : Gestion de la base de données MySQL (avec fallback SQLite)
          - Connexion MySQL via mysql-connector-python
          - Fallback automatique sur SQLite si MySQL indisponible
          - Tables : users, predictions, properties, messages
          - Sécurité : bcrypt pour les mots de passe
          - Protection anti-injection SQL via requêtes paramétrées
=============================================================================
"""
import sqlite3
import hashlib
import os
import json
import datetime
from typing import Optional, Dict, List, Any

# Essayer mysql-connector, fallback sqlite
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# Essayer bcrypt, fallback sha256
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'app.db')

# Config MySQL par défaut (XAMPP)
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'desktop_db_Imob'
}


class Database:
    """
    Gestionnaire de base de données.
    Priorité : MySQL → SQLite (fallback automatique)
    """

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_type = None  # 'mysql' ou 'sqlite'

    # ─────────────────────────────────────────────────────────────────
    # Connexion
    # ─────────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Tente MySQL puis SQLite en fallback."""
        if MYSQL_AVAILABLE:
            try:
                self.conn = mysql.connector.connect(**MYSQL_CONFIG)
                self.cursor = self.conn.cursor(dictionary=True)
                self.db_type = 'mysql'
                print("[DB] Connecté à MySQL")
                self.create_tables()
                return True
            except Exception as e:
                print(f"[DB] MySQL indisponible ({e}), bascule sur SQLite")

        # Fallback SQLite
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.db_type = 'sqlite'
            print("[DB] Connecté à SQLite (mode local)")
            self.create_tables()
            return True
        except Exception as e:
            print(f"[DB] Erreur SQLite : {e}")
            return False

    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

    def _execute(self, query: str, params: tuple = ()) -> bool:
        """Exécute une requête avec gestion des erreurs."""
        try:
            if self.db_type == 'sqlite':
                query = query.replace('%s', '?')
            self.cursor.execute(query, params)
            if self.db_type == 'sqlite':
                self.conn.commit()
            else:
                self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Erreur requête : {e}")
            return False

    def _fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch tous les résultats."""
        try:
            if self.db_type == 'sqlite':
                query = query.replace('%s', '?')
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            if self.db_type == 'sqlite':
                return [dict(r) for r in rows]
            return rows or []
        except Exception as e:
            print(f"[DB] Erreur fetch : {e}")
            return []

    def _fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch un seul résultat."""
        rows = self._fetchall(query, params)
        return rows[0] if rows else None

    # ─────────────────────────────────────────────────────────────────
    # Création des tables
    # ─────────────────────────────────────────────────────────────────

    def create_tables(self):
        """Crée toutes les tables nécessaires."""
        AUTO_INC = "AUTO_INCREMENT" if self.db_type == 'mysql' else "AUTOINCREMENT"
        INT_PK = f"INT PRIMARY KEY {AUTO_INC}" if self.db_type == 'mysql' else "INTEGER PRIMARY KEY AUTOINCREMENT"

        tables = [
            f"""
            CREATE TABLE IF NOT EXISTS users (
                id {INT_PK},
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                avatar_path VARCHAR(255),
                phone VARCHAR(30),
                city VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )""",
            f"""
            CREATE TABLE IF NOT EXISTS predictions (
                id {INT_PK},
                user_id INT NOT NULL,
                area FLOAT,
                bedrooms INT,
                bathrooms INT,
                stories INT,
                parking INT,
                mainroad INT DEFAULT 0,
                guestroom INT DEFAULT 0,
                basement INT DEFAULT 0,
                hotwaterheating INT DEFAULT 0,
                airconditioning INT DEFAULT 0,
                prefarea INT DEFAULT 0,
                furnishingstatus INT DEFAULT 1,
                model_used VARCHAR(50),
                predicted_price FLOAT,
                price_category VARCHAR(30),
                ai_message TEXT,
                photo_path VARCHAR(255),
                confirmed INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""
            CREATE TABLE IF NOT EXISTS properties (
                id {INT_PK},
                user_id INT NOT NULL,
                title VARCHAR(200),
                description TEXT,
                property_type VARCHAR(50),
                transaction_type VARCHAR(20),
                price FLOAT,
                area FLOAT,
                bedrooms INT,
                bathrooms INT,
                city VARCHAR(100),
                address TEXT,
                photos TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                admin_validated INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""
            CREATE TABLE IF NOT EXISTS messages (
                id {INT_PK},
                sender_id INT NOT NULL,
                receiver_id INT NOT NULL,
                property_id INT,
                content TEXT NOT NULL,
                is_read INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
        ]

        for sql in tables:
            self._execute(sql)

        # Créer admin par défaut
        self._create_default_admin()

    def _create_default_admin(self):
        """Crée le compte admin si inexistant."""
        existing = self._fetchone("SELECT id FROM users WHERE email = %s", ('admin@realestate.ai',))
        if not existing:
            hashed = self.hash_password('Admin2025!')
            self._execute(
                "INSERT INTO users (email, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                ('admin@realestate.ai', hashed, 'Administrateur', 'admin')
            )
            print("[DB] Admin créé : admin@realestate.ai / Admin2025!")

    # ─────────────────────────────────────────────────────────────────
    # Sécurité
    # ─────────────────────────────────────────────────────────────────

    def hash_password(self, password: str) -> str:
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        if BCRYPT_AVAILABLE:
            try:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception:
                pass
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    # ─────────────────────────────────────────────────────────────────
    # Utilisateurs
    # ─────────────────────────────────────────────────────────────────

    def register_user(self, email: str, password: str, full_name: str = '') -> Dict:
        """Inscrit un nouvel utilisateur."""
        import re
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return {'success': False, 'error': 'Email invalide'}
        if len(password) < 6:
            return {'success': False, 'error': 'Mot de passe trop court (6 car. min)'}
        if self._fetchone("SELECT id FROM users WHERE email = %s", (email,)):
            return {'success': False, 'error': 'Email déjà utilisé'}

        hashed = self.hash_password(password)
        ok = self._execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)",
            (email, hashed, full_name)
        )
        if ok:
            user = self._fetchone("SELECT * FROM users WHERE email = %s", (email,))
            return {'success': True, 'user': dict(user)}
        return {'success': False, 'error': 'Erreur création compte'}

    def login_user(self, email: str, password: str) -> Dict:
        """Authentifie un utilisateur."""
        user = self._fetchone("SELECT * FROM users WHERE email = %s", (email,))
        if not user:
            return {'success': False, 'error': 'Email introuvable'}
        if not self.verify_password(password, user['password_hash']):
            return {'success': False, 'error': 'Mot de passe incorrect'}
        # Màj last_login
        self._execute("UPDATE users SET last_login = %s WHERE id = %s",
                      (datetime.datetime.now(), user['id']))
        return {'success': True, 'user': dict(user)}

    def update_user_profile(self, user_id: int, data: Dict) -> bool:
        fields = []
        values = []
        allowed = ['full_name', 'phone', 'city', 'avatar_path']
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = %s")
                values.append(v)
        if not fields:
            return False
        values.append(user_id)
        return self._execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = %s", tuple(values)
        )

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        return self._fetchone("SELECT * FROM users WHERE id = %s", (user_id,))

    def get_all_users(self) -> List[Dict]:
        return self._fetchall("SELECT id, email, full_name, role, city, created_at, last_login FROM users ORDER BY created_at DESC")

    def delete_user(self, user_id: int) -> bool:
        return self._execute("DELETE FROM users WHERE id = %s", (user_id,))

    # ─────────────────────────────────────────────────────────────────
    # Prédictions
    # ─────────────────────────────────────────────────────────────────

    def save_prediction(self, user_id: int, data: Dict) -> bool:
        return self._execute("""
            INSERT INTO predictions
            (user_id, area, bedrooms, bathrooms, stories, parking,
             mainroad, guestroom, basement, hotwaterheating, airconditioning,
             prefarea, furnishingstatus, model_used, predicted_price,
             price_category, ai_message, photo_path, confirmed)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            data.get('area', 0), data.get('bedrooms', 1),
            data.get('bathrooms', 1), data.get('stories', 1),
            data.get('parking', 0), data.get('mainroad', 0),
            data.get('guestroom', 0), data.get('basement', 0),
            data.get('hotwaterheating', 0), data.get('airconditioning', 0),
            data.get('prefarea', 0), data.get('furnishingstatus', 1),
            data.get('model_used', 'linear_regression'),
            data.get('predicted_price', 0),
            data.get('price_category', ''),
            data.get('ai_message', ''),
            data.get('photo_path', ''),
            data.get('confirmed', 0)
        ))

    def get_user_predictions(self, user_id: int) -> List[Dict]:
        return self._fetchall(
            "SELECT * FROM predictions WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )

    def get_all_predictions(self) -> List[Dict]:
        return self._fetchall("""
            SELECT p.*, u.email, u.full_name
            FROM predictions p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """)

    def get_prediction_count(self, user_id: int) -> int:
        row = self._fetchone("SELECT COUNT(*) as cnt FROM predictions WHERE user_id = %s", (user_id,))
        return row['cnt'] if row else 0

    # ─────────────────────────────────────────────────────────────────
    # Propriétés (annonces)
    # ─────────────────────────────────────────────────────────────────

    def create_property(self, user_id: int, data: Dict) -> bool:
        return self._execute("""
            INSERT INTO properties
            (user_id, title, description, property_type, transaction_type,
             price, area, bedrooms, bathrooms, city, address, photos, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id, data.get('title', ''), data.get('description', ''),
            data.get('property_type', 'appartement'), data.get('transaction_type', 'vente'),
            data.get('price', 0), data.get('area', 0),
            data.get('bedrooms', 1), data.get('bathrooms', 1),
            data.get('city', ''), data.get('address', ''),
            data.get('photos', ''), 'pending'
        ))

    def get_properties(self, filters: Dict = None) -> List[Dict]:
        query = """
            SELECT p.*, u.email, u.full_name, u.phone
            FROM properties p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.admin_validated = 1
        """
        params = []
        if filters:
            if filters.get('type'):
                query += " AND p.transaction_type = %s"
                params.append(filters['type'])
            if filters.get('city'):
                query += " AND p.city LIKE %s"
                params.append(f"%{filters['city']}%")
            if filters.get('min_price'):
                query += " AND p.price >= %s"
                params.append(filters['min_price'])
            if filters.get('max_price'):
                query += " AND p.price <= %s"
                params.append(filters['max_price'])
        query += " ORDER BY p.created_at DESC"
        return self._fetchall(query, tuple(params))

    def get_pending_properties(self) -> List[Dict]:
        return self._fetchall("""
            SELECT p.*, u.email, u.full_name
            FROM properties p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.admin_validated = 0
            ORDER BY p.created_at DESC
        """)

    def validate_property(self, prop_id: int, validated: bool) -> bool:
        return self._execute(
            "UPDATE properties SET admin_validated = %s, status = %s WHERE id = %s",
            (1 if validated else 0, 'active' if validated else 'rejected', prop_id)
        )

    def get_user_properties(self, user_id: int) -> List[Dict]:
        return self._fetchall(
            "SELECT * FROM properties WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )

    # ─────────────────────────────────────────────────────────────────
    # Messages
    # ─────────────────────────────────────────────────────────────────

    def send_message(self, sender_id: int, receiver_id: int, content: str, property_id: int = None) -> bool:
        return self._execute(
            "INSERT INTO messages (sender_id, receiver_id, property_id, content) VALUES (%s,%s,%s,%s)",
            (sender_id, receiver_id, property_id, content)
        )

    def get_messages_for_user(self, user_id: int) -> List[Dict]:
        return self._fetchall("""
            SELECT m.*, 
                   s.email as sender_email, s.full_name as sender_name,
                   r.email as receiver_email, r.full_name as receiver_name
            FROM messages m
            LEFT JOIN users s ON m.sender_id = s.id
            LEFT JOIN users r ON m.receiver_id = r.id
            WHERE m.receiver_id = %s OR m.sender_id = %s
            ORDER BY m.created_at DESC
        """, (user_id, user_id))

    def get_admin_messages(self) -> List[Dict]:
        admin = self._fetchone("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        if not admin:
            return []
        return self.get_messages_for_user(admin['id'])

    def mark_messages_read(self, receiver_id: int):
        self._execute("UPDATE messages SET is_read = 1 WHERE receiver_id = %s", (receiver_id,))

    # ─────────────────────────────────────────────────────────────────
    # Stats admin
    # ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        total_users = self._fetchone("SELECT COUNT(*) as c FROM users WHERE role != 'admin'")
        total_preds = self._fetchone("SELECT COUNT(*) as c FROM predictions")
        total_props = self._fetchone("SELECT COUNT(*) as c FROM properties")
        pending     = self._fetchone("SELECT COUNT(*) as c FROM properties WHERE admin_validated = 0")
        avg_price   = self._fetchone("SELECT AVG(predicted_price) as a FROM predictions WHERE confirmed = 1")
        return {
            'total_users':  total_users['c'] if total_users else 0,
            'total_preds':  total_preds['c'] if total_preds else 0,
            'total_props':  total_props['c'] if total_props else 0,
            'pending_props': pending['c'] if pending else 0,
            'avg_price':    avg_price['a'] or 0 if avg_price else 0,
        }


# Instance singleton
db = Database()