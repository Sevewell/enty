-- 日付時点フィルタリング機能テスト用サンプルデータ
-- 新しいスキーマ（entity_class, entity_instanceなど）に対応

-- 1. エンティティクラスの定義
INSERT INTO entity_class (title) VALUES 
('サーバー'),
('アプリケーション'),
('データベース');

-- 2. 属性クラスの定義
-- サーバーの属性
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES 
('ホスト名', 1, 'TEXT', 1),
('IPアドレス', 1, 'TEXT', 2),
('OS', 1, 'TEXT', 3),
('CPU', 1, 'TEXT', 4),
('メモリ', 1, 'TEXT', 5);

-- アプリケーションの属性
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES 
('アプリ名', 2, 'TEXT', 1),
('バージョン', 2, 'TEXT', 2),
('ポート', 2, 'number', 3),
('URL', 2, 'url', 4);

-- データベースの属性
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES 
('DB名', 3, 'TEXT', 1),
('エンジン', 3, 'TEXT', 2),
('バージョン', 3, 'TEXT', 3);

-- 3. リレーションクラスの定義
INSERT INTO relation_class (title, from_entity_id, to_entity_id) VALUES 
('稼働', 2, 1),  -- アプリケーション → サーバー
('接続', 2, 3);  -- アプリケーション → データベース

-- 4. エンティティインスタンスの登録（時系列データ）
-- サーバー
INSERT INTO entity_instance (title, class_id, date_in, date_out) VALUES 
('web-server-01', 1, '2023-01-01', NULL),
('web-server-02', 1, '2023-06-01', NULL),
('db-server-01', 1, '2022-01-01', '2024-06-01'),  -- 廃止されたサーバー
('db-server-02', 1, '2024-05-01', NULL),  -- 新しいサーバー
('app-server-01', 1, '2023-03-01', NULL);

-- アプリケーション
INSERT INTO entity_instance (title, class_id, date_in, date_out) VALUES 
('WebShop', 2, '2023-01-15', NULL),
('UserAPI', 2, '2023-02-01', '2024-01-01'),  -- 廃止されたアプリ
('UserAPI-v2', 2, '2023-12-01', NULL),  -- 新バージョン
('AdminPanel', 2, '2023-03-15', NULL),
('BatchProcessor', 2, '2023-04-01', NULL);

-- データベース
INSERT INTO entity_instance (title, class_id, date_in, date_out) VALUES 
('maindb', 3, '2022-01-01', '2024-06-01'),  -- 古いDB
('maindb-v2', 3, '2024-05-15', NULL),  -- 新しいDB
('userdb', 3, '2023-01-01', NULL),
('logdb', 3, '2023-02-01', NULL);

-- 5. 属性インスタンスの登録
-- web-server-01の属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('web-server-01', 1, 1, '2023-01-01'),
('192.168.1.10', 2, 1, '2023-01-01'),
('Ubuntu 20.04', 3, 1, '2023-01-01'),
('Intel Xeon E5-2680', 4, 1, '2023-01-01'),
('32GB', 5, 1, '2023-01-01');

-- web-server-02の属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('web-server-02', 1, 2, '2023-06-01'),
('192.168.1.11', 2, 2, '2023-06-01'),
('Ubuntu 22.04', 3, 2, '2023-06-01'),
('Intel Xeon Gold 6248', 4, 2, '2023-06-01'),
('64GB', 5, 2, '2023-06-01');

-- db-server-01の属性（廃止済み）
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('db-server-01', 1, 3, '2022-01-01'),
('192.168.1.20', 2, 3, '2022-01-01'),
('CentOS 7', 3, 3, '2022-01-01');

-- db-server-02の属性（新サーバー）
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('db-server-02', 1, 4, '2024-05-01'),
('192.168.1.21', 2, 4, '2024-05-01'),
('Ubuntu 22.04', 3, 4, '2024-05-01');

-- WebShopアプリの属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('WebShop', 6, 6, '2023-01-15'),
('v1.0.0', 7, 6, '2023-01-15'),
('80', 8, 6, '2023-01-15'),
('https://webshop.company.com', 9, 6, '2023-01-15');

-- UserAPI v2の属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('UserAPI', 6, 8, '2023-12-01'),
('v2.0.0', 7, 8, '2023-12-01'),
('8080', 8, 8, '2023-12-01'),
('https://api.company.com/user', 9, 8, '2023-12-01');

-- maindb-v2の属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('maindb-v2', 10, 11, '2024-05-15'),
('PostgreSQL', 11, 11, '2024-05-15'),
('15.3', 12, 11, '2024-05-15');

-- userdbの属性
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES 
('userdb', 10, 12, '2023-01-01'),
('MySQL', 11, 12, '2023-01-01'),
('8.0', 12, 12, '2023-01-01');

-- 6. リレーションインスタンスの登録
-- アプリケーション → サーバー（稼働関係）
INSERT INTO relation_instance (class_id, entity_from, entity_to, date_event) VALUES 
(1, 6, 1, '2023-01-15'),  -- WebShop → web-server-01
(1, 8, 2, '2023-12-01'),  -- UserAPI-v2 → web-server-02
(1, 9, 5, '2023-03-15');  -- AdminPanel → app-server-01

-- アプリケーション → データベース（接続関係）
INSERT INTO relation_instance (class_id, entity_from, entity_to, date_event) VALUES 
(2, 6, 12, '2023-01-15'),  -- WebShop → userdb
(2, 8, 11, '2023-12-15'),  -- UserAPI-v2 → maindb-v2
(2, 9, 12, '2023-03-15');  -- AdminPanel → userdb

-- サンプルデータ登録完了
