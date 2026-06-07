// oauth.ts — GitHub App OAuth handler
import { config } from './config.js';
import { readJson, writeJson, DATA_DIR } from './db.js';
import { logAudit } from './db.js';
import { join } from 'node:path';

const OAUTH_FILE = join(DATA_DIR, 'oauth.json');

interface OAuthState {
  githubToken: string | null;
  githubUser: string | null;
  connectedAt: string | null;
}

export function getOAuthState(): OAuthState {
  return readJson<OAuthState>(OAUTH_FILE, {
    githubToken: null,
    githubUser: null,
    connectedAt: null,
  });
}

export function saveOAuthToken(token: string, user: string) {
  writeJson(OAUTH_FILE, {
    githubToken: token,
    githubUser: user,
    connectedAt: new Date().toISOString(),
  });
  config.github.oauthToken = token;
  logAudit('oauth_connected', 'info', `GitHub OAuth connected: ${user}`);
}

export function clearOAuthToken() {
  writeJson(OAUTH_FILE, {
    githubToken: null,
    githubUser: null,
    connectedAt: null,
  });
  config.github.oauthToken = '';
  logAudit('oauth_disconnected', 'info', 'GitHub OAuth disconnected');
}

export function getAuthToken(): string {
  const state = getOAuthState();
  return config.github.token || state.githubToken || '';
}

export async function exchangeCodeForToken(code: string): Promise<{ access_token: string }> {
  const { clientId, clientSecret, redirectUri } = config.github;
  const res = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      redirect_uri: redirectUri,
    }),
  });

  if (!res.ok) {
    throw new Error(`GitHub OAuth token exchange failed: ${await res.text()}`);
  }

  return res.json() as Promise<{ access_token: string }>;
}

export async function fetchGithubUser(token: string): Promise<{ login: string }> {
  const res = await fetch('https://api.github.com/user', {
    headers: {
      Authorization: `Bearer ${token}`,
      'User-Agent': 'LAON-VaultGuard',
    },
  });
  if (!res.ok) throw new Error(`Failed to fetch GitHub user: ${await res.text()}`);
  return res.json() as Promise<{ login: string }>;
}

export async function listGithubRepos(token: string): Promise<Array<{ full_name: string; private: boolean; html_url: string }>> {
  const res = await fetch('https://api.github.com/user/repos?per_page=100&sort=updated', {
    headers: {
      Authorization: `Bearer ${token}`,
      'User-Agent': 'LAON-VaultGuard',
    },
  });
  if (!res.ok) throw new Error(`Failed to list GitHub repos: ${await res.text()}`);
  return res.json() as Promise<Array<{ full_name: string; private: boolean; html_url: string }>>;
}
