import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import { initDatabase } from './database.js';
import customerRoutes from './routes/customers.js';
import paymentRoutes from './routes/payments.js';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

// Initialize database
initDatabase();

// Routes
app.use('/api/customers', customerRoutes);
app.use('/api/payments', paymentRoutes);

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});