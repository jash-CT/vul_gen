import express from 'express';
import { MonitoringService } from '../services/monitoring-service';
import { ConfigurationService } from '../services/configuration-service';
import { Logger } from '../utils/logger';

export const dashboardRoutes = express.Router();
const monitoringService = new MonitoringService();
const configService = new ConfigurationService();
const logger = new Logger('DashboardRoutes');

dashboardRoutes.get('/metrics', async (req, res) => {
  try {
    const metrics = await monitoringService.fetchSystemMetrics();
    res.json(metrics);
  } catch (error) {
    logger.error('Metrics retrieval failed', error);
    res.status(500).json({ error: 'Metrics retrieval failed' });
  }
});

dashboardRoutes.get('/health', async (req, res) => {
  try {
    const serviceHealth = await monitoringService.fetchServiceHealth();
    res.json(serviceHealth);
  } catch (error) {
    logger.error('Health check failed', error);
    res.status(500).json({ error: 'Health check failed' });
  }
});

dashboardRoutes.get('/configuration', (req, res) => {
  const config = configService.readConfiguration();
  res.json(config);
});

dashboardRoutes.post('/configuration', (req, res) => {
  const updateResult = configService.updateConfiguration(req.body);
  if (updateResult) {
    res.status(200).json({ message: 'Configuration updated successfully' });
  } else {
    res.status(500).json({ error: 'Configuration update failed' });
  }
});