export type IMUSample = {
  ts: number; // monotonic seconds
  quaternion: [number, number, number, number];
  acceleration?: [number, number, number];
  gyro?: [number, number, number];
};

export class IMURingBuffer {
  private readonly capacity: number;
  private buffer: IMUSample[] = [];

  constructor(capacity = 256) {
    if (capacity <= 0) throw new Error("capacity must be positive");
    this.capacity = capacity;
  }

  push(sample: IMUSample) {
    if (this.buffer.length > 0 && sample.ts < this.buffer[this.buffer.length - 1].ts) {
      throw new Error("samples must be appended in monotonic order");
    }
    this.buffer.push(sample);
    if (this.buffer.length > this.capacity) {
      this.buffer.shift();
    }
  }

  snapshot(): IMUSample[] {
    return [...this.buffer];
  }

  latest(): IMUSample | undefined {
    return this.buffer[this.buffer.length - 1];
  }

  clear() {
    this.buffer = [];
  }
}
