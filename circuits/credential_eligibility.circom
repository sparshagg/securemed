pragma circom 2.1.6;

include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";

template CredentialEligibility() {
    signal input credentialSecret;
    signal input roleCode;
    signal input expiryDay;
    signal input salt;

    signal input credentialCommitment;
    signal input requiredRole;
    signal input currentDay;

    signal output eligible;

    component commitmentHasher = Poseidon(4);
    commitmentHasher.inputs[0] <== credentialSecret;
    commitmentHasher.inputs[1] <== roleCode;
    commitmentHasher.inputs[2] <== expiryDay;
    commitmentHasher.inputs[3] <== salt;
    commitmentHasher.out === credentialCommitment;

    roleCode === requiredRole;

    component expiryCheck = LessThan(32);
    expiryCheck.in[0] <== currentDay;
    expiryCheck.in[1] <== expiryDay;
    eligible <== expiryCheck.out;
    eligible === 1;
}

component main { public [credentialCommitment, requiredRole, currentDay] } = CredentialEligibility();
