import axios, { AxiosInstance, AxiosResponse } from 'axios';

export interface GitHubConfig {
  token: string;
  baseURL?: string;
}

export class GitHubAPI {
  private client: AxiosInstance;

  constructor(config: GitHubConfig) {
    this.client = axios.create({
      baseURL: config.baseURL || 'https://api.github.com',
      headers: {
        'Authorization': `Bearer ${config.token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      }
    });
  }

  async makeRequest<T = any>(endpoint: string, params: Record<string, any> = {}): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.get(endpoint, { params });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`GitHub API Error: ${error.response?.status} - ${error.response?.statusText}`);
      }
      throw error;
    }
  }

  async makePostRequest<T = any>(endpoint: string, data: any = {}): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.post(endpoint, data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`GitHub API Error: ${error.response?.status} - ${error.response?.statusText}`);
      }
      throw error;
    }
  }
}