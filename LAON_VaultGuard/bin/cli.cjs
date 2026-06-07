#!/usr/bin/env node
'use strict';
const { spawnSync } = require('child_process');
const path = require('path');

const tsx = path.resolve(__dirname, '..', 'node_modules', '.bin', 'tsx');
const scriptName = __filename.includes('setup') ? 'setup.ts' : 'cli.ts';
const script = path.resolve(__dirname, '..', 'src', scriptName);

const result = spawnSync(tsx, [script, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status ?? 0);
