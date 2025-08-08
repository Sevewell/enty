import sqlite3
import os
from typing import List, Dict, Any, Optional

# データベースファイルのパス
DB_PATH = 'data/enty.db'

def get_connection():
    """データベース接続を取得"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        print('Initializing database...')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # 新しいスキーマを使用
        with open('init.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
                
        conn.commit()
        return conn

# 後方互換性のため
def Connect():
    """後方互換性のためのConnect関数"""
    return get_connection()

class EntityMetaRepository:
    """エンティティクラスのデータアクセス（旧EntityMeta）"""
    
    @staticmethod
    def get_all() -> List[sqlite3.Row]:
        """全てのエンティティクラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT identifier, title
                FROM entity_class
                ORDER BY identifier
            """).fetchall()
    
    @staticmethod
    def get_by_id(entity_class_id: int) -> Optional[sqlite3.Row]:
        """IDでエンティティクラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT identifier, title
                FROM entity_class
                WHERE identifier = ?
            """, (entity_class_id,)).fetchone()
    
    @staticmethod
    def create(title: str) -> int:
        """新しいエンティティクラスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO entity_class (title)
                VALUES (?)
            """, (title,))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(entity_class_id: int, title: str) -> bool:
        """エンティティクラスを更新"""
        with get_connection() as conn:
            cursor = conn.execute("""
                UPDATE entity_class
                SET title = ?
                WHERE identifier = ?
            """, (title, entity_class_id))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(entity_class_id: int) -> bool:
        """エンティティクラスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM entity_class WHERE identifier = ?
            """, (entity_class_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def exists_by_title(title: str) -> bool:
        """同じタイトルのエンティティクラスが存在するかチェック"""
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM entity_class WHERE title = ?
            """, (title,))
            return cursor.fetchone()[0] > 0

class EntityRepository:
    """エンティティインスタンスのデータアクセス（旧Entity）"""
    
    @staticmethod
    def get_all() -> List[sqlite3.Row]:
        """全てのエンティティインスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT e.identifier, e.title, e.date_in, e.date_out, ec.title as type_name
                FROM entity_instance e
                JOIN entity_class ec ON e.class_id = ec.identifier
                ORDER BY e.date_in DESC
            """).fetchall()
    
    @staticmethod
    def get_all_at_date(view_date: str) -> List[sqlite3.Row]:
        """指定日付時点での全てのエンティティインスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT e.identifier, e.title, e.date_in, e.date_out, ec.title as type_name
                FROM entity_instance e
                JOIN entity_class ec ON e.class_id = ec.identifier
                WHERE (e.date_in IS NULL OR e.date_in <= ?)
                  AND (e.date_out IS NULL OR e.date_out > ?)
                ORDER BY e.date_in DESC
            """, (view_date, view_date)).fetchall()
    
    @staticmethod
    def get_by_type(entity_type_id: int) -> List[sqlite3.Row]:
        """特定のタイプのエンティティインスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT e.identifier, e.title, e.date_in, e.date_out, ec.title as type_name
                FROM entity_instance e
                JOIN entity_class ec ON e.class_id = ec.identifier
                WHERE ec.identifier = ?
                ORDER BY e.date_in DESC
            """, (entity_type_id,)).fetchall()
    
    @staticmethod
    def get_by_type_at_date(entity_type_id: int, view_date: str) -> List[sqlite3.Row]:
        """指定日付時点での特定タイプのエンティティインスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT e.identifier, e.title, e.date_in, e.date_out, ec.title as type_name
                FROM entity_instance e
                JOIN entity_class ec ON e.class_id = ec.identifier
                WHERE ec.identifier = ?
                  AND (e.date_in IS NULL OR e.date_in <= ?)
                  AND (e.date_out IS NULL OR e.date_out > ?)
                ORDER BY e.date_in DESC
            """, (entity_type_id, view_date, view_date)).fetchall()
    
    @staticmethod
    def get_by_id(entity_id: int) -> Optional[sqlite3.Row]:
        """IDでエンティティインスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT e.*, ec.title as type_name
                FROM entity_instance e
                JOIN entity_class ec ON e.class_id = ec.identifier
                WHERE e.identifier = ?
            """, (entity_id,)).fetchone()
    
    @staticmethod
    def create(title: str, class_id: int, date_in: str = None, date_out: str = None) -> int:
        """新しいエンティティインスタンスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO entity_instance (title, class_id, date_in, date_out)
                VALUES (?, ?, ?, ?)
            """, (title, class_id, date_in, date_out))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(entity_id: int, title: str = None, class_id: int = None, 
               date_in: str = None, date_out: str = None) -> bool:
        """エンティティインスタンスを更新"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if class_id is not None:
            updates.append("class_id = ?")
            params.append(class_id)
        if date_in is not None:
            updates.append("date_in = ?")
            params.append(date_in)
        if date_out is not None:
            updates.append("date_out = ?")
            params.append(date_out)
        
        if not updates:
            return False
        
        params.append(entity_id)
        
        with get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE entity_instance
                SET {', '.join(updates)}
                WHERE identifier = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(entity_id: int) -> bool:
        """エンティティインスタンスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM entity_instance WHERE identifier = ?
            """, (entity_id,))
            conn.commit()
            return cursor.rowcount > 0

class AttributeRepository:
    """属性インスタンスのデータアクセス（旧Attribute）"""
    
    @staticmethod
    def get_by_entity_id(entity_id: int) -> List[sqlite3.Row]:
        """エンティティIDで属性インスタンスを取得（現在時点）"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    a.identifier,
                    a.title,
                    a.class_id,
                    a.entity_id,
                    a.date_event,
                    ac.title as attr_name,
                    ac.data_type,
                    ac.order_display,
                    CASE 
                        WHEN ac.data_type = 'ENTITY' AND a.title IS NOT NULL 
                        THEN te.title
                        ELSE NULL
                    END as target_entity_title,
                    CASE 
                        WHEN ac.data_type = 'ENTITY' AND a.title IS NOT NULL 
                        THEN CAST(a.title AS INTEGER)
                        ELSE NULL
                    END as target_entity_id
                FROM attribute_instance a
                JOIN attribute_class ac ON a.class_id = ac.identifier
                LEFT JOIN entity_instance te ON (ac.data_type = 'ENTITY' AND CAST(a.title AS INTEGER) = te.identifier)
                WHERE a.entity_id = ?
                ORDER BY COALESCE(ac.order_display, ac.identifier)
            """, (entity_id,)).fetchall()
    
    @staticmethod
    def get_by_entity_id_at_date(entity_id: int, view_date: str) -> List[sqlite3.Row]:
        """エンティティIDで属性インスタンスを取得（指定日付時点での最新値）"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    a.identifier,
                    a.title,
                    a.class_id,
                    a.entity_id,
                    a.date_event,
                    ac.title as attr_name,
                    ac.data_type,
                    ac.order_display,
                    CASE 
                        WHEN ac.data_type = 'ENTITY' AND a.title IS NOT NULL 
                        THEN te.title
                        ELSE NULL
                    END as target_entity_title,
                    CASE 
                        WHEN ac.data_type = 'ENTITY' AND a.title IS NOT NULL 
                        THEN CAST(a.title AS INTEGER)
                        ELSE NULL
                    END as target_entity_id
                FROM attribute_instance a
                JOIN attribute_class ac ON a.class_id = ac.identifier
                LEFT JOIN entity_instance te ON (ac.data_type = 'ENTITY' AND CAST(a.title AS INTEGER) = te.identifier)
                WHERE a.entity_id = ?
                  AND (a.date_event IS NULL OR a.date_event <= ?)
                  AND a.identifier = (
                    SELECT MAX(a2.identifier)
                    FROM attribute_instance a2
                    WHERE a2.entity_id = a.entity_id
                      AND a2.class_id = a.class_id
                      AND (a2.date_event IS NULL OR a2.date_event <= ?)
                  )
                ORDER BY COALESCE(ac.order_display, ac.identifier)
            """, (entity_id, view_date, view_date)).fetchall()
    
    @staticmethod
    def create(title: str, class_id: int, entity_id: int, date_event: str = None) -> int:
        """新しい属性インスタンスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO attribute_instance (title, class_id, entity_id, date_event)
                VALUES (?, ?, ?, ?)
            """, (title, class_id, entity_id, date_event))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(attribute_id: int, title: str = None, date_event: str = None) -> bool:
        """属性インスタンスを更新"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if date_event is not None:
            updates.append("date_event = ?")
            params.append(date_event)
        
        if not updates:
            return False
        
        params.append(attribute_id)
        
        with get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE attribute_instance
                SET {', '.join(updates)}
                WHERE identifier = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(attribute_id: int) -> bool:
        """属性インスタンスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM attribute_instance WHERE identifier = ?
            """, (attribute_id,))
            conn.commit()
            return cursor.rowcount > 0

class AttributeMetaRepository:
    """属性クラスのデータアクセス（旧AttributeMeta）"""
    
    @staticmethod
    def get_by_entity_meta_id(entity_class_id: int) -> List[sqlite3.Row]:
        """エンティティクラスIDで属性クラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    ac.identifier, 
                    ac.title, 
                    ac.entity_id, 
                    ac.data_type, 
                    ac.order_display
                FROM attribute_class ac
                WHERE ac.entity_id = ?
                ORDER BY COALESCE(ac.order_display, ac.identifier)
            """, (entity_class_id,)).fetchall()
    
    @staticmethod
    def get_by_id(attribute_class_id: int) -> Optional[sqlite3.Row]:
        """IDで属性クラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    ac.identifier, 
                    ac.title, 
                    ac.entity_id, 
                    ac.data_type, 
                    ac.order_display
                FROM attribute_class ac
                WHERE ac.identifier = ?
            """, (attribute_class_id,)).fetchone()
    
    @staticmethod
    def create(title: str, entity_id: int, data_type: str, order_display: int = None) -> int:
        """新しい属性クラスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO attribute_class (title, entity_id, data_type, order_display)
                VALUES (?, ?, ?, ?)
            """, (title, entity_id, data_type, order_display))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(attribute_class_id: int, title: str = None, data_type: str = None, order_display: int = None) -> bool:
        """属性クラスを更新"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if data_type is not None:
            updates.append("data_type = ?")
            params.append(data_type)
        if order_display is not None:
            updates.append("order_display = ?")
            params.append(order_display)
        
        if not updates:
            return False
        
        params.append(attribute_class_id)
        
        with get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE attribute_class
                SET {', '.join(updates)}
                WHERE identifier = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(attribute_class_id: int) -> bool:
        """属性クラスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM attribute_class WHERE identifier = ?
            """, (attribute_class_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def exists_by_title_and_entity(title: str, entity_id: int, exclude_id: int = None) -> bool:
        """同じエンティティ内で同じタイトルの属性クラスが存在するかチェック"""
        with get_connection() as conn:
            if exclude_id:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM attribute_class 
                    WHERE title = ? AND entity_id = ? AND identifier != ?
                """, (title, entity_id, exclude_id))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM attribute_class 
                    WHERE title = ? AND entity_id = ?
                """, (title, entity_id))
            return cursor.fetchone()[0] > 0

# 汎用的なデータベースハンドラー（既存コードとの互換性のため）
class DatabaseHandler:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """クエリを実行し、結果を辞書のリストで返す"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """更新系クエリを実行し、影響を受けた行数を返す"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
