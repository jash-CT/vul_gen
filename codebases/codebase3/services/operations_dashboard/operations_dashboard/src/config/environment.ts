import dotenv from 'dotenv';

dotenv.config();

export const CONFIG = {
  PORT: process.env.PORT || 3030,
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
  MONITORING_ENDPOINT: process.env.MONITORING_ENDPOINT || 'http://localhost:9090',
  INTERNAL_AUTH_TOKEN: process.env.INTERNAL_AUTH_TOKEN || 'default-insecure-token'
};