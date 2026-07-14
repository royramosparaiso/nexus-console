---
id: voicebox_tts
name: voicebox_tts
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [voicebox_rest, voicebox_mcp]
tags: [voice, tts, stt, whisper, mcp, local, voicebox, skill]
gate: false
optional: true
---

# voicebox_tts

## Identity

```yaml
skills:
  - name: voicebox_tts
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: local-first text-to-speech, speech-to-text (Whisper
dictation), and optional voice cloning via **Voicebox**
(https://github.com/jamiepine/voicebox) — an open-source alternative to hosted
TTS/STT that runs entirely on the operator's machine. Voicebox is a **separate
process**, not vendored into Nexus; this skill only talks to a configured
Voicebox REST endpoint and its HTTP MCP server. No audio leaves the operator's
Voicebox instance and there are no per-character API bills.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `voicebox_rest` | Voicebox REST API | jamiepine/voicebox (external, local) | optional |
| `voicebox_mcp` | Voicebox HTTP MCP server | jamiepine/voicebox (external, local) | optional |

## Inputs

Text to synthesize (+ optional voice id / language / engine) for TTS, or an
audio clip for STT. Configuration comes from Console settings
(`CONSOLE_VOICEBOX_*`): a base URL, an optional API key held server-side, and
the voice-cloning consent flag.

## Outputs

Synthesized audio stream or a transcript as `structured_json`, plus health
metadata (reachable / unreachable, latency, reported version).

## Wiring

Enabled only when the operator sets `CONSOLE_VOICEBOX_ENABLED=true` and a valid
`CONSOLE_VOICEBOX_BASE_URL`. The Console exposes:

- `GET /voicebox/config` — redacted config (never returns the API key).
- `GET /voicebox/status` — best-effort health probe; returns a typed state
  (`disabled` / `unconfigured` / `invalid_url` / `reachable` / `unreachable`).
- `GET /voicebox/cloning-consent` — consent state + ownership notice.

Agents reach Voicebox's own MCP server directly (surfaced as `mcp_url`) so
Claude Code / Cursor / Cline can dictate and speak without a paid TTS API.

## Safety limits

- **Opt-in voice cloning.** Cloning affordances are gated behind
  `CONSOLE_VOICEBOX_VOICE_CLONING_CONSENT=true`. Only clone voices you own or
  have explicit, documented permission to use. Nexus never uploads audio on
  your behalf — cloning happens inside your local Voicebox instance from a
  reference clip you provide there.
- **No secret leakage.** The API key stays server-side; the API only reports
  whether a key is configured.
- **Base URL is validated** (http/https + host) before any request; health
  checks use a short timeout and never crash the Console.
- **Local by default.** Voicebox is meant to run on the operator's machine or
  self-hosted; Nexus imposes no cloud dependency.
