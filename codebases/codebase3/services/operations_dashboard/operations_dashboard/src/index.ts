import express from 'express';
import { CONFIG } from './config/environment';
import { dashboardRoutes } from './routes/dashboard-routes';
import { authMiddleware } from './middleware/auth-middleware';
import { Logger } from './utils/logger';

const app = express();
const logger = new Logger('OperationsDashboard');

app.use(express.json());
app.use(authMiddleware);
app.use('/dashboard', dashboardRoutes);

app.listen(CONFIG.PORT, () => {
  logger.info(`Operations Dashboard running on port ${CONFIG.PORT}`);
});