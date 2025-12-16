import Ajv, {ValidateFunction} from "ajv";
import eventSchema from "../../../schema/event.v1.json";
import agentFrameSchema from "../../../schema/agent_frame.v1.json";

export type MinimalParameters = {
  POINTER_DELTA: { dx: number; dy: number };
  ZOOM_DELTA: number;
  ROT_DELTA: number;
  INPUT_TRIGGER: boolean;
  HOLO_FRAME?: HoloFrame;
};

export type HoloFrame = {
  quaternion: [number, number, number, number];
  translation: [number, number, number];
  surface: string;
  metadata?: Record<string, unknown>;
};

export type EventEnvelope = {
  type: "input" | "holo_frame" | "agent";
  timestamp: number;
  payload: MinimalParameters;
};

export type AgentFrame = {
  role: string;
  goal: string;
  sdk_surface: string;
  bounds: { x: number; y: number; z: number };
  focus: { path: string; hoist?: boolean };
  inputs: MinimalParameters;
  outputs: string[];
  safety: { spawn_bounds: number; rate_limit: number; rejection_reason?: string };
  telemetry?: { latency_ms?: number; jitter_ms?: number; replay_frame?: string };
};

export type EnvelopeKind = "event.v1" | "agent_frame.v1";

const ajv = new Ajv({allErrors: true, strict: false});
const validateEvent = ajv.compile<EventEnvelope>(eventSchema as any) as ValidateFunction<EventEnvelope>;
const validateAgentFrame = ajv.compile<AgentFrame>(agentFrameSchema as any) as ValidateFunction<AgentFrame>;

export function validator(kind: EnvelopeKind): ValidateFunction<EventEnvelope | AgentFrame> {
  if (kind === "event.v1") return validateEvent;
  if (kind === "agent_frame.v1") return validateAgentFrame;
  throw new Error(`Unknown envelope kind: ${kind}`);
}

export function assertValid(kind: EnvelopeKind, payload: EventEnvelope | AgentFrame): void {
  const validate = validator(kind);
  const valid = validate(payload);
  if (!valid) {
    const message = validate.errors?.map((err) => `${err.instancePath} ${err.message}`).join("; ") || "validation failed";
    throw new Error(message);
  }
}
