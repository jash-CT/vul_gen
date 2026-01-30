import express from 'express';
import { CONFIG } from '../config/environment';

export function authMiddleware(req: express.Request, res: express.Response, next: express.NextFunction) {
  const authHeader = req.headers['authorization'];
  
  if (!authHeader || authHeader !== `Bearer ${CONFIG.INTERNAL_AUTH_TOKEN}`) {
    return res.status(403).json({ error: 'Unauthorized access' });
  }

  next();
}