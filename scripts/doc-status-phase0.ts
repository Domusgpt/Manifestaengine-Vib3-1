import { existsSync, readFileSync } from 'fs';
import path from 'path';

interface Check {
  name: string;
  success: boolean;
  detail?: string;
}

function checkFileExists(relativePath: string): Check {
  const fullPath = path.resolve(__dirname, '..', relativePath);
  const success = existsSync(fullPath);
  return {
    name: `File exists: ${relativePath}`,
    success,
    detail: success ? fullPath : `${relativePath} missing`,
  };
}

function checkDocReferences(): Check {
  const docPath = path.resolve(__dirname, '..', 'docs/status/phase0.md');
  const content = readFileSync(docPath, 'utf-8');
  const requiredSnippets = [
    'schema/event.v1.json',
    'schema/agent_frame.v1.json',
    'packages/types/src/event.ts',
    'packages/types_dart/lib/event.dart',
    'services/telemetry/ws-server',
    'scripts/mock',
    'scripts/replay.ts',
    'packages/math/src/quaternion.ts',
    'packages/math/src/elasticity.ts',
  ];

  const missing = requiredSnippets.filter((snippet) => !content.includes(snippet));
  return {
    name: 'Docs reference required artifacts',
    success: missing.length === 0,
    detail: missing.length === 0 ? 'All referenced' : `Missing references: ${missing.join(', ')}`,
  };
}

function main(): void {
  const checks: Check[] = [
    checkFileExists('docs/status/phase0.md'),
    checkFileExists('schema/event.v1.json'),
    checkFileExists('schema/agent_frame.v1.json'),
    checkFileExists('packages/types/src/event.ts'),
    checkFileExists('packages/types_dart/lib/event.dart'),
    checkDocReferences(),
  ];

  let exitCode = 0;
  for (const check of checks) {
    const status = check.success ? 'PASS' : 'FAIL';
    console.log(`[${status}] ${check.name}`);
    if (check.detail) {
      console.log(`  ${check.detail}`);
    }
    if (!check.success) {
      exitCode = 1;
    }
  }

  if (exitCode !== 0) {
    process.exit(exitCode);
  }
}

main();
