// index.ts — Vibe Investing Dashboard server (Node.js/TS)

import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { vibeRouter } from './routes/vibe.js';

const app = express();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3200', 10);

app.use(express.json());

// CORS
app.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Static frontend
app.use(express.static(path.join(__dirname, '../../static_web')));

// API routes
app.use('/api/vibe', vibeRouter);

// Serve dashboard at root
app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, '../../static_web/index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n  VIBE INVESTING Dashboard`);
  console.log(`  Server: http://localhost:${PORT}`);
  console.log(`  API:    http://localhost:${PORT}/api/vibe/\n`);
});
