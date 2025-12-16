import assert from "assert";
import fs from "fs";
import path from "path";
import {startServer} from "../../services/telemetry/ws-server/index";
import {EventEnvelope} from "../../packages/types/src/event";

function writeLog(tmpPath: string) {
  const lines: Array<{kind: string; payload: EventEnvelope}> = [
    {
      kind: "event.v1",
      payload: {
        type: "input",
        timestamp: 1.1,
        payload: {
          POINTER_DELTA: {dx: 0.1, dy: 0.2},
          ZOOM_DELTA: 0.9,
          ROT_DELTA: 0.01,
          INPUT_TRIGGER: true,
        },
      },
    },
    {
      kind: "event.v1",
      payload: {
        type: "holo_frame",
        timestamp: 1.2,
        payload: {
          POINTER_DELTA: {dx: 0, dy: 0},
          ZOOM_DELTA: 1,
          ROT_DELTA: 0,
          INPUT_TRIGGER: false,
          HOLO_FRAME: {
            quaternion: [0, 0, 0, 1],
            translation: [0, 0, 0],
            surface: "holographic",
          },
        },
      },
    },
  ];
  const content = lines.map((entry) => JSON.stringify(entry)).join("\n");
  fs.writeFileSync(tmpPath, content);
}

async function main() {
  const tmpPath = path.join("./", "tmp-replay.jsonl");
  writeLog(tmpPath);
  assert.ok(fs.existsSync(tmpPath));
  const {server} = startServer(8091);
  const replay = await import("../replay");
  await replay.sendFrames("ws://localhost:8091", replay.readFrames(tmpPath));
  fs.unlinkSync(tmpPath);
  assert.ok(!fs.existsSync(tmpPath));
  server.close();
  console.log("replay harness test passed");
}

main();
