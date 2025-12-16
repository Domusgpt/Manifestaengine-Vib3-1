import assert from "assert";
import fs from "fs";
import path from "path";
import {startServer} from "../../services/telemetry/ws-server/index";
import {EventEnvelope} from "../../packages/types/src/event";

function writeLog(tmpPath: string) {
  const payload: EventEnvelope = {
    type: "input",
    timestamp: 1.1,
    payload: {
      POINTER_DELTA: {dx: 0.1, dy: 0.2},
      ZOOM_DELTA: 0.9,
      ROT_DELTA: 0.01,
      INPUT_TRIGGER: true,
    },
  };
  fs.writeFileSync(tmpPath, JSON.stringify({kind: "event.v1", payload}));
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
