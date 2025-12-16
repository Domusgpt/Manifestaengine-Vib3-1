export interface SpringState {
  restLength: number;
  stiffness: number;
  damping: number;
}

export interface ElasticInput {
  position: [number, number, number];
  anchor: [number, number, number];
  velocity: [number, number, number];
  state: SpringState;
}

export interface ElasticOutput {
  tension: number;
  force: [number, number, number];
  potentialEnergy: number;
}

export function computeElasticity(input: ElasticInput): ElasticOutput {
  const [px, py, pz] = input.position;
  const [ax, ay, az] = input.anchor;
  const [vx, vy, vz] = input.velocity;
  const {restLength, stiffness, damping} = input.state;

  const dx = px - ax;
  const dy = py - ay;
  const dz = pz - az;
  const distance = Math.hypot(dx, dy, dz);
  const stretch = distance - restLength;

  const nx = distance === 0 ? 0 : dx / distance;
  const ny = distance === 0 ? 0 : dy / distance;
  const nz = distance === 0 ? 0 : dz / distance;

  const projectedVelocity = vx * nx + vy * ny + vz * nz;
  const dampingForce = damping * projectedVelocity;

  const forceMagnitude = stiffness * stretch + dampingForce;
  const force: [number, number, number] = [forceMagnitude * nx, forceMagnitude * ny, forceMagnitude * nz];

  const potentialEnergy = 0.5 * stiffness * stretch * stretch;

  return {
    tension: Math.abs(forceMagnitude),
    force,
    potentialEnergy,
  };
}
