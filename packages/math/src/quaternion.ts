export type Quaternion = [number, number, number, number];

export function normalize(q: Quaternion): Quaternion {
  const [x, y, z, w] = q;
  const mag = Math.hypot(x, y, z, w) || 1;
  return [x / mag, y / mag, z / mag, w / mag];
}

export function multiply(a: Quaternion, b: Quaternion): Quaternion {
  const [ax, ay, az, aw] = a;
  const [bx, by, bz, bw] = b;
  return [
    aw * bx + ax * bw + ay * bz - az * by,
    aw * by - ax * bz + ay * bw + az * bx,
    aw * bz + ax * by - ay * bx + az * bw,
    aw * bw - ax * bx - ay * by - az * bz,
  ];
}

export function slerp(a: Quaternion, b: Quaternion, t: number): Quaternion {
  let cosHalfTheta = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
  if (cosHalfTheta < 0) {
    b = [-b[0], -b[1], -b[2], -b[3]];
    cosHalfTheta = -cosHalfTheta;
  }
  if (Math.abs(cosHalfTheta) >= 1.0) {
    return normalize(a);
  }
  const halfTheta = Math.acos(Math.min(1, Math.max(-1, cosHalfTheta)));
  const sinHalfTheta = Math.sqrt(1.0 - cosHalfTheta * cosHalfTheta) || 1;
  const ratioA = Math.sin((1 - t) * halfTheta) / sinHalfTheta;
  const ratioB = Math.sin(t * halfTheta) / sinHalfTheta;
  return normalize([
    a[0] * ratioA + b[0] * ratioB,
    a[1] * ratioA + b[1] * ratioB,
    a[2] * ratioA + b[2] * ratioB,
    a[3] * ratioA + b[3] * ratioB,
  ]);
}

export function rotateVector(v: [number, number, number], q: Quaternion): [number, number, number] {
  const [x, y, z] = v;
  const [qx, qy, qz, qw] = normalize(q);
  // q * v * q^-1 with simplified math
  const ix = qw * x + qy * z - qz * y;
  const iy = qw * y + qz * x - qx * z;
  const iz = qw * z + qx * y - qy * x;
  const iw = -qx * x - qy * y - qz * z;
  return [
    ix * qw + iw * -qx + iy * -qz - iz * -qy,
    iy * qw + iw * -qy + iz * -qx - ix * -qz,
    iz * qw + iw * -qz + ix * -qy - iy * -qx,
  ];
}
