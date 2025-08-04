DROP TABLE IF EXISTS entity_class;
DROP TABLE IF EXISTS attribute_class;
DROP TABLE IF EXISTS relation_class;
DROP TABLE IF EXISTS entity_instance;
DROP TABLE IF EXISTS attribute_instance;
DROP TABLE IF EXISTS relation_instance;

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
CREATE TABLE relation_class (
    identifier INTEGER PRIMARY KEY,
    title TEXT,
    from_entity_id INTEGER,
    to_entity_id INTEGER,
    FOREIGN KEY (from_entity_id) REFERENCES entity_class(identifier),
    FOREIGN KEY (to_entity_id) REFERENCES entity_class(identifier)
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
CREATE TABLE relation_instance (
    identifier INTEGER PRIMARY KEY,
    class_id INTEGER,
    entity_from INTEGER,
    entity_to INTEGER,
    date_event TEXT,
    FOREIGN KEY (class_id) REFERENCES relation_class(identifier),
    FOREIGN KEY (entity_from) REFERENCES entity_instance(identifier),
    FOREIGN KEY (entity_to) REFERENCES entity_instance(identifier)
);
