"""Serialise a WizardSubmission to `nexus.instance.yaml`."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.wizard import AVAILABLE_AREAS, WizardSubmission


def _yaml_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if any(c in s for c in " :#") or s == "":
        return f'"{s}"'
    return s


def _yaml_list_inline(items: list) -> str:
    return "[" + ", ".join(_yaml_scalar(i) for i in items) + "]"


def render_instance_yaml(sub: WizardSubmission) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    lines: list[str] = []
    lines.append(f"# nexus.instance.yaml — emitted by Nexus Console wizard")
    lines.append(f"# Generated: {now}")
    lines.append("")
    lines.append(f"apiVersion: nexus.v0.6")
    lines.append(f"kind: Instance")
    lines.append(f"metadata:")
    lines.append(f"  name: {_yaml_scalar(sub.instance_name)}")
    lines.append(f"spec:")

    # persona
    lines.append(f"  persona:")
    lines.append(f"    display_name: {_yaml_scalar(sub.persona.display_name)}")
    lines.append(f"    kind: {sub.persona.kind}")
    if sub.persona.description:
        lines.append(f"    description: {_yaml_scalar(sub.persona.description)}")
    lines.append(f"    default_locale: {sub.persona.default_locale}")

    # deployment
    lines.append(f"  deployment:")
    lines.append(f"    modality: {sub.deployment.modality}")
    if sub.deployment.domain:
        lines.append(f"    domain: {_yaml_scalar(sub.deployment.domain)}")
    if sub.deployment.region:
        lines.append(f"    region: {_yaml_scalar(sub.deployment.region)}")
    lines.append(f"    tls: {_yaml_scalar(sub.deployment.tls)}")
    lines.append(f"    autoscale: {_yaml_scalar(sub.deployment.autoscale)}")

    # llms
    lines.append(f"  llms:")
    lines.append(f"    enabled_providers: {_yaml_list_inline(sub.llms.enabled_providers)}")
    lines.append(f"    roles:")
    lines.append(f"      planner: {_yaml_scalar(sub.llms.roles.planner)}")
    lines.append(f"      coordinator: {_yaml_scalar(sub.llms.roles.coordinator)}")
    lines.append(f"      worker: {_yaml_scalar(sub.llms.roles.worker)}")
    lines.append(f"      embeddings: {_yaml_scalar(sub.llms.roles.embeddings)}")
    lines.append(f"    allow_fallback: {_yaml_scalar(sub.llms.allow_fallback)}")
    lines.append(f"    monthly_budget_usd: {sub.llms.monthly_budget_usd}")

    # memory
    lines.append(f"  memory:")
    lines.append(f"    driver: {sub.memory.driver}")
    lines.append(f"    graph: {sub.memory.graph}")
    lines.append(f"    retention_days: {sub.memory.retention_days}")
    lines.append(f"    encryption_at_rest: {_yaml_scalar(sub.memory.encryption_at_rest)}")

    # areas
    lines.append(f"  areas:")
    lines.append(f"    enabled:")
    for slug in sub.areas.enabled:
        lines.append(f"      - {slug}")

    # stack (optional)
    if sub.stack is not None:
        lines.append(f"  stack:")
        lines.append(f"    tier: {sub.stack.selection.tier}")
        lines.append(f"    monthly_budget_eur: {sub.stack.preferences.monthly_budget_eur}")
        lines.append(f"    deployment_mode: {sub.stack.preferences.deployment_mode}")
        lines.append(f"    estimated_monthly_usd: {sub.stack.selection.estimated_monthly_usd}")
        lines.append(f"    services:")
        for role, slug in sorted(sub.stack.effective_services().items()):
            lines.append(f"      {role}: {_yaml_scalar(slug)}")

    # governance
    lines.append(f"  governance:")
    lines.append(f"    default_autonomy: {sub.governance.default_autonomy}")
    lines.append(f"    kill_switch_enabled: {_yaml_scalar(sub.governance.kill_switch_enabled)}")
    lines.append(f"    audit_retention_days: {sub.governance.audit_retention_days}")
    lines.append(f"    monthly_budget_alert_pct: {sub.governance.monthly_budget_alert_pct}")
    lines.append(f"    require_2fa_for_superadmin: {_yaml_scalar(sub.governance.require_2fa_for_superadmin)}")

    lines.append("")
    return "\n".join(lines)


def compute_warnings(sub: WizardSubmission) -> list[str]:
    warnings: list[str] = []
    if sub.llms.monthly_budget_usd == 0:
        warnings.append("Budget is 0 USD — LLM calls will be blocked at ceiling. OK if you rely only on Ollama.")
    if "ollama" not in sub.llms.enabled_providers and sub.llms.monthly_budget_usd < 10:
        warnings.append("Budget below 10 USD and no local Ollama provider — expect frequent budget blocks.")
    if sub.deployment.modality == "local" and sub.deployment.domain:
        warnings.append("Domain set on a `local` deployment — ignored unless you front it with a tunnel.")
    if sub.deployment.modality in ("fly", "k8s") and not sub.deployment.domain:
        warnings.append("Remote deployment without domain — Platform will only be reachable via its raw endpoint.")
    if sub.governance.default_autonomy == "act_autonomously":
        warnings.append("Default autonomy = act_autonomously. Kill switch is your only guardrail on all agents.")
    if sub.memory.driver == "sqlite" and sub.deployment.modality != "local":
        warnings.append("SQLite memory driver on a remote deployment — fine for prototype, not for prod.")
    return warnings


def default_areas() -> list[str]:
    return [a["slug"] for a in AVAILABLE_AREAS if a["default"]]
