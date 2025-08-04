#!/usr/bin/env python3
import sys
import os
sys.path.append('/projects/enty')

from db import get_connection

# データベース接続をテスト
try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # テーブル一覧を取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("テーブル一覧:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 各テーブルのスキーマを確認
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}テーブルのスキーマ:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
    
    conn.close()
    print("\nデータベース初期化成功！")
    
except Exception as e:
    print(f"エラー: {e}")
