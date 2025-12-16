import { spawnSync } from 'child_process';
import { existsSync } from 'fs';
import path from 'path';

interface StepResult {
  name: string;
  success: boolean;
  output: string;
}

function runCommand(command: string, args: string[]): StepResult {
  const result = spawnSync(command, args, { stdio: 'pipe', encoding: 'utf-8' });
  const output = [result.stdout, result.stderr].filter(Boolean).join('').trim();
  return {
    name: `${command} ${args.join(' ')}`.trim(),
    success: result.status === 0,
    output,
  };
}

function assertSchemaFiles(): StepResult {
  const schemaDir = path.resolve(__dirname, '..', 'schema');
  const files = ['event.v1.json', 'agent_frame.v1.json'];
  const missing = files.filter((file) => !existsSync(path.join(schemaDir, file)));
  const success = missing.length === 0;
  const output = success
    ? `Schemas located in ${schemaDir}`
    : `Missing schemas: ${missing.join(', ')}`;
  return { name: 'schema check', success, output };
}

function main(): void {
  const steps: StepResult[] = [];

  steps.push(assertSchemaFiles());

  const commands: Array<[string, string[]]> = [
    ['pnpm', ['lint']],
    ['pnpm', ['test:math']],
    ['pnpm', ['test:telemetry']],
    ['pnpm', ['test:ws']],
    ['pnpm', ['test:replay']],
  ];

  for (const [cmd, args] of commands) {
    steps.push(runCommand(cmd, args));
  }

  let exitCode = 0;
  for (const step of steps) {
    const status = step.success ? 'PASS' : 'FAIL';
    console.log(`[${status}] ${step.name}`);
    if (step.output) {
      console.log(step.output);
    }
    if (!step.success) {
      exitCode = 1;
    }
  }

  if (exitCode !== 0) {
    process.exit(exitCode);
  }
}

main();
