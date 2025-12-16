import assert from "assert";
import fs from "fs";
import path from "path";
import {AgentFrame, assertValid, EventEnvelope} from "../../../packages/types/src/event";
import {IMURingBuffer} from "../../../src/runtime/buffers/imuBuffer";
import {SignalJournal} from "../../../src/runtime/bus/journal";
import eventSchema from "../../../schema/event.v1.json";
import agentFrameSchema from "../../../schema/agent_frame.v1.json";

function sampleEvent(): EventEnvelope {
  return {
    type: "input",
    timestamp: 1.23,
    payload: {
      POINTER_DELTA: {dx: 0.1, dy: -0.2},
      ZOOM_DELTA: 1.0,
      ROT_DELTA: 0.0,
      INPUT_TRIGGER: true,
      HOLO_FRAME: {quaternion: [0, 0, 0, 1], translation: [0, 0, 0], surface: "holographic"},
    },
  };
}

function sampleAgent(): AgentFrame {
  return {
    role: "navigator",
    goal: "stabilize overlay",
    sdk_surface: "wearable",
    bounds: {x: 1, y: 1, z: 1},
    focus: {path: "holographic.scene:anchor/base"},
    inputs: sampleEvent().payload,
    outputs: ["render.intent.apply"],
    safety: {spawn_bounds: 10, rate_limit: 5, rejection_reason: ""},
  };
}

function testSchemas() {
  assert(eventSchema.properties.payload.properties.HOLO_FRAME);
  assert(agentFrameSchema.properties.inputs.properties.HOLO_FRAME);
}

function testValidation() {
  assertValid("event.v1", sampleEvent());
  assertValid("agent_frame.v1", sampleAgent());
}

function testIMURingBuffer() {
  const buffer = new IMURingBuffer(2);
  buffer.push({ts: 1, quaternion: [0, 0, 0, 1]});
  buffer.push({ts: 2, quaternion: [0, 1, 0, 0], acceleration: [0.1, 0.2, 0.3]});
  const snap = buffer.snapshot();
  assert.strictEqual(snap.length, 2);
  assert.deepStrictEqual(buffer.latest()?.quaternion, [0, 1, 0, 0]);
  buffer.push({ts: 3, quaternion: [1, 0, 0, 0]});
  assert.strictEqual(buffer.snapshot().length, 2, "ring buffer should evict oldest sample");
}

function testSignalJournal() {
  const tmpPath = path.join(process.cwd(), "tmp", "journal.jsonl");
  const journal = new SignalJournal(tmpPath);
  journal.clear();
  const payload: EventEnvelope = sampleEvent();
  journal.append({kind: "event.v1", payload});
  const entries = journal.readAll();
  assert.strictEqual(entries.length, 1);
  assert.strictEqual(entries[0].kind, "event.v1");
  const entryPayload = entries[0].payload as EventEnvelope;
  assert.strictEqual(entryPayload.payload.INPUT_TRIGGER, payload.payload.INPUT_TRIGGER);
  journal.clear();
  if (fs.existsSync(tmpPath)) throw new Error("journal did not clear");
}

function main() {
  testSchemas();
  testValidation();
  testIMURingBuffer();
  testSignalJournal();
  console.log("telemetry schema tests passed");
}

main();
