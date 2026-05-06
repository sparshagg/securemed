# FastAPI Streaming Patterns

Use this reference only when an endpoint must stream JSON Lines, events, or bytes.

## Defaults

- Use normal typed return models unless streaming is required.
- For JSON Lines, return one JSON object per line and document the media type.
- For Server-Sent Events, use a maintained SSE response implementation and keep event payloads public-safe.
- For byte streaming, use `StreamingResponse` and avoid loading large files into memory.

## SecureMed Notes

- Do not stream plaintext EMRs unless a demo endpoint explicitly requires provider-side decrypted output.
- Never stream DEKs, private keys, raw credential witnesses, or trusted setup toxic waste.
- Audit streaming endpoints the same way as normal access endpoints when they reveal protected record material.

