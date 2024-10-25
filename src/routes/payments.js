import express from 'express';
import db from '../database.js';

const router = express.Router();

// Register new payment
router.post('/', (req, res) => {
  const { customer_id, amount } = req.body;
  
  if (!customer_id || !amount || amount <= 0) {
    res.status(400).json({ error: 'Please provide valid customer ID and amount' });
    return;
  }

  db.get('SELECT remaining_credit FROM customers WHERE id = ?', [customer_id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    if (!row) {
      res.status(404).json({ error: 'Customer not found' });
      return;
    }

    if (amount > row.remaining_credit) {
      res.status(400).json({ error: 'Payment amount exceeds remaining credit' });
      return;
    }

    const new_credit = row.remaining_credit - amount;
    const date = new Date().toISOString();

    db.run('BEGIN TRANSACTION');

    db.run(
      'UPDATE customers SET remaining_credit = ? WHERE id = ?',
      [new_credit, customer_id],
      (err) => {
        if (err) {
          db.run('ROLLBACK');
          res.status(500).json({ error: err.message });
          return;
        }

        db.run(
          'INSERT INTO payments (customer_id, amount, date) VALUES (?, ?, ?)',
          [customer_id, amount, date],
          function(err) {
            if (err) {
              db.run('ROLLBACK');
              res.status(500).json({ error: err.message });
              return;
            }

            db.run('COMMIT');
            res.json({
              id: this.lastID,
              customer_id,
              amount,
              date,
              remaining_credit: new_credit
            });
          }
        );
      }
    );
  });
});

// Get payments by customer ID
router.get('/customer/:id', (req, res) => {
  const sql = 'SELECT * FROM payments WHERE customer_id = ? ORDER BY date DESC';
  db.all(sql, [req.params.id], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

export default router;