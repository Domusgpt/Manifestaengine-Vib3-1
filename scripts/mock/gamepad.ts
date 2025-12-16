import {WebSocket} from "ws";
import {EventEnvelope} from "../../packages/types/src/event";

const socket = new WebSocket(process.env.TELEMETRY_URL || "ws://localhost:8080");

const inputs: EventEnvelope[] = [
  {
    type: "input",
    timestamp: Date.now() / 1000,
    payload: {
      POINTER_DELTA: {dx: 0.2, dy: -0.1},
      ZOOM_DELTA: 0.5,
      ROT_DELTA: 0.1,
      INPUT_TRIGGER: true,
    },
  },
  {
    type: "input",
    timestamp: Date.now() / 1000 + 0.1,
    payload: {
      POINTER_DELTA: {dx: -0.3, dy: 0.4},
      ZOOM_DELTA: 0.75,
      ROT_DELTA: -0.05,
      INPUT_TRIGGER: false,
    },
  },
];

socket.on("open", () => {
  inputs.forEach((payload) => socket.send(JSON.stringify({kind: "event.v1", payload})));
  socket.close();
});
