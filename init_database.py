import sqlite3
import os

# データベースファイルのパス
DB_PATH = '/projects/enty/data/enty.db'

def test_database():
    # データディレクトリを作成
    if not os.path.exists('/projects/enty/data'):
        os.makedirs('/projects/enty/data')
    
    # 既存のデータベースファイルを削除（テスト用）
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("既存のデータベースファイルを削除しました")
    
    # 新しいデータベースを作成
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 新しいスキーマを読み込んで実行
    with open('/projects/enty/init_new_fixed.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    
    # テーブル一覧を確認
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("作成されたテーブル:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
    print("データベース初期化完了！")

if __name__ == "__main__":
    test_database()
