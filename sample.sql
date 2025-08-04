-- 人と部署のサンプルデータ登録
-- aggre.db用サンプルSQL

-- 1. エンティティタイプの定義
INSERT INTO entity_meta (identifier, title) VALUES 
(1, '人'),
(2, '部署');

-- 2. 属性タイプの定義
-- 人の属性
INSERT INTO attribute_meta (identifier, entity_meta_id, title, data_type) VALUES 
(1, 1, '氏名', 'TEXT'),
(2, 1, '年齢', 'INTEGER'),
(3, 1, 'メールアドレス', 'TEXT'),
(4, 1, '入社日', 'DATE'),
(5, 1, '職位', 'TEXT');

-- 部署の属性
INSERT INTO attribute_meta (identifier, entity_meta_id, title, data_type) VALUES 
(6, 2, '部署名', 'TEXT'),
(7, 2, '予算', 'INTEGER'),
(8, 2, '設立日', 'DATE'),
(9, 2, '責任者', 'TEXT'),
(10, 2, '場所', 'TEXT');

-- 3. 関係タイプの定義
INSERT INTO relation_meta (identifier, entity_meta_from, entity_meta_to, title) VALUES 
(1, 1, 2, '所属'),
(2, 1, 1, '上司部下'),
(3, 2, 2, '上位下位部署');

-- 4. 実際のエンティティ（人）の登録
INSERT INTO entity (identifier, meta_id, title, date_in, date_out) VALUES 
(1, 1, '田中太郎', '2020-04-01', NULL),
(2, 1, '佐藤花子', '2019-07-01', NULL),
(3, 1, '山田次郎', '2021-01-15', NULL),
(4, 1, '鈴木美咲', '2022-03-01', NULL),
(5, 1, '高橋健一', '2018-04-01', NULL);

-- 5. 実際のエンティティ（部署）の登録
INSERT INTO entity (identifier, meta_id, title, date_in, date_out) VALUES 
(6, 2, '営業部', '2015-04-01', NULL),
(7, 2, '開発部', '2015-04-01', NULL),
(8, 2, '人事部', '2015-04-01', NULL),
(9, 2, '営業第一課', '2018-04-01', NULL),
(10, 2, '営業第二課', '2020-04-01', NULL);

-- 6. 人の属性値
-- 田中太郎の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(1, 1, 1, '田中太郎', '2020-04-01'),
(2, 1, 2, '28', '2020-04-01'),
(3, 1, 3, 'tanaka@company.com', '2020-04-01'),
(4, 1, 4, '2020-04-01', '2020-04-01'),
(5, 1, 5, '主任', '2023-04-01');

-- 佐藤花子の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(6, 2, 1, '佐藤花子', '2019-07-01'),
(7, 2, 2, '32', '2019-07-01'),
(8, 2, 3, 'sato@company.com', '2019-07-01'),
(9, 2, 4, '2019-07-01', '2019-07-01'),
(10, 2, 5, '課長', '2022-04-01');

-- 山田次郎の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(11, 3, 1, '山田次郎', '2021-01-15'),
(12, 3, 2, '25', '2021-01-15'),
(13, 3, 3, 'yamada@company.com', '2021-01-15'),
(14, 3, 4, '2021-01-15', '2021-01-15'),
(15, 3, 5, '一般', '2021-01-15');

-- 鈴木美咲の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(16, 4, 1, '鈴木美咲', '2022-03-01'),
(17, 4, 2, '26', '2022-03-01'),
(18, 4, 3, 'suzuki@company.com', '2022-03-01'),
(19, 4, 4, '2022-03-01', '2022-03-01'),
(20, 4, 5, '一般', '2022-03-01');

-- 高橋健一の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(21, 5, 1, '高橋健一', '2018-04-01'),
(22, 5, 2, '35', '2018-04-01'),
(23, 5, 3, 'takahashi@company.com', '2018-04-01'),
(24, 5, 4, '2018-04-01', '2018-04-01'),
(25, 5, 5, '部長', '2020-04-01');

-- 7. 部署の属性値
-- 営業部の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(26, 6, 6, '営業部', '2015-04-01'),
(27, 6, 7, '50000000', '2024-04-01'),
(28, 6, 8, '2015-04-01', '2015-04-01'),
(29, 6, 9, '高橋健一', '2020-04-01'),
(30, 6, 10, '本社3階', '2015-04-01');

-- 開発部の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(31, 7, 6, '開発部', '2015-04-01'),
(32, 7, 7, '80000000', '2024-04-01'),
(33, 7, 8, '2015-04-01', '2015-04-01'),
(34, 7, 9, '未定', '2015-04-01'),
(35, 7, 10, '本社4階', '2015-04-01');

-- 人事部の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(36, 8, 6, '人事部', '2015-04-01'),
(37, 8, 7, '30000000', '2024-04-01'),
(38, 8, 8, '2015-04-01', '2015-04-01'),
(39, 8, 9, '未定', '2015-04-01'),
(40, 8, 10, '本社2階', '2015-04-01');

-- 営業第一課の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(41, 9, 6, '営業第一課', '2018-04-01'),
(42, 9, 7, '20000000', '2024-04-01'),
(43, 9, 8, '2018-04-01', '2018-04-01'),
(44, 9, 9, '佐藤花子', '2022-04-01'),
(45, 9, 10, '本社3階', '2018-04-01');

-- 営業第二課の属性
INSERT INTO attribute (identifier, entity_id, meta_id, title, date_event) VALUES 
(46, 10, 6, '営業第二課', '2020-04-01'),
(47, 10, 7, '15000000', '2024-04-01'),
(48, 10, 8, '2020-04-01', '2020-04-01'),
(49, 10, 9, '未定', '2020-04-01'),
(50, 10, 10, '本社3階', '2020-04-01');

-- 8. 関係の定義
-- 人の部署所属関係
INSERT INTO relation (identifier, meta_id, entity_from, entity_to, date_event) VALUES 
(1, 1, 1, 9, '2020-04-01'),  -- 田中太郎 → 営業第一課
(2, 1, 2, 9, '2019-07-01'),  -- 佐藤花子 → 営業第一課
(3, 1, 3, 10, '2021-01-15'), -- 山田次郎 → 営業第二課
(4, 1, 4, 7, '2022-03-01'),  -- 鈴木美咲 → 開発部
(5, 1, 5, 6, '2018-04-01');  -- 高橋健一 → 営業部

-- 上司部下関係
INSERT INTO relation (identifier, meta_id, entity_from, entity_to, date_event) VALUES 
(6, 2, 2, 1, '2022-04-01'),  -- 佐藤花子(課長) → 田中太郎(主任)
(7, 2, 5, 2, '2020-04-01');  -- 高橋健一(部長) → 佐藤花子(課長)

-- 部署の上位下位関係
INSERT INTO relation (identifier, meta_id, entity_from, entity_to, date_event) VALUES 
(8, 3, 6, 9, '2018-04-01'),  -- 営業部 → 営業第一課
(9, 3, 6, 10, '2020-04-01'); -- 営業部 → 営業第二課

-- サンプルデータ登録完了
