DROP TABLE IF EXISTS entity_class;
DROP TABLE IF EXISTS attribute_class;
DROP TABLE IF EXISTS entity_instance;
DROP TABLE IF EXISTS attribute_instance;

CREATE TABLE entity_class (
    identifier INTEGER PRIMARY KEY,
    title TEXT
);

CREATE TABLE attribute_class (
    identifier INTEGER PRIMARY KEY,
    title TEXT,
    entity_id INTEGER,
    data_type TEXT,
    order_display INTEGER,
    FOREIGN KEY (entity_id) REFERENCES entity_class(identifier)
);

CREATE TABLE entity_instance (
    identifier INTEGER PRIMARY KEY,
    title TEXT,
    class_id INTEGER,
    date_in TEXT,
    date_out TEXT,
    FOREIGN KEY (class_id) REFERENCES entity_class(identifier)
);

CREATE TABLE attribute_instance (
    identifier INTEGER PRIMARY KEY,
    title TEXT,
    class_id INTEGER,
    entity_id INTEGER,
    date_event TEXT,
    FOREIGN KEY (entity_id) REFERENCES entity_instance(identifier),
    FOREIGN KEY (class_id) REFERENCES attribute_class(identifier)
);

-- サンプルデータ
INSERT INTO entity_class (title) VALUES ('サーバー');
INSERT INTO entity_class (title) VALUES ('アプリケーション');
INSERT INTO entity_class (title) VALUES ('データベース');

-- サーバークラスの属性定義
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('ホスト名', 1, 'TEXT', 1);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('IPアドレス', 1, 'TEXT', 2);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('OS', 1, 'TEXT', 3);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('CPU', 1, 'TEXT', 4);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('メモリ', 1, 'TEXT', 5);

-- アプリケーションクラスの属性定義
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('アプリケーション名', 2, 'TEXT', 1);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('バージョン', 2, 'TEXT', 2);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('ポート', 2, 'NUMBER', 3);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('稼働サーバー', 2, 'ENTITY', 4);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('接続DB', 2, 'ENTITY', 5);

-- データベースクラスの属性定義
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('DB名', 3, 'TEXT', 1);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('エンジン', 3, 'TEXT', 2);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('バージョン', 3, 'TEXT', 3);
INSERT INTO attribute_class (title, entity_id, data_type, order_display) VALUES ('稼働サーバー', 3, 'ENTITY', 4);

-- エンティティインスタンス
INSERT INTO entity_instance (title, class_id, date_in) VALUES ('web-server-01', 1, '2023-01-01');
INSERT INTO entity_instance (title, class_id, date_in) VALUES ('web-server-02', 1, '2023-06-01');
INSERT INTO entity_instance (title, class_id, date_in, date_out) VALUES ('db-server-01', 1, '2022-01-01', '2024-06-01');
INSERT INTO entity_instance (title, class_id, date_in) VALUES ('WebShop', 2, '2023-01-15');
INSERT INTO entity_instance (title, class_id, date_in) VALUES ('userdb', 3, '2023-01-01');
INSERT INTO entity_instance (title, class_id, date_in) VALUES ('maindb-v2', 3, '2024-05-15');

-- サーバーの属性インスタンス
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('web-server-01', 1, 1, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('192.168.1.10', 2, 1, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('Ubuntu 20.04', 3, 1, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('Intel Xeon E5-2680', 4, 1, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('32GB', 5, 1, '2023-01-01');

INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('web-server-02', 1, 2, '2023-06-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('192.168.1.11', 2, 2, '2023-06-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('Ubuntu 22.04', 3, 2, '2023-06-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('Intel Xeon Gold 6248', 4, 2, '2023-06-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('64GB', 5, 2, '2023-06-01');

-- アプリケーションの属性インスタンス（ENTITY型はIDを文字列として保存）
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('WebShop', 6, 4, '2023-01-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('1.0.0', 7, 4, '2023-01-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('8080', 8, 4, '2023-01-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('1', 9, 4, '2023-01-15');  -- web-server-01のID
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('5', 10, 4, '2023-01-15'); -- userdbのID

-- アプリケーションのリレーション変更履歴
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('2', 9, 4, '2024-02-01');  -- web-server-02に移行
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('6', 10, 4, '2024-03-01'); -- maindb-v2に移行

-- データベースの属性インスタンス
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('userdb', 11, 5, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('PostgreSQL', 12, 5, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('13.0', 13, 5, '2023-01-01');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('3', 14, 5, '2023-01-01'); -- db-server-01のID（削除されているので表示されない）

INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('maindb-v2', 11, 6, '2024-05-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('PostgreSQL', 12, 6, '2024-05-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('15.0', 13, 6, '2024-05-15');
INSERT INTO attribute_instance (title, class_id, entity_id, date_event) VALUES ('1', 14, 6, '2024-05-15'); -- web-server-01のID
