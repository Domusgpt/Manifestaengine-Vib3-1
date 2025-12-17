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

function checkDocStructure(): Check {
  const docPath = path.resolve(__dirname, '..', 'docs/status/phase1.md');
  const content = readFileSync(docPath, 'utf-8');
  const requiredSections = [
    '## Scope',
    '## Artifacts to Produce',
    '## Validation Checklist',
    '## Progress',
    '## Exit Notes / Handoff to Phase 2',
    '## Gaps / Blockers',
    '## Sequencing / Dependencies',
    '## Risks / Watch-outs',
  ];

  const missingSections = requiredSections.filter((section) => !content.includes(section));

  const hasUncheckedItems = /- \[ \]/.test(content);
  const detailParts = [] as string[];
  if (missingSections.length > 0) {
    detailParts.push(`Missing sections: ${missingSections.join(', ')}`);
  }
  if (!hasUncheckedItems) {
    detailParts.push('No unchecked checklist items found; ensure open tasks remain visible.');
  }

  return {
    name: 'Phase 1 doc structure and openness',
    success: missingSections.length === 0 && hasUncheckedItems,
    detail: detailParts.join(' '),
  };
}

function checkReferences(): Check {
  const docPath = path.resolve(__dirname, '..', 'docs/status/phase1.md');
  const content = readFileSync(docPath, 'utf-8');
  const requiredMentions = [
    'schema/event.v1.json',
    'schema/agent_frame.v1.json',
    'packages/types/src/event.ts',
    'packages/types_dart/lib/event.dart',
    'vib34d-xr-quaternion-sdk',
    'HOLO_FRAME',
  ];

  const missingMentions = requiredMentions.filter((snippet) => !content.includes(snippet));

  return {
    name: 'Phase 1 doc references baseline artifacts',
    success: missingMentions.length === 0,
    detail:
      missingMentions.length === 0
        ? 'All required references are present.'
        : `Missing references: ${missingMentions.join(', ')}`,
  };
}

function main(): void {
  const checks: Check[] = [
    checkFileExists('docs/status/phase1.md'),
    checkReferences(),
    checkDocStructure(),
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
