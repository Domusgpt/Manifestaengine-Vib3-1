import assert from "assert";
import {WebSocket} from "ws";
import {startServer} from "../ws-server/index";

async function sendPayload(url: string, payload: unknown): Promise<any> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(url);
    socket.on("open", () => socket.send(JSON.stringify(payload)));
    socket.on("message", (data) => {
      resolve(JSON.parse(data.toString()));
      socket.close();
    });
    socket.on("error", (err) => reject(err));
  });
}

async function main() {
  const {server} = startServer(8090);
  const response = await sendPayload("ws://localhost:8090", {
    kind: "event.v1",
    payload: {
      type: "input",
      timestamp: 5.0,
      payload: {
        POINTER_DELTA: {dx: 0.4, dy: 0.2},
        ZOOM_DELTA: 1.2,
        ROT_DELTA: 0.0,
        INPUT_TRIGGER: false,
      },
    },
  });
  assert.strictEqual(response.status, "ok");
  server.close();
  console.log("ws dispatch test passed");
}

main();
