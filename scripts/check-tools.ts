import { execSync } from 'child_process';

interface ToolCheck {
  label: string;
  command: string;
  args?: string[];
  required?: boolean;
}

const tools: ToolCheck[] = [
  { label: 'Node', command: 'node', args: ['--version'], required: true },
  { label: 'pnpm', command: 'pnpm', args: ['--version'], required: true },
  { label: 'TypeScript', command: 'tsc', args: ['--version'], required: true },
  { label: 'ts-node', command: 'ts-node', args: ['--version'], required: true },
  { label: 'Python', command: 'python3', args: ['--version'], required: true },
];

function runCheck(tool: ToolCheck) {
  try {
    const version = execSync([tool.command, ...(tool.args ?? ['--version'])].join(' '), {
      stdio: ['ignore', 'pipe', 'pipe'],
    })
      .toString()
      .trim();

    return { label: tool.label, status: 'ok', detail: version } as const;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { label: tool.label, status: 'missing', detail: message } as const;
  }
}

function main() {
  const results = tools.map(runCheck);
  const missing = results.filter((result) => result.status !== 'ok' && tools.find((tool) => tool.label === result.label)?.required);

  results.forEach((result) => {
    const prefix = result.status === 'ok' ? '✅' : '❌';
    console.log(`${prefix} ${result.label}: ${result.detail}`);
  });

  if (missing.length > 0) {
    console.error('\nOne or more required tools are missing or unavailable.');
    process.exit(1);
  }
}

main();
