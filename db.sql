/*
db.sql
DB Engine: SQLite3
This is the Data Definition Language (DDL) file for the insurance policies database.
*/

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    insurer TEXT NOT NULL,
    expiration_date TEXT NOT NULL, -- A text string that is one of the ISO 8601 date/time values shown in items 1 through 10 below. Example: '2025-05-29 14:16:00'
    status INTEGER NOT NULL CHECK(status IN (1, 0)) -- An integer that is either 1 (managed) or 0 (not managed)

    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Insert sample data into clients table
INSERT INTO clients (name, email, phone) VALUES
('John Doe', 'john.doe@example.com', '123-456-7890'),
('Jane Smith', 'jane.smith@example.com', '987-654-3210');

-- Insert sample data into policies table
INSERT INTO policies (client_id, insurer, expiration_date, status) VALUES
(1, 'Insurer A', '2025-05-29 14:16:00', 1),
(2, 'Insurer B', '2024-12-31 23:59:59', 0),
(1, 'Insurer C', '2023-11-30 12:00:00', 1),
(2, 'Insurer D', '2024-01-15 08:30:00', 0);
