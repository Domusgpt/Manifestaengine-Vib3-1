import assert from "assert";
import {readFileSync} from "fs";
import {computeElasticity} from "../src/elasticity";
import {multiply, normalize, Quaternion, rotateVector, slerp} from "../src/quaternion";

function approxEqual(actual: number, expected: number, tol = 1e-3) {
  assert(Math.abs(actual - expected) <= tol, `expected ${actual} ~ ${expected}`);
}

function testQuaternion() {
  const vectors = JSON.parse(readFileSync("tests/vectors/quaternion.json", "utf-8"));
  const norm = normalize(vectors.normalize.input as Quaternion);
  norm.forEach((value: number, idx: number) => approxEqual(value, vectors.normalize.expected[idx]));

  const mult = multiply(vectors.multiply.a as Quaternion, vectors.multiply.b as Quaternion);
  mult.forEach((value: number, idx: number) => approxEqual(value, vectors.multiply.expected[idx]));

  const slerped = slerp(vectors.slerp.a as Quaternion, vectors.slerp.b as Quaternion, vectors.slerp.t);
  slerped.forEach((value: number, idx: number) => approxEqual(value, vectors.slerp.expected[idx]));

  const rotated = rotateVector(vectors.rotate.vector as [number, number, number], vectors.rotate.q as Quaternion);
  rotated.forEach((value: number, idx: number) => approxEqual(value, vectors.rotate.expected[idx]));
}

function testElasticity() {
  const cases = JSON.parse(readFileSync("tests/vectors/elasticity.json", "utf-8"));
  cases.forEach((entry: any) => {
    const result = computeElasticity(entry as any);
    approxEqual(result.tension, entry.expected.tension);
    result.force.forEach((value: number, idx: number) => approxEqual(value, entry.expected.force[idx]));
    approxEqual(result.potentialEnergy, entry.expected.potentialEnergy, 1e-2);
  });
}

function main() {
  testQuaternion();
  testElasticity();
  console.log("math tests passed");
}

main();
