// setup.ts — LAON VaultGuard interactive setup (LLM provider multi-select + Ollama install)
import { createInterface } from 'node:readline';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { resolve } from 'node:path';
import { platform } from 'node:os';

const ENV_PATH = resolve(import.meta.dirname || '.', '../.env');
const ENV_EXAMPLE = resolve(import.meta.dirname || '.', '../.env.example');

// ── .env helpers ──

function readEnvLines(path: string): string[] {
  if (existsSync(path)) {
    return readFileSync(path, 'utf-8').split('\n');
  }
  return readFileSync(ENV_EXAMPLE, 'utf-8').split('\n');
}

function writeEnv(lines: string[]) {
  writeFileSync(ENV_PATH, lines.join('\n'), 'utf-8');
}

function setKey(lines: string[], key: string, value: string): string[] {
  const prefix = `${key}=`;
  const idx = lines.findIndex(l => l.startsWith(prefix) || l.startsWith(`# ${prefix}`));
  if (idx !== -1) {
    lines[idx] = `${key}=${value}`;
  } else {
    lines.push(`${key}=${value}`);
  }
  return lines;
}

// ── masked API key input (raw mode, ***) ──

function maskedInput(prompt: string): Promise<string> {
  return new Promise(resolve => {
    process.stdout.write(prompt);
    let input = '';
    const prev = process.stdin.isRaw;
    process.stdin.setRawMode?.(true);
    process.stdin.resume();
    process.stdin.on('data', (chunk: Buffer) => {
      const str = chunk.toString();
      for (const ch of str) {
        if (ch === '\r' || ch === '\n') {
          process.stdout.write('\n');
          process.stdin.setRawMode?.(Boolean(prev));
          process.stdin.pause();
          resolve(input);
          return;
        }
        if (ch === '\x7f' || ch === '\b') {
          if (input.length > 0) {
            input = input.slice(0, -1);
            process.stdout.write('\b \b');
          }
        } else if (ch === '\x03') {
          process.stdout.write('\n');
          process.exit(1);
        } else {
          input += ch;
          process.stdout.write('*');
        }
      }
    });
  });
}

// ── question helper ──

function question(rl: ReturnType<typeof createInterface>, prompt: string): Promise<string> {
  return new Promise(resolve => {
    rl.question(prompt, answer => resolve(answer.trim()));
  });
}

// ── Ollama helpers ──

function checkOllama(): boolean {
  try {
    execSync('ollama --version', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

function listOllamaModels(): string[] {
  try {
    const out = execSync('ollama list', { encoding: 'utf-8', stdio: 'pipe' });
    return out.split('\n')
      .slice(1)
      .map(line => line.split(/\s+/)[0])
      .filter(Boolean);
  } catch {
    return [];
  }
}

function getOllamaInstallGuide(): string {
  const os = platform();
  if (os === 'darwin') {
    return '  brew install ollama';
  }
  if (os === 'linux') {
    return '  curl -fsSL https://ollama.com/install.sh | sh';
  }
  return '  Download: https://ollama.com/download/windows';
}

// ── LLM provider definitions ──

interface LlmOption {
  id: string;
  label: string;
  envKey: string;
  description: string;
  getKeyUrl: string;
  recommended: boolean;
}

const LLM_OPTIONS: LlmOption[] = [
  {
    id: 'deepseek',
    label: 'DeepSeek',
    envKey: 'DEEPSEEK_API_KEY',
    description: 'best price-performance, $0.14/M tokens',
    getKeyUrl: 'https://platform.deepseek.com/api_keys',
    recommended: true,
  },
  {
    id: 'claude',
    label: 'Claude (Anthropic)',
    envKey: 'CLAUDE_API_KEY',
    description: 'highest accuracy, enterprise-grade audit',
    getKeyUrl: 'https://console.anthropic.com/',
    recommended: false,
  },
  {
    id: 'openai',
    label: 'ChatGPT (OpenAI)',
    envKey: 'OPENAI_API_KEY',
    description: 'well-rounded, largest ecosystem',
    getKeyUrl: 'https://platform.openai.com/api-keys',
    recommended: false,
  },
];

const OLLAMA_RECOMMENDED_MODELS = [
  { name: 'llama3.1:8b', desc: 'general purpose, fast (~4.7GB)', why: 'lightweight, good all-around' },
  { name: 'deepseek-r1:8b', desc: 'reasoning, security audit (~4.9GB)', why: 'best for code analysis, secret detection' },
  { name: 'mistral:7b', desc: 'lightweight, fast (~4.1GB)', why: 'smallest usable model, lowest RAM' },
  { name: 'codestral:22b', desc: 'code specialist (~13GB)', why: 'larger, needs 16GB+ RAM' },
];

// ── main ──

async function main() {
  const rl = createInterface({ input: process.stdin, output: process.stdout });

  console.log('\n  LAON VaultGuard — Setup\n');
  console.log('  This wizard configures your .env with storage engine, LLM providers, and API keys.\n');

  let lines = readEnvLines(ENV_PATH);

  // ── Storage engine ──
  console.log('─── Storage Engine ───');
  console.log('  [1] SQLite (recommended) — ACID transactions, concurrent-safe, WAL mode');
  console.log('  [2] JSON (legacy)       — simple file-based, no dependencies\n');
  const engineChoice = await question(rl, 'Storage engine [1]: ');
  const engineMap: Record<string, string> = { '1': 'sqlite', '2': 'json', 'sqlite': 'sqlite', 'json': 'json' };
  const engine = engineMap[engineChoice] || 'sqlite';
  lines = setKey(lines, 'STORAGE_ENGINE', engine);
  console.log(`  -> ${engine === 'sqlite' ? 'SQLite (ACID, WAL mode)' : 'JSON (legacy)'}\n`);

  // ── LLM provider selection (multi-select) ──
  console.log('─── LLM Providers ───');
  console.log('  Select providers (comma-separated, e.g. 1,2,4).');
  console.log('  DeepSeek is recommended for best price-performance.\n');
  console.log('  [1] DeepSeek    (recommended) — $0.14/M tokens, fastest');
  console.log('  [2] Claude                    — highest accuracy, $3/$15 per M');
  console.log('  [3] ChatGPT                   — well-rounded, $2.50/$10 per M');
  console.log('  [4] Ollama                    — free, local, offline (no API key)\n');
  const providerChoice = await question(rl, 'Providers [1,4]: ');
  const chosen = (providerChoice || '1,4').split(',').map(s => s.trim()).filter(Boolean);
  const wantOllama = chosen.includes('4');
  const onlineChoices = LLM_OPTIONS.filter(o => chosen.includes(String(LLM_OPTIONS.indexOf(o) + 1)));

  // ── API key input (only for selected online providers) ──
  if (onlineChoices.length > 0) {
    console.log('\nEnter API keys. Input is masked (***). Press Enter to skip.\n');
    console.log('Key registration URLs:');
    for (const opt of onlineChoices) {
      console.log(`  ${opt.label}: ${opt.getKeyUrl}`);
    }
    console.log();
  }

  const enteredKeys: Record<string, string> = {};
  for (const opt of onlineChoices) {
    const key = await maskedInput(`${opt.label} API key: `);
    if (key) {
      lines = setKey(lines, opt.envKey, key);
      enteredKeys[opt.id] = key;
      console.log('  -> key saved');
    } else {
      console.log('  -> skipped');
    }
  }

  // ── Ollama setup ──
  let ollamaReady = false;
  if (wantOllama) {
    console.log('\n─── Ollama Setup ───');
    if (checkOllama()) {
      console.log('  Ollama detected.\n');
      const existing = listOllamaModels();
      if (existing.length > 0) {
        console.log('  Installed models:');
        for (const m of existing) console.log(`    - ${m}`);
      } else {
        console.log('  No models pulled yet.');
      }

      console.log('\n  Recommended models:');
      for (const m of OLLAMA_RECOMMENDED_MODELS) {
        console.log(`    ${m.name.padEnd(20)} ${m.desc.padEnd(30)} ${m.why}`);
      }

      const pullChoice = await question(rl, '\nPull a model? (name or Enter to skip): ');
      if (pullChoice) {
        console.log(`\n  Pulling ${pullChoice}... (this may take a few minutes)\n`);
        try {
          execSync(`ollama pull ${pullChoice}`, { stdio: 'inherit' });
          console.log(`\n  -> ${pullChoice} ready`);
        } catch {
          console.log(`\n  -> pull failed. Run manually: ollama pull ${pullChoice}`);
        }
      } else {
        console.log('  -> model pull skipped (run ollama pull <name> later)');
      }
      ollamaReady = true;
    } else {
      console.log('  Ollama is not installed.\n');
      console.log(`  Install command:\n${getOllamaInstallGuide()}\n`);
      const installChoice = await question(rl, 'Install now? This opens your terminal [y/N]: ');
      if (installChoice.toLowerCase() === 'y' || installChoice.toLowerCase() === 'yes') {
        console.log(`\n  Run this command in another terminal:\n  ${getOllamaInstallGuide()}\n`);
        console.log('  After install, run:  ollama pull llama3.1:8b');
        console.log('  Then re-run this setup to add Ollama.\n');
      }
      console.log('  -> Ollama skipped. Add later via .env: OLLAMA_BASE_URL=http://localhost:11434/v1');
    }
  }

  // ── Auto-configure providers ──
  const providers: string[] = [];
  if (enteredKeys.deepseek) providers.push('deepseek');
  if (enteredKeys.claude) providers.push('claude');
  if (enteredKeys.openai) providers.push('openai');
  if (wantOllama && ollamaReady) {
    providers.push('ollama');
    // ensure ollama env vars are set
    if (!lines.some(l => l.startsWith('OLLAMA_BASE_URL'))) {
      lines = setKey(lines, 'OLLAMA_BASE_URL', 'http://localhost:11434/v1');
    }
    if (!lines.some(l => l.startsWith('OLLAMA_MODEL'))) {
      lines = setKey(lines, 'OLLAMA_MODEL', 'deepseek-r1:8b');
    }
  }

  if (providers.length > 0) {
    lines = setKey(lines, 'LLM_PROVIDERS', providers.join(','));
    lines = setKey(lines, 'LLM_MODE', providers.length >= 2 ? 'parallel' : 'sequential');
  }

  // ── Write config ──
  writeEnv(lines);

  console.log('\n──────────────────────────────────────────');
  console.log(`  Config saved to .env`);
  console.log(`  Storage:  ${engine === 'sqlite' ? 'SQLite' : 'JSON'}`);
  console.log(`  LLM:     ${providers.join(', ') || 'none'}`);
  console.log(`  Mode:     ${providers.length >= 2 ? 'parallel (cross-validation)' : 'sequential'}`);
  if (wantOllama && !ollamaReady) {
    console.log('  ⚠ Ollama not ready. Install and re-run setup, or edit .env manually.');
  }
  console.log('──────────────────────────────────────────');
  console.log('  Start:  npm run dev');
  console.log('  Scan:   npm run scan -- <repo-path>');
  console.log('  Re-run: npm run setup\n');

  rl.close();
}

main().catch(console.error);
