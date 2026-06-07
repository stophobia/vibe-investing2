// setup.ts — LAON VaultGuard interactive setup (LLM provider multi-select + Ollama install)
import { createInterface } from 'node:readline';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { resolve } from 'node:path';
import { platform } from 'node:os';
import { t, setLocale, type Locale } from './i18n.js';

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

interface OllamaModel {
  name: string;
  sizeGB: number;
  ramNeeded: string;
  accuracy: string;
  speed: string;
  bestFor: string;
  requiresAppleSilicon?: boolean;
  isFineTuned?: boolean;
}

const OLLAMA_MODELS: OllamaModel[] = [
  {
    name: 'deepseek-r1:8b',
    sizeGB: 4.9,
    ramNeeded: '8GB+',
    accuracy: '★★★☆',
    speed: '★★☆☆',
    bestFor: '시크릿 탐지 최적 — 추론 특화, false positive 제어 우수 (SecretBench 검증)',
  },
  {
    name: 'llama3.1:8b',
    sizeGB: 4.7,
    ramNeeded: '8GB+',
    accuracy: '★★☆☆',
    speed: '★★★☆',
    bestFor: '범용 스캔 — 무난한 성능, Ollama 공식 기본 모델',
  },
  {
    name: 'mistral:7b',
    sizeGB: 4.1,
    ramNeeded: '8GB',
    accuracy: '★☆☆☆',
    speed: '★★★★',
    bestFor: '저사양 기기 — 구형 Mac, 8GB RAM, 빠른 응답 필요 시',
  },
  {
    name: 'codestral:22b',
    sizeGB: 13,
    ramNeeded: '16GB+',
    accuracy: '★★★★',
    speed: '★☆☆☆',
    bestFor: '최고 정확도 — 대용량 RAM 확보 시 코드 분석 정밀도 최상',
  },
  {
    name: 'vitorallo/securereview-7b-mlx-4bit',
    sizeGB: 4.2,
    ramNeeded: '8GB+',
    accuracy: '★★★★',
    speed: '★★☆☆',
    bestFor: '보안 리뷰 파인튜닝 — 취약점·시크릿 탐지에 특화 학습됨',
    requiresAppleSilicon: true,
    isFineTuned: true,
  },
];

// ── main ──

async function main() {
  const rl = createInterface({ input: process.stdin, output: process.stdout });

  // ── Language selection ──
  console.log('\n  🌐 Language / 언어 / 语言 / 言語');
  console.log('  [1] 한국어  [2] English  [3] 中文  [4] 日本語');
  const langChoice = await question(rl, 'Language [1]: ');
  const langMap: Record<string, Locale> = { '1': 'ko', '2': 'en', '3': 'zh', '4': 'ja' };
  setLocale(langMap[langChoice] || 'ko');

  console.log(`\n  ${t('title')}\n`);
  console.log(`  ${t('welcome')}\n`);

  let lines = readEnvLines(ENV_PATH);

  // ── Storage engine ──
  console.log(`─── ${t('storage_title')} ───`);
  console.log(`  [1] ${t('storage_sqlite')}`);
  console.log(`  [2] ${t('storage_json')}\n`);
  const engineChoice = await question(rl, `${t('storage_prompt')}`);
  const engineMap: Record<string, string> = { '1': 'sqlite', '2': 'json', 'sqlite': 'sqlite', 'json': 'json' };
  const engine = engineMap[engineChoice] || 'sqlite';
  lines = setKey(lines, 'STORAGE_ENGINE', engine);
  console.log(`  -> ${engine === 'sqlite' ? t('storage_chosen_sqlite') : t('storage_chosen_json')}\n`);

  // ── LLM provider selection (multi-select) ──
  console.log(`─── ${t('llm_title')} ───`);
  console.log(`  ${t('llm_multi_intro')}\n`);
  console.log(`  [1] DeepSeek    (recommended) — ${t('llm_deepseek_desc')}`);
  console.log(`  [2] Claude                    — ${t('llm_claude_desc')}`);
  console.log(`  [3] ChatGPT                   — ${t('llm_chatgpt_desc')}`);
  console.log(`  [4] Ollama                    — ${t('llm_ollama_desc')}\n`);
  const providerChoice = await question(rl, `${t('llm_prompt')}`);
  const chosen = (providerChoice || '1,4').split(',').map(s => s.trim()).filter(Boolean);
  const wantOllama = chosen.includes('4');
  const onlineChoices = LLM_OPTIONS.filter(o => chosen.includes(String(LLM_OPTIONS.indexOf(o) + 1)));

  // ── API key input (only for selected online providers) ──
  if (onlineChoices.length > 0) {
    console.log(`\n${t('api_keys_title')}\n`);
    console.log(`${t('api_keys_reg_url')}`);
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
      console.log(`  ${t('api_key_saved')}`);
    } else {
      console.log(`  ${t('api_key_skipped')}`);
    }
  }

  // ── Ollama setup ──
  let ollamaReady = false;
  if (wantOllama) {
    console.log('\n─── Ollama Setup ───');
    if (checkOllama()) {
      const isAppleSilicon = platform() === 'darwin' && (() => {
        try { return execSync('sysctl -n machdep.cpu.brand_string', { encoding: 'utf-8' }).includes('Apple'); } catch { return false; }
      })();
      console.log('  ✅ Ollama detected.\n');
      const existing = listOllamaModels();
      if (existing.length > 0) {
        console.log('  Currently installed models:');
        for (const m of existing) console.log(`    - ${m}`);
        console.log();
      } else {
        console.log('  No models installed yet. Choose from below:\n');
      }

      // ── model comparison table ──
      console.log('  Available models (select 1-2 for best results):\n');
      console.log('    #  Model                        Size    RAM     Acc.   Speed  Notes');
      console.log('    ── ──────────────────────────── ──────  ──────  ────   ─────  ──────────────────────────────────');
      for (let i = 0; i < OLLAMA_MODELS.length; i++) {
        const m = OLLAMA_MODELS[i];
        const num = `[${i + 1}]`;
        let notes = '';
        if (i === 0) notes = '← 시크릿 탐지 권장';
        else if (i === 1) notes = '← Ollama 기본';
        else if (i === 4) notes = '← 보안 파인튜닝 (Apple Silicon 전용)';
        // skip models not available on this platform
        if (m.requiresAppleSilicon && !isAppleSilicon) continue;
        const notePad = notes ? ` ${notes}` : '';
        console.log(`    ${num.padEnd(3)} ${m.name.padEnd(28)} ${String(m.sizeGB).padEnd(6)} ${m.ramNeeded.padEnd(6)} ${m.accuracy.padEnd(4)}  ${m.speed.padEnd(5)}${notePad}`);
      }
      if (!isAppleSilicon) {
        console.log('    ─   (securereview-7b skipped — Apple Silicon only)');
      }
      console.log('    [0]  skip — I\'ll pull models manually later');
      console.log();

      // ── guided recommendation ──
      console.log('  ── 최적 조합 가이드 ──');
      console.log('  🥇 단일 모델:  [1] deepseek-r1:8b — 비용 0, 시크릿 탐지 False Positive 제어 최고');
      if (isAppleSilicon) {
        console.log('  🥈 보안 특화:   [5] securereview-7b — 취약점 리뷰 파인튜닝, SecretBench 유사 데이터 학습');
        console.log('  🔥 최고 조합:  [1+5] deepseek-r1 + securereview — 추론 + 보안 도메인 교차검증');
      } else {
        console.log('  🔥 최고 조합:  [1+3] deepseek-r1 + mistral — 추론 + 경량 모델 교차검증');
      }
      console.log();

      // ── select models to pull (multi) ──
      const pullChoice = await question(rl, 'Models to pull (comma-separated, e.g. 1,5) [1]: ');
      if (pullChoice === '0') {
        console.log('  -> model pull skipped. Run "ollama pull <name>" later.\n');
      } else {
        const nums = (pullChoice || '1').split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n) && n > 0 && n <= OLLAMA_MODELS.length);
        const selectedModels = nums.map(n => OLLAMA_MODELS[n - 1]).filter(Boolean);

        for (const model of selectedModels) {
          if (model.requiresAppleSilicon && !isAppleSilicon) {
            console.log(`  ⚠ ${model.name} requires Apple Silicon — skipping`);
            continue;
          }
          if (existing.includes(model.name)) {
            console.log(`  ✅ ${model.name} already installed`);
            continue;
          }
          console.log(`\n  ⬇ Pulling ${model.name}... (${model.sizeGB}GB, ${model.isFineTuned ? 'custom model' : '~2-10 min'})\n`);
          try {
            execSync(`ollama pull ${model.name}`, { stdio: 'inherit' });
            console.log(`\n  ✅ ${model.name} pulled successfully`);
          } catch {
            console.log(`\n  ❌ pull failed. Run manually: ollama pull ${model.name}`);
          }
        }
        console.log();
      }

      // ── multi-Ollama cross-validation guidance ──
      const pulledNow = ((pullChoice || '1').split(',').map(s => parseInt(s.trim(), 10))
        .filter(n => !isNaN(n)).map(n => OLLAMA_MODELS[n - 1]).filter(Boolean)
        .map(m => m.name));
      const allAvailable = [...new Set([...existing, ...pulledNow])];

      if (allAvailable.length >= 2) {
        console.log('  🔥 Multi-Ollama 권장 구성 (교차검증):');
        console.log(`    현재 ${allAvailable.length}개 모델 사용 가능.\n`);
        console.log('    VaultGuard는 여러 LLM의 판단을 교차검증하여 오탐을 줄입니다.');
        console.log('    Ollama 모델 2개를 동시에 사용하면 API 비용 없이도 다수결 모드 사용 가능.\n');
        const primary = allAvailable.find(m => m.includes('deepseek-r1')) || allAvailable[0];
        const secondary = allAvailable.filter(m => m !== primary);
        console.log(`    권장 .env 설정 (주 모델: ${primary}):`);
        console.log(`      LLM_PROVIDERS=ollama,ollama-secondary`);
        console.log(`      LLM_MODE=majority`);
        console.log(`      OLLAMA_MODEL=${primary}`);
        console.log(`      OLLAMA_MODEL_SECONDARY=${secondary[0]}`);
        console.log();
      } else if (allAvailable.length === 1) {
        console.log('  💡 Pro tip: Pull a second model for cross-validation:');
        console.log(`    Currently: ${allAvailable[0]}`);
        if (allAvailable[0].includes('deepseek')) {
          console.log('    Add:      ollama pull mistral  (fast + lightweight complement)');
        } else {
          console.log('    Add:      ollama pull deepseek-r1:8b  (reasoning + best for secrets)');
        }
        console.log();
      }

      // configure primary ollama model in .env
      const ollamaModel = allAvailable[0] || 'deepseek-r1:8b';
      lines = setKey(lines, 'OLLAMA_MODEL', ollamaModel);
      if (!lines.some(l => l.startsWith('OLLAMA_BASE_URL'))) {
        lines = setKey(lines, 'OLLAMA_BASE_URL', 'http://localhost:11434/v1');
      }
      ollamaReady = true;
    } else {
      console.log('  ❌ Ollama is not installed.\n');
      console.log(`  Install:\n    ${getOllamaInstallGuide()}\n`);
      console.log('  1. Run the install command above');
      console.log('  2. Pull models:  ollama pull deepseek-r1:8b');
      console.log('  3. Re-run:  npm run setup  to complete configuration\n');

      const installChoice = await question(rl, 'Show install instructions? [y/N]: ');
      if (installChoice.toLowerCase() === 'y' || installChoice.toLowerCase() === 'yes') {
        console.log(`\n  Platform: ${platform()}`);
        console.log(`  Command:  ${getOllamaInstallGuide()}`);
        console.log('  Models:   ollama pull deepseek-r1:8b');
        console.log('            ollama pull securereview-7b-mlx-4bit  (Apple Silicon only)');
        console.log('\n  After install + model pull, re-run: npm run setup\n');
      }
      console.log('  -> Ollama deferred. Set manually in .env:');
      console.log('     OLLAMA_BASE_URL=http://localhost:11434/v1');
      console.log('     OLLAMA_MODEL=deepseek-r1:8b\n');
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

  const modeLabel = providers.length >= 2 ? t('summary_mode_parallel') : t('summary_mode_sequential');
  console.log('\n──────────────────────────────────────────');
  console.log(`  ${t('summary_title')}: .env`);
  console.log(`  ${t('summary_storage')}:  ${engine === 'sqlite' ? 'SQLite' : 'JSON'}`);
  console.log(`  ${t('summary_llm')}:     ${providers.join(', ') || 'none'}`);
  console.log(`  ${t('summary_mode')}:     ${modeLabel}`);
  if (wantOllama && !ollamaReady) {
    console.log(`  ${t('summary_ollama_warn')}`);
  }
  console.log('──────────────────────────────────────────');
  console.log(`  ${t('summary_start')}`);
  console.log(`  ${t('summary_scan')}`);
  console.log(`  ${t('summary_rerun')}\n`);

  rl.close();
}

main().catch(console.error);
