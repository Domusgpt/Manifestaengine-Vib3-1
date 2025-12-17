import {createServer} from "http";
import {WebSocketServer, WebSocket} from "ws";
import {assertValid, EnvelopeKind, EventEnvelope, AgentFrame} from "../../../packages/types/src/event";

const PORT = parseInt(process.env.PORT || "8080", 10);

function validateEnvelope(kind: EnvelopeKind, payload: unknown) {
  assertValid(kind, payload as EventEnvelope | AgentFrame);
}

function telemetryMessage(message: string): {kind: EnvelopeKind; payload: EventEnvelope | AgentFrame} {
  const parsed = JSON.parse(message);
  const kind = parsed.kind as EnvelopeKind;
  const payload = parsed.payload as EventEnvelope | AgentFrame;
  validateEnvelope(kind, payload);
  return {kind, payload};
}

function buildResponse(kind: EnvelopeKind, payload: EventEnvelope | AgentFrame) {
  return JSON.stringify({status: "ok", kind, minimal: payload});
}

export function startServer(port = PORT) {
  const server = createServer();
  const wss = new WebSocketServer({server});

  wss.on("connection", (socket: WebSocket) => {
    socket.on("message", (data) => {
      try {
        const {kind, payload} = telemetryMessage(data.toString());
        socket.send(buildResponse(kind, payload));
      } catch (err) {
        socket.send(JSON.stringify({status: "error", error: (err as Error).message}));
      }
    });
  });

  server.listen(port, () => {
    console.log(`telemetry ws-server listening on ${port}`);
  });

  return {server, wss};
}

if (require.main === module) {
  startServer();
}
