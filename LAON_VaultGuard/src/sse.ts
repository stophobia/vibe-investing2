// sse.ts — Server-Sent Events event bus for dashboard real-time updates

import type { Response } from 'express';
import type { SseEvent } from './types.js';

const clients = new Set<Response>();

export function addSseClient(res: Response) {
  clients.add(res);
  res.on('close', () => {
    clients.delete(res);
  });
}

export function emitSse(type: SseEvent['type'], data: unknown) {
  const payload = `data: ${JSON.stringify({ type, data, timestamp: new Date().toISOString() })}\n\n`;
  for (const client of clients) {
    try {
      client.write(payload);
    } catch {
      clients.delete(client);
    }
  }
}

export function sseClientCount(): number {
  return clients.size;
}
