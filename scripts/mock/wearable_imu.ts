import {WebSocket} from "ws";
import {EventEnvelope} from "../../packages/types/src/event";

const socket = new WebSocket(process.env.TELEMETRY_URL || "ws://localhost:8080");

function samplePayload(counter: number): EventEnvelope {
  return {
    type: "input",
    timestamp: Date.now() / 1000,
    payload: {
      POINTER_DELTA: {dx: Math.sin(counter / 10), dy: Math.cos(counter / 10)},
      ZOOM_DELTA: 1 + counter * 0.01,
      ROT_DELTA: 0.05 * counter,
      INPUT_TRIGGER: counter % 5 === 0,
      HOLO_FRAME: {
        quaternion: [0, 0, 0, 1],
        translation: [0, 0, 0],
        surface: "wearable",
      },
    },
  };
}

socket.on("open", () => {
  let counter = 0;
  const interval = setInterval(() => {
    const payload = samplePayload(counter++);
    socket.send(JSON.stringify({kind: "event.v1", payload}));
    if (counter > 10) {
      clearInterval(interval);
      socket.close();
    }
  }, 10);
});
