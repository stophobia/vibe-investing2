#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');

const scriptName = __filename.includes('setup') ? 'setup' : 'cli';
const script = path.join(__dirname, 'src', `${scriptName}.ts`);

// Use node --import tsx/esm to run TypeScript directly
const r = spawnSync(process.execPath, ['--import', 'tsx/esm', script, ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: { ...process.env, NODE_OPTIONS: '' },
});
process.exit(r.status ?? 0);
