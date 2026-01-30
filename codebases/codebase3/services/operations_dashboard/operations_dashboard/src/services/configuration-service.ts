import fs from 'fs';
import path from 'path';

export class ConfigurationService {
  private configPath = path.join(__dirname, '../../config/system-config.json');

  readConfiguration() {
    try {
      const rawConfig = fs.readFileSync(this.configPath, 'utf-8');
      return JSON.parse(rawConfig);
    } catch (error) {
      console.error('Failed to read configuration', error);
      return {};
    }
  }

  updateConfiguration(newConfig: any) {
    try {
      fs.writeFileSync(this.configPath, JSON.stringify(newConfig, null, 2));
      return true;
    } catch (error) {
      console.error('Failed to update configuration', error);
      return false;
    }
  }
}