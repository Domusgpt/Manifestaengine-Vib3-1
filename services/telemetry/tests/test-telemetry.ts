import assert from "assert";
import {assertValid} from "../../../packages/types/src/event";
import eventSchema from "../../../schema/event.v1.json";
import agentFrameSchema from "../../../schema/agent_frame.v1.json";

function sampleEvent() {
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

function sampleAgent() {
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

function main() {
  testSchemas();
  testValidation();
  console.log("telemetry schema tests passed");
}

main();
