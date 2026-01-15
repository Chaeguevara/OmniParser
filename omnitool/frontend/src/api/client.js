/**
 * REST API Client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';

class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Chat endpoints
  async sendMessage(message) {
    return this.request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async getChatHistory() {
    return this.request('/api/chat/history');
  }

  async clearChatHistory() {
    return this.request('/api/chat/history', {
      method: 'DELETE',
    });
  }

  // Agent endpoints
  async startAgent(config) {
    return this.request('/api/agent/start', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async stopAgent() {
    return this.request('/api/agent/stop', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getAgentStatus() {
    return this.request('/api/agent/status');
  }

  // Settings endpoints
  async getSettings() {
    return this.request('/api/settings');
  }

  async updateSettings(settings) {
    return this.request('/api/settings', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new APIClient();
