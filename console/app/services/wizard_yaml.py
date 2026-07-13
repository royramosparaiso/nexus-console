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
        # Import here so the yaml module doesn't hard-depend on the
        # provisioning layer for its own tests.
        from app.models.host_capabilities import assess_host
        from app.services.stack_provisioning import handoff_for

        lines.append(f"  stack:")
        lines.append(f"    tier: {sub.stack.selection.tier}")
        lines.append(f"    monthly_budget_eur: {sub.stack.preferences.monthly_budget_eur}")
        lines.append(f"    deployment_mode: {sub.stack.preferences.deployment_mode}")
        lines.append(f"    estimated_monthly_usd: {sub.stack.selection.estimated_monthly_usd}")

        # Kernel — always emitted, never configurable through the catalogue.
        from app.models.kernel import DEFAULT_HERMES_AGENTS

        kernel = sub.stack.kernel
        lines.append(f"    kernel:")
        lines.append(f"      # Always deployed. Not part of the stack catalogue.")
        lines.append(f"      hermes:")
        lines.append(f"        engine: {kernel.hermes.engine}")
        lines.append(f"        features:")
        for feat in kernel.hermes.features:
            lines.append(f"          - {feat}")
        secrets = kernel.hermes.required_secrets()
        if secrets:
            lines.append(f"        required_secrets:")
            for s in secrets:
                lines.append(f"          - {s}")
        # Default agents that Hermes registers on the `hermes-agents`
        # task queue at boot. The operator adds more via Nexus Studios.
        lines.append(f"        default_agents:")
        lines.append(
            f"          # Registered on the `hermes-agents` queue at kernel boot."
        )
        for agent in DEFAULT_HERMES_AGENTS:
            lines.append(f"          - name: {agent['name']}")
            lines.append(f"            queue: {agent['queue']}")
            lines.append(f"            role: {agent['role']}")
            lines.append(f"            note: {agent['note']!r}")

        # Host capabilities — what laptop the operator is running from.
        if sub.stack.host is not None:
            host = sub.stack.host
            lines.append(f"    host:")
            lines.append(f"      os: {host.os}")
            if host.os_version:
                lines.append(f"      os_version: {_yaml_scalar(host.os_version)}")
            lines.append(f"      arch: {host.arch}")
            if host.cpu_cores is not None:
                lines.append(f"      cpu_cores: {host.cpu_cores}")
            if host.ram_gb is not None:
                lines.append(f"      ram_gb: {host.ram_gb}")
            if host.free_disk_gb is not None:
                lines.append(f"      free_disk_gb: {host.free_disk_gb}")
            lines.append(f"      has_gpu: {_yaml_scalar(host.has_gpu)}")
            if host.gpu_model:
                lines.append(f"      gpu_model: {_yaml_scalar(host.gpu_model)}")
            lines.append(f"      docker_available: {_yaml_scalar(host.docker_available)}")

            assessment = assess_host(host)
            lines.append(f"      local_supported: {_yaml_scalar(assessment.local_supported)}")
            if assessment.reasons:
                lines.append(f"      local_blockers:")
                for reason in assessment.reasons:
                    lines.append(f"        - {_yaml_scalar(reason)}")
            if assessment.warnings:
                lines.append(f"      host_warnings:")
                for w in assessment.warnings:
                    lines.append(f"        - {_yaml_scalar(w)}")
        lines.append(f"    # handoff=builder: nexus.handoff.md will include "
                     f"scripted provisioning steps.")
        lines.append(f"    # handoff=manual : self-hosted or dashboard-only "
                     f"\u2014 the operator runs it out-of-band.")
        lines.append(f"    services:")
        automated: list[str] = []
        manual: list[str] = []
        for role, slug in sorted(sub.stack.effective_services().items()):
            has_builder = handoff_for(slug) is not None
            marker = "builder" if has_builder else "manual"
            lines.append(
                f"      {role}: {{ slug: {_yaml_scalar(slug)}, handoff: {marker} }}"
            )
            (automated if has_builder else manual).append(f"{role}={slug}")
        lines.append(f"    handoff_summary:")
        lines.append(
            f"      automated: {_yaml_scalar(', '.join(automated) or '(none)')}"
        )
        lines.append(
            f"      manual:    {_yaml_scalar(', '.join(manual) or '(none)')}"
        )

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
    if (
        sub.stack is not None
        and sub.stack.host is not None
        and sub.stack.preferences.deployment_mode == "local"
    ):
        from app.models.host_capabilities import assess_host
        assessment = assess_host(sub.stack.host)
        if not assessment.local_supported:
            warnings.append(
                "Host does not meet the local-deployment bar: "
                + "; ".join(assessment.reasons)
                + ". Consider switching deployment_mode to `cloud`."
            )
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
