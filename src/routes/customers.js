import express from 'express';
import db from '../database.js';

const router = express.Router();

// Get all customers
router.get('/', (req, res) => {
  db.all('SELECT * FROM customers', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Create new customer
router.post('/', (req, res) => {
  const { name, phone, total_credit } = req.body;
  
  if (!name || !phone || !total_credit || total_credit <= 0) {
    res.status(400).json({ error: 'Please provide all required fields' });
    return;
  }

  const sql = `INSERT INTO customers (name, phone, total_credit, remaining_credit)
               VALUES (?, ?, ?, ?)`;
               
  db.run(sql, [name, phone, total_credit, total_credit], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      id: this.lastID,
      name,
      phone,
      total_credit,
      remaining_credit: total_credit
    });
  });
});

// Get customer by ID
router.get('/:id', (req, res) => {
  const sql = 'SELECT * FROM customers WHERE id = ?';
  db.get(sql, [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (!row) {
      res.status(404).json({ error: 'Customer not found' });
      return;
    }
    res.json(row);
  });
});

export default router;