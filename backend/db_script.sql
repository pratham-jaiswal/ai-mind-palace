-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS lifelog;

-- Table: lifelog.users
CREATE TABLE lifelog.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    additional_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: lifelog.documents
CREATE TABLE lifelog.documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES lifelog.users(id) ON DELETE CASCADE,
    filename VARCHAR(512),
    source VARCHAR(128),
    text TEXT,
    additional_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: lifelog.projects
CREATE TABLE lifelog.projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES lifelog.users(id) ON DELETE CASCADE,
    title VARCHAR(512) NOT NULL,
    status VARCHAR(64) DEFAULT 'idea',
    description TEXT,
    additional_info JSON,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function to update last_updated on update
CREATE OR REPLACE FUNCTION lifelog.update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on projects table before update
CREATE TRIGGER trg_update_last_updated
BEFORE UPDATE ON lifelog.projects
FOR EACH ROW EXECUTE FUNCTION lifelog.update_last_updated_column();

-- Table: lifelog.people
CREATE TABLE lifelog.people (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES lifelog.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    notes TEXT,
    additional_info JSON,
    last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: lifelog.decisions
CREATE TABLE lifelog.decisions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES lifelog.users(id) ON DELETE CASCADE,
    decision_name VARCHAR(255) NOT NULL,
    decision_text TEXT NOT NULL,
    additional_info JSON,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: lifelog.chunks
CREATE TABLE lifelog.chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES lifelog.documents(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES lifelog.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    additional_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
