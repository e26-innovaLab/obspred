import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = resolve(fileURLToPath(import.meta.url), '..');
const rootDir = resolve(__dirname, '..');
const backendDir = join(rootDir, 'backend');

function findPython() {
  const isWin = process.platform === 'win32';
  const pyRel = isWin ? join('Scripts', 'python.exe') : join('bin', 'python');

  const candidates = [
    join(rootDir, '.venv', pyRel),
    join(backendDir, '.venv', pyRel),
    join(rootDir, 'venv', pyRel),
    join(backendDir, 'venv', pyRel),
  ];

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }

  return isWin ? 'python' : 'python3';
}

const pythonExe = findPython();
console.log(`[backend] Usando Python: ${pythonExe}`);

const child = spawn(
  pythonExe,
  ['-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
  {
    cwd: backendDir,
    stdio: 'inherit',
    windowsHide: true,
  }
);

child.on('exit', (code) => {
  process.exit(code ?? 0);
});
