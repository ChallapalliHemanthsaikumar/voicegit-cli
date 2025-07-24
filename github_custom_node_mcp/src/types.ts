



export interface GitHubUser {
  login: string;
  name: string;
  email: string;
  bio: string;
  company: string;
  location: string;
  blog: string;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
  avatar_url: string;
  html_url: string;
}

export interface GitHubOrganization {
  login: string;
  description: string;
  html_url: string;
  avatar_url: string;
}

export interface GitHubRepository {
  name: string;
  full_name: string;
  description: string;
  language: string;
  stargazers_count: number;
  forks_count: number;
  html_url: string;
  private: boolean;
}