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
        """エンティティIDで属性インスタンスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT a.*, ac.title as attr_name, ac.data_type, ac.order_display
                FROM attribute_instance a
                JOIN attribute_class ac ON a.class_id = ac.identifier
                WHERE a.entity_id = ?
                ORDER BY COALESCE(ac.order_display, ac.identifier)
            """, (entity_id,)).fetchall()
    
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

class RelationRepository:
    """リレーションインスタンスのデータアクセス（旧Relation）"""
    
    @staticmethod
    def get_relations_from(entity_id: int) -> List[sqlite3.Row]:
        """指定エンティティから出るリレーションを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT r.*, e.title as to_entity_title, rc.title as relation_name
                FROM relation_instance r
                JOIN entity_instance e ON r.entity_to = e.identifier
                JOIN relation_class rc ON r.class_id = rc.identifier
                WHERE r.entity_from = ?
            """, (entity_id,)).fetchall()
    
    @staticmethod
    def get_relations_to(entity_id: int) -> List[sqlite3.Row]:
        """指定エンティティに入るリレーションを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT r.*, e.title as from_entity_title, rc.title as relation_name
                FROM relation_instance r
                JOIN entity_instance e ON r.entity_from = e.identifier
                JOIN relation_class rc ON r.class_id = rc.identifier
                WHERE r.entity_to = ?
            """, (entity_id,)).fetchall()
    
    @staticmethod
    def create(class_id: int, entity_from: int, entity_to: int, date_event: str = None) -> int:
        """新しいリレーションインスタンスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO relation_instance (class_id, entity_from, entity_to, date_event)
                VALUES (?, ?, ?, ?)
            """, (class_id, entity_from, entity_to, date_event))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def delete(relation_id: int) -> bool:
        """リレーションインスタンスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM relation_instance WHERE identifier = ?
            """, (relation_id,))
            conn.commit()
            return cursor.rowcount > 0

class AttributeMetaRepository:
    """属性クラスのデータアクセス（旧AttributeMeta）"""
    
    @staticmethod
    def get_by_entity_meta_id(entity_class_id: int) -> List[sqlite3.Row]:
        """エンティティクラスIDで属性クラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT identifier, title, entity_id, data_type, order_display
                FROM attribute_class
                WHERE entity_id = ?
                ORDER BY COALESCE(order_display, identifier)
            """, (entity_class_id,)).fetchall()
    
    @staticmethod
    def get_by_id(attribute_class_id: int) -> Optional[sqlite3.Row]:
        """IDで属性クラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT identifier, title, entity_id, data_type, order_display
                FROM attribute_class
                WHERE identifier = ?
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

class RelationMetaRepository:
    """リレーションクラスのデータアクセス（旧RelationMeta）"""
    
    @staticmethod
    def get_all() -> List[sqlite3.Row]:
        """全てのリレーションクラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT identifier, title, from_entity_id, to_entity_id
                FROM relation_class
                ORDER BY title
            """).fetchall()
    
    @staticmethod
    def get_by_entity_meta_id(entity_class_id: int) -> List[sqlite3.Row]:
        """エンティティクラスIDでリレーションクラスを取得（FROMまたはTOで絡んでいるもの）"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    rc.identifier, 
                    rc.title, 
                    rc.from_entity_id, 
                    rc.to_entity_id,
                    ec_from.title as from_entity_name,
                    ec_to.title as to_entity_name
                FROM relation_class rc
                JOIN entity_class ec_from ON rc.from_entity_id = ec_from.identifier
                JOIN entity_class ec_to ON rc.to_entity_id = ec_to.identifier
                WHERE rc.from_entity_id = ? OR rc.to_entity_id = ?
                ORDER BY rc.title
            """, (entity_class_id, entity_class_id)).fetchall()
    
    @staticmethod
    def get_by_id(relation_class_id: int) -> Optional[sqlite3.Row]:
        """IDでリレーションクラスを取得"""
        with get_connection() as conn:
            return conn.execute("""
                SELECT 
                    rc.identifier, 
                    rc.title, 
                    rc.from_entity_id, 
                    rc.to_entity_id,
                    ec_from.title as from_entity_name,
                    ec_to.title as to_entity_name
                FROM relation_class rc
                JOIN entity_class ec_from ON rc.from_entity_id = ec_from.identifier
                JOIN entity_class ec_to ON rc.to_entity_id = ec_to.identifier
                WHERE rc.identifier = ?
            """, (relation_class_id,)).fetchone()
    
    @staticmethod
    def create(title: str, from_entity_id: int, to_entity_id: int) -> int:
        """新しいリレーションクラスを作成"""
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO relation_class (title, from_entity_id, to_entity_id)
                VALUES (?, ?, ?)
            """, (title, from_entity_id, to_entity_id))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(relation_class_id: int, title: str = None, from_entity_id: int = None, to_entity_id: int = None) -> bool:
        """リレーションクラスを更新"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if from_entity_id is not None:
            updates.append("from_entity_id = ?")
            params.append(from_entity_id)
        if to_entity_id is not None:
            updates.append("to_entity_id = ?")
            params.append(to_entity_id)
        
        if not updates:
            return False
        
        params.append(relation_class_id)
        
        with get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE relation_class
                SET {', '.join(updates)}
                WHERE identifier = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(relation_class_id: int) -> bool:
        """リレーションクラスを削除"""
        with get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM relation_class WHERE identifier = ?
            """, (relation_class_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def exists_by_title_and_entities(title: str, from_entity_id: int, to_entity_id: int, exclude_id: int = None) -> bool:
        """同じタイトルとエンティティ組み合わせのリレーションクラスが存在するかチェック"""
        with get_connection() as conn:
            if exclude_id:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM relation_class 
                    WHERE title = ? AND from_entity_id = ? AND to_entity_id = ? AND identifier != ?
                """, (title, from_entity_id, to_entity_id, exclude_id))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM relation_class 
                    WHERE title = ? AND from_entity_id = ? AND to_entity_id = ?
                """, (title, from_entity_id, to_entity_id))
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
