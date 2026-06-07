// candidate-filter.ts — 1st pass: git grep keyword filter before LLM

import { simpleGit } from 'simple-git';
import type { Candidate } from './types.js';

const SUSPECT_PATTERNS = [
  'AKIA',
  'ASIA',
  'AIza',
  '-----BEGIN',
  'client_secret',
  'AccountKey=',
  'aws_secret',
  'x-ncp',
  'ncloud',
  'ktcloud',
  'ucloudbiz',
  'api_key',
  'api-key',
  'secret_key',
  'secret-key',
  'NCP_ACCESS_KEY',
  'NCP_SECRET_KEY',
  'x-ncp-apigw-api-key',
  'x-ncp-iam-access-key',
  'OS_USERNAME',
  'OS_PASSWORD',
  'DefaultEndpointsProtocol',
  'service_account',
  'private_key_id',
  'ghp_',
  'gho_',
  'ghs_',
  'github_pat_',
  'xox[baprs]-',
  'sk-',
  'Bearer',
  'eyJ',            // JWT header
  'passwor?d\\s*=\\s*[\'"]',  // password= assignment
  'token\\s*=\\s*[\'"]',      // token= assignment
];

export function buildGrepPattern(): string {
  return SUSPECT_PATTERNS.join('|');
}

export async function extractCandidates(repoPath: string): Promise<Candidate[]> {
  const git = simpleGit(repoPath);
  const candidates: Candidate[] = [];
  const pattern = buildGrepPattern();

  try {
    // git grep with extended regex, line numbers, across all tracked files
    const result = await git.raw([
      'grep', '-nIE',
      pattern,
      '--', // end of options
    ]);
    if (!result.trim()) return candidates;

    for (const line of result.trim().split('\n')) {
      // format: filepath:linenum:content
      const match = line.match(/^(.+?):(\d+):(.*)$/);
      if (match) {
        const [, filePath, lineNum, content] = match;
        // skip obvious test fixtures and docs
        if (
          content.includes('example') ||
          content.includes('xxxx') ||
          content.includes('TODO') ||
          content.includes('placeholder')
        ) {
          // still include but mark separately — handled by LLM
        }
        candidates.push({
          filePath,
          lineNumber: parseInt(lineNum, 10),
          snippet: content.trim().slice(0, 200), // cap snippet length
          matchedPattern: pattern,
        });
      }
    }
  } catch (err) {
    // git grep returns exit code 1 when no matches — not an error
    if (err instanceof Error && !(err as Error & { code: number }).code) {
      throw err;
    }
  }

  return candidates;
}
