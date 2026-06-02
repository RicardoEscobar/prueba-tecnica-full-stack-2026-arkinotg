/*
db.sql
DB Engine: SQLite3
This is the Data Definition Language (DDL) file for the insurance policies database.
*/
--Drop tables if they already exist
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS advisors;
DROP TABLE IF EXISTS contact_attempts;


CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS advisors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    insurer TEXT NOT NULL,
    expiration_date TEXT NOT NULL, -- A text string that is one of the ISO 8601 date/time values shown in items 1 through 10 below. Example: '2025-05-29 14:16:00'
    status INTEGER NOT NULL CHECK(status IN (1, 0)), -- An integer that is either 1 (managed) or 0 (not managed)
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (advisor_id) REFERENCES advisors(id)
);

CREATE TABLE IF NOT EXISTS contact_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    attempt_date TEXT NOT NULL, -- A text string that is one of the ISO 8601 date/time values shown in items 1 through 10 below. Example: '2025-05-29 14:16:00'
    FOREIGN KEY (policy_id) REFERENCES policies(id)
);


-- Insert sample data into clients table
INSERT INTO clients (name, email, phone) VALUES
('John Doe', 'john.doe@example.com', '123-456-7890'),
('Jane Smith', 'jane.smith@example.com', '987-654-3210');

-- Insert sample data into advisors table
INSERT INTO advisors (name, email, phone) VALUES
('Alice Johnson', 'alice.johnson@example.com', '555-123-4567'),
('Bob Williams', 'bob.williams@example.com', '555-987-6543');

-- Insert sample data into policies table
INSERT INTO policies (client_id, advisor_id, insurer, expiration_date, status) VALUES
(1, 1, 'Insurer A', '2025-05-29 14:16:00', 1),
(2, 2, 'Insurer B', '2024-12-31 23:59:59', 0),
(1, 1, 'Insurer C', '2023-11-30 12:00:00', 1),
(2, 2, 'Insurer D', '2024-01-15 08:30:00', 0);

-- Insert sample data into contact_attempts table
INSERT INTO contact_attempts (policy_id, attempt_date) VALUES
(1, '2025-05-01 10:00:00'),
(1, '2025-05-15 14:30:00'),
(2, '2024-12-01 09:00:00'),
(3, '2023-11-15 16:45:00');