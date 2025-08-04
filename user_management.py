from functools import wraps
from flask import session, redirect, url_for, flash, g
import sqlite3
from datetime import datetime

class UserManager:
    def __init__(self, db_path='aggre.db'):
        self.db_path = db_path
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_or_create_user(self, user_info):
        """ユーザーを取得または作成"""
        conn = self.get_db_connection()
        try:
            # 既存ユーザーを検索
            user = conn.execute(
                'SELECT * FROM users WHERE provider_id = ? AND provider = ?',
                (user_info['id'], user_info['provider'])
            ).fetchone()
            
            if user:
                # 既存ユーザーの情報を更新
                conn.execute('''
                    UPDATE users 
                    SET email = ?, name = ?, picture = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    user_info['email'],
                    user_info['name'],
                    user_info.get('picture'),
                    datetime.now(),
                    user['id']
                ))
                conn.commit()
                return dict(user)
            else:
                # 新しいユーザーを作成
                cursor = conn.execute('''
                    INSERT INTO users (provider_id, provider, email, name, picture)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_info['id'],
                    user_info['provider'],
                    user_info['email'],
                    user_info['name'],
                    user_info.get('picture')
                ))
                conn.commit()
                
                # 新規ユーザーには 'viewer' ロールを自動付与
                user_id = cursor.lastrowid
                self.assign_role(user_id, 'viewer')
                
                return self.get_user_by_id(user_id)
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """IDでユーザーを取得"""
        conn = self.get_db_connection()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_user_roles(self, user_id):
        """ユーザーのロールを取得"""
        conn = self.get_db_connection()
        try:
            roles = conn.execute('''
                SELECT r.name, r.display_name, r.description
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ? AND ur.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > datetime('now'))
            ''', (user_id,)).fetchall()
            return [dict(role) for role in roles]
        finally:
            conn.close()
    
    def get_user_permissions(self, user_id):
        """ユーザーの権限を取得"""
        conn = self.get_db_connection()
        try:
            permissions = conn.execute('''
                SELECT DISTINCT p.name, p.resource, p.action
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN roles r ON rp.role_id = r.id
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ? AND ur.is_active = TRUE AND p.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > datetime('now'))
            ''', (user_id,)).fetchall()
            return [dict(perm) for perm in permissions]
        finally:
            conn.close()
    
    def has_permission(self, user_id, permission_name):
        """ユーザーが特定の権限を持っているかチェック"""
        permissions = self.get_user_permissions(user_id)
        return any(perm['name'] == permission_name for perm in permissions)
    
    def has_role(self, user_id, role_name):
        """ユーザーが特定のロールを持っているかチェック"""
        roles = self.get_user_roles(user_id)
        return any(role['name'] == role_name for role in roles)
    
    def assign_role(self, user_id, role_name, granted_by=None):
        """ユーザーにロールを付与"""
        conn = self.get_db_connection()
        try:
            # ロールIDを取得
            role = conn.execute(
                'SELECT id FROM roles WHERE name = ?',
                (role_name,)
            ).fetchone()
            
            if not role:
                raise ValueError(f"Role '{role_name}' not found")
            
            # 既存の関連があるかチェック
            existing = conn.execute(
                'SELECT id FROM user_roles WHERE user_id = ? AND role_id = ?',
                (user_id, role['id'])
            ).fetchone()
            
            if existing:
                # 既存の関連を有効化
                conn.execute(
                    'UPDATE user_roles SET is_active = TRUE WHERE id = ?',
                    (existing['id'],)
                )
            else:
                # 新しい関連を作成
                conn.execute(
                    'INSERT INTO user_roles (user_id, role_id, granted_by) VALUES (?, ?, ?)',
                    (user_id, role['id'], granted_by)
                )
            
            conn.commit()
        finally:
            conn.close()
    
    def revoke_role(self, user_id, role_name):
        """ユーザーからロールを取り消し"""
        conn = self.get_db_connection()
        try:
            conn.execute('''
                UPDATE user_roles 
                SET is_active = FALSE 
                WHERE user_id = ? AND role_id = (
                    SELECT id FROM roles WHERE name = ?
                )
            ''', (user_id, role_name))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_users(self):
        """全ユーザーを取得"""
        conn = self.get_db_connection()
        try:
            users = conn.execute('''
                SELECT u.*, GROUP_CONCAT(r.display_name, ', ') as roles
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = TRUE
                LEFT JOIN roles r ON ur.role_id = r.id
                WHERE u.is_active = TRUE
                GROUP BY u.id
                ORDER BY u.created_at DESC
            ''').fetchall()
            return [dict(user) for user in users]
        finally:
            conn.close()

# デコレーター関数
def login_required(f):
    """ログイン必須のデコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('ログインが必要です', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """特定のロールが必要なデコレーター"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_manager = UserManager()
            db_user = user_manager.get_or_create_user(session['user'])
            
            if not user_manager.has_role(db_user['id'], role_name):
                flash(f'この機能には{role_name}ロールが必要です', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission_name):
    """特定の権限が必要なデコレーター"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_manager = UserManager()
            db_user = user_manager.get_or_create_user(session['user'])
            
            if not user_manager.has_permission(db_user['id'], permission_name):
                flash(f'この機能には{permission_name}権限が必要です', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# リクエストごとに現在のユーザー情報を設定
def load_user():
    """各リクエストで現在のユーザー情報を g に設定"""
    if 'user' in session:
        user_manager = UserManager()
        g.current_user = user_manager.get_or_create_user(session['user'])
        g.user_roles = user_manager.get_user_roles(g.current_user['id'])
        g.user_permissions = user_manager.get_user_permissions(g.current_user['id'])
    else:
        g.current_user = None
        g.user_roles = []
        g.user_permissions = []
