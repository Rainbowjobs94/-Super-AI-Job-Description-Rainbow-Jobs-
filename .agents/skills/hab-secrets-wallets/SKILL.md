---
name: hab-secrets-wallets
description: Separate public chain/wallet/vault configuration from signing secrets and plan secure credential provisioning. Use for API keys, wallets, vault addresses, keystore encryption or hard-coded configuration without putting private keys in source.
---

# Secretless repository configuration

1. Classify each value before storing it. Public chain IDs, token/vault/treasury
   addresses and RPC URL names may be versioned after network/ownership review.
   API keys, authenticated RPC URLs, private keys, seeds, cookies and connection
   credentials may not. Addresses can still be privacy-sensitive.
2. Use workspace Secrets, n8n credentials or a reviewed secret manager. Request
   secrets through that system, never chat. Frontends receive no signing secret.
3. Prefer external/hardware/multisig signing for consequential transactions.
   Build unsigned requests for human review of chain, destination, amount,
   method, fees and permissions; do not authorize signing through a skill.
4. If keystore encryption is required, use a maintained wallet/keystore
   implementation with authenticated encryption and reviewed key derivation.
   Keep decryption keys separate from encrypted material and outside Git.
   Base64, obfuscation or ciphertext beside its key does not protect a wallet.
5. Define least privilege, rotation, revocation, backup/recovery, access logs,
   expiry, rate/spend limits and emergency pause. Test with synthetic secrets.
6. Scan diffs, logs, archives and history before publication. If a genuine
   credential was exposed, revoke/rotate through its provider and review use;
   do not reproduce its value in a report.
7. Keep raw sensitive evidence and secrets off immutable blockchains.

## Safe illustrative config (not deployed)

    chainId: <reviewed chain ID>
    tokenAddress: <verified public contract address>
    vaultAddress: <verified public vault address>
    credentialRef: <opaque secret-manager reference, not the value>
    signingMode: external-human-approved
    financialActivation: disabled

Never hard-code a private key, seed or decryption key. Encryption is not a grant
of custody, provider access, financial approval or security certification.
