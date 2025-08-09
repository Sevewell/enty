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
    date_in TEXT,
    date_out TEXT,
    FOREIGN KEY (entity_id) REFERENCES entity_instance(identifier),
    FOREIGN KEY (class_id) REFERENCES attribute_class(identifier)
);