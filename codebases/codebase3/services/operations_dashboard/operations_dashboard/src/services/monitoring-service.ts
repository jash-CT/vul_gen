import axios from 'axios';
import { CONFIG } from '../config/environment';
import { Logger } from '../utils/logger';

export class MonitoringService {
  private logger = new Logger('MonitoringService');

  async fetchSystemMetrics() {
    try {
      const response = await axios.get(`${CONFIG.MONITORING_ENDPOINT}/metrics`, {
        headers: { 'Authorization': `Bearer ${CONFIG.INTERNAL_AUTH_TOKEN}` }
      });
      return response.data;
    } catch (error) {
      this.logger.error('Failed to fetch system metrics', error);
      throw error;
    }
  }

  async fetchServiceHealth() {
    const services = ['user_management', 'order_processing', 'analytics', 'integration_broker'];
    const healthChecks = services.map(async (service) => {
      try {
        const response = await axios.get(`${CONFIG.MONITORING_ENDPOINT}/health/${service}`);
        return { service, status: response.data.status };
      } catch (error) {
        return { service, status: 'UNKNOWN' };
      }
    });

    return Promise.all(healthChecks);
  }
}