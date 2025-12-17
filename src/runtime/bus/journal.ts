import fs from "fs";
import path from "path";
import {AgentFrame, EnvelopeKind, EventEnvelope, validator} from "../../../packages/types/src/event";

export type JournalEntry = {kind: EnvelopeKind; payload: EventEnvelope | AgentFrame};

export class SignalJournal {
  constructor(private readonly logPath: string) {
    const dir = path.dirname(logPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, {recursive: true});
    }
  }

  append(entry: JournalEntry) {
    const validate = validator(entry.kind);
    if (!validate(entry.payload as any)) {
      const message = validate.errors?.map((err) => `${err.instancePath} ${err.message}`).join("; ") || "validation failed";
      throw new Error(message);
    }
    fs.appendFileSync(this.logPath, JSON.stringify(entry) + "\n", "utf-8");
  }

  readAll(): JournalEntry[] {
    if (!fs.existsSync(this.logPath)) return [];
    const lines = fs.readFileSync(this.logPath, "utf-8").split(/\r?\n/).filter(Boolean);
    return lines.map((line) => JSON.parse(line) as JournalEntry);
  }

  clear() {
    if (fs.existsSync(this.logPath)) fs.unlinkSync(this.logPath);
  }
}
