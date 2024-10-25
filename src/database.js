import sqlite3 from 'sqlite3';

const db = new sqlite3.Database('credits.db');

export function initDatabase() {
  db.serialize(() => {
    // Create customers table
    db.run(`CREATE TABLE IF NOT EXISTS customers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone TEXT NOT NULL,
      total_credit REAL NOT NULL,
      remaining_credit REAL NOT NULL
    )`);

    // Create payments table
    db.run(`CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      date TEXT NOT NULL,
      FOREIGN KEY (customer_id) REFERENCES customers(id)
    )`);
  });
}

export default db;