import fs from "fs";
import {WebSocket} from "ws";
import {assertValid, EnvelopeKind, EventEnvelope, AgentFrame} from "../packages/types/src/event";

export function readFrames(path: string): Array<{kind: EnvelopeKind; payload: EventEnvelope | AgentFrame}> {
  const lines = fs.readFileSync(path, "utf-8").split(/\r?\n/).filter(Boolean);
  return lines.map((line) => {
    const parsed = JSON.parse(line);
    assertValid(parsed.kind, parsed.payload);
    return parsed;
  });
}

export async function sendFrames(url: string, frames: Array<{kind: EnvelopeKind; payload: EventEnvelope | AgentFrame}>) {
  return new Promise<void>((resolve, reject) => {
    const socket = new WebSocket(url);
    let acknowledgements = 0;

    socket.on("open", () => {
      frames.forEach((frame) => socket.send(JSON.stringify(frame)));
    });

    socket.on("message", () => {
      acknowledgements += 1;
      if (acknowledgements >= frames.length) {
        socket.close();
        resolve();
      }
    });

    socket.on("error", (err) => reject(err));
  });
}

async function main() {
  const [logPath = "", url = "ws://localhost:8080"] = process.argv.slice(2);
  if (!logPath) {
    console.error("usage: ts-node scripts/replay.ts <logPath> [url]");
    process.exit(1);
  }
  const frames = readFrames(logPath);
  await sendFrames(url, frames);
  console.log(`replayed ${frames.length} frames to ${url}`);
}

if (require.main === module) {
  main();
}
