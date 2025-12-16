import {WebSocket} from "ws";
import {EventEnvelope} from "../../packages/types/src/event";

const socket = new WebSocket(process.env.TELEMETRY_URL || "ws://localhost:8080");

function midiPayload(note: number): EventEnvelope {
  return {
    type: "agent",
    timestamp: Date.now() / 1000,
    payload: {
      POINTER_DELTA: {dx: note / 127, dy: note / 254},
      ZOOM_DELTA: note / 100,
      ROT_DELTA: 0,
      INPUT_TRIGGER: true,
    },
  };
}

socket.on("open", () => {
  [40, 60, 80].forEach((note) => socket.send(JSON.stringify({kind: "event.v1", payload: midiPayload(note)})));
  socket.close();
});
