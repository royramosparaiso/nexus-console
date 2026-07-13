"""nexus.handoff.md — human-readable deploy playbook.

After the wizard finishes, Console writes two files into the instance's
deployments directory:

  * `nexus.handoff.md`   — a Markdown playbook you can hand to another
                            operator (or a setup-automation agent like
                            Cloud Cowork / OpenClaw) and they can execute
                            the deploy from scratch.
  * `nexus.secrets.env`   — key=value pairs for every ${VAR} the playbook
                            references. Permissions 0600. NOT committed to
                            git. This file is the ONLY place real secret
                            values live on disk.

The playbook itself NEVER contains a real secret value. Every reference is
${VAR_NAME}, resolved from the .env at deploy time. This lets you email or
paste the playbook safely; the .env stays on the operator's disk.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.services.cloud_deployers import PlaybookInputs


PLAYBOOK_FILENAME = "nexus.handoff.md"
SECRETS_FILENAME = "nexus.secrets.env"


def render_playbook(p: PlaybookInputs, bootstrap_token: str) -> str:
    """Return the Markdown body. Caller writes it wherever it wants."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append(f"# Nexus OS Handoff Playbook — {p.instance_name}")
    lines.append("")
    lines.append(
        "This playbook describes exactly what to do to deploy a fresh Nexus "
        "Platform instance for this user. Every command is meant to be "
        "reviewed and executed by a human operator or by a setup-automation "
        "agent (Cloud Cowork, OpenClaw). Console has NOT executed anything "
        "yet — the compose files and provider configs are prepared, and the "
        "deploy is left to you."
    )
    lines.append("")
    lines.append("## Instance metadata")
    lines.append("")
    lines.append(f"- **Instance ID**: `{p.instance_id}`")
    lines.append(f"- **Name**: {p.instance_name}")
    lines.append(f"- **Modality**: `{p.modality}`")
    lines.append(f"- **Region**: `{p.region or '(unspecified)'}`")
    lines.append(f"- **Domain**: `{p.domain or '(none — using provider default hostname)'}`")
    lines.append(f"- **Endpoint hint**: `{p.endpoint_hint}`")
    lines.append(f"- **Generated at**: {now}")
    lines.append("")

    lines.append("## Files in this directory")
    lines.append("")
    lines.append(
        "The provisioner has written the following files alongside this "
        "playbook. **Read them before running the deploy.**"
    )
    lines.append("")
    lines.append("- `docker-compose.yml` — Postgres + Kokoro + Platform stack. Same for all modalities.")
    if p.modality == "fly":
        lines.append("- `fly.toml` — Fly.io app config for the Platform service.")
    if p.modality == "hetzner":
        lines.append("- `cloud-init.yaml` — Ubuntu cloud-init user-data (writes Compose files + starts them).")
    lines.append("- `.env.example` — placeholder env with the generated bootstrap token.")
    lines.append(f"- `{SECRETS_FILENAME}` — **real secret values (0600).** Never commit. Never paste in chat.")
    lines.append("")

    lines.append("## Required secrets")
    lines.append("")
    lines.append(
        f"Before running any of the commands below, populate `{SECRETS_FILENAME}` "
        "with the following variables. The playbook references them as "
        "`${VAR_NAME}` — DO NOT inline the real values into commands."
    )
    lines.append("")
    for s in p.required_secrets:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append(f"```bash")
    lines.append(f"# Load secrets into your shell environment before running any step below")
    lines.append(f"set -a && source ./{SECRETS_FILENAME} && set +a")
    lines.append(f"```")
    lines.append("")

    lines.append("## Deploy steps")
    lines.append("")
    lines.append(
        "Run the steps in order. Each is idempotent enough that re-running a "
        "failed step from the last checkpoint is safe."
    )
    lines.append("")
    for i, step in enumerate(p.provider_steps, 1):
        lines.append(f"### Step {i} — {step['title']}")
        lines.append("")
        lines.append("```bash")
        lines.append(step["cmd"])
        lines.append("```")
        lines.append("")

    lines.append("## Post-deploy verification")
    lines.append("")
    lines.append("After the deploy commands finish, verify the instance is healthy:")
    lines.append("")
    lines.append("```bash")
    for check in p.post_deploy_checks:
        lines.append(check)
    lines.append("```")
    lines.append("")

    lines.append("## Handing back to Console")
    lines.append("")
    lines.append(
        "Once Platform is up and reachable, tell Console to complete the "
        "bootstrap handshake by POSTing to `/wizard/{instance_id}/complete-remote`. "
        "Console already holds the bootstrap token and the manifest \u2014 it "
        "only needs to know the real endpoint (in case the domain differs from "
        "what the wizard predicted). Console will sign the bootstrap request, "
        "call `/_bootstrap` on Platform, burn the token, and flip the instance "
        "status to `running`."
    )
    lines.append("")
    lines.append("```bash")
    lines.append(
        f"curl -X POST http://localhost:7000/wizard/{p.instance_id}/complete-remote \\\n"
        "     -H 'Content-Type: application/json' \\\n"
        f"     -d '{{\"endpoint\":\"{p.endpoint_hint}\"}}'"
    )
    lines.append("```")
    lines.append("")
    lines.append(
        "If the real domain differs from the placeholder above, replace it in "
        "the `endpoint` field. To retry after a failed bootstrap (e.g. Platform "
        "was not healthy yet), simply POST again \u2014 the token remains valid "
        "until the handshake succeeds."
    )
    lines.append("")

    lines.append("## Safety notes")
    lines.append("")
    lines.append(
        "- **Never** commit `nexus.secrets.env` to git. Add it to `.gitignore` "
        "in the same commit that adds this playbook.\n"
        "- **Never** paste the contents of `nexus.secrets.env` in chat, tickets, "
        "or logs. If a secret leaks, rotate it immediately (`fly secrets set` "
        "or `hcloud server` env update, then restart Compose).\n"
        "- The `PLATFORM_BOOTSTRAP_TOKEN` is single-use in effect — Platform "
        "will only accept the first `/_bootstrap` call that presents it. Any "
        "later attempts fail with `invalid_token`.\n"
        "- Kokoro (voice TTS) is included in the compose stack. If you want a "
        "voiceless deploy, remove the `kokoro` service and unset `KOKORO_URL` "
        "on Platform — `/_voice/stream` will send `{\"event\":\"unavailable\"}`.\n"
    )

    return "\n".join(lines) + "\n"


def render_secrets(p: PlaybookInputs, bootstrap_token: str) -> str:
    """Return the raw `nexus.secrets.env` body with placeholders and the token."""
    lines = [
        "# Nexus OS secrets — populate before running the playbook.",
        f"# Instance: {p.instance_name} ({p.instance_id})",
        f"# Modality: {p.modality}",
        "# DO NOT COMMIT. DO NOT PASTE. chmod 600 this file.",
        "",
        f"PLATFORM_BOOTSTRAP_TOKEN={bootstrap_token}",
    ]
    for s in p.required_secrets:
        if s == "PLATFORM_BOOTSTRAP_TOKEN":
            continue  # already emitted with the real value
        lines.append(f"{s}=CHANGE_ME_{s.lower()}")
    lines.append("")
    return "\n".join(lines)


def write_playbook(
    p: PlaybookInputs, bootstrap_token: str,
) -> tuple[Path, Path]:
    """Write both files under `p.deployments_dir`. Returns (playbook, secrets)."""
    playbook = p.deployments_dir / PLAYBOOK_FILENAME
    secrets_env = p.deployments_dir / SECRETS_FILENAME

    playbook.write_text(render_playbook(p, bootstrap_token), encoding="utf-8")
    secrets_env.write_text(render_secrets(p, bootstrap_token), encoding="utf-8")
    try:
        secrets_env.chmod(0o600)
    except OSError:
        pass  # Windows / read-only mounts — best-effort

    # Guardrail: make sure the secrets file never sneaks into git.
    gitignore = p.deployments_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(f"{SECRETS_FILENAME}\n.env\n", encoding="utf-8")

    return playbook, secrets_env
