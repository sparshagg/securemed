import { buildPoseidon } from "circomlibjs";

const values = process.argv.slice(2);

if (values.length !== 4) {
  console.error(
    "usage: node scripts/zkp/credential_commitment.mjs <credential_secret> <role_code> <expiry_day> <salt>",
  );
  process.exit(2);
}

const poseidon = await buildPoseidon();
const field = poseidon.F;
const commitment = poseidon(values.map((value) => BigInt(value)));
console.log(field.toString(commitment));
