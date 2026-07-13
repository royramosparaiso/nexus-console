"""Host discovery: commands, parsers, assessment, wizard integration."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.host_capabilities import (
    DISCOVERY_INSTRUCTIONS,
    HostCapabilities,
    MIN_DISK_GB_LOCAL,
    MIN_RAM_GB_LOCAL,
    assess_host,
    discovery_command,
    parse_discovery_output,
)


# --- Sample outputs (real-ish snippets, trimmed) --------------------------


_MACOS_SAMPLE = """\
Hardware Overview:
      Model Name: MacBook Pro
      Chip: Apple M2 Pro
      Total Number of Cores: 12
Graphics/Displays:
    Apple M2 Pro:
      Chipset Model: Apple M2 Pro
System Software Overview:
      System Version: macOS 15.1 (24B83)
/dev/disk3s1s1  974696448 12345678 400123456    3%    123 456 1%  /
hw.ncpu: 12
hw.memsize: 34359738368
arm64
DOCKER_OK
"""


_LINUX_SAMPLE = """\
Ubuntu 24.04.1 LTS
x86_64
16
MemTotal:       32851420 kB
    400G
00:02.0 VGA compatible controller: Intel Corporation Iris Xe
DOCKER_OK
"""


_WINDOWS_SAMPLE = """\
OS Name:                   Microsoft Windows 11 Pro
OS Version:                10.0.22631 N/A Build 22631
System Type:               x64-based PC
Total Physical Memory:     32,768 MB
16
   536870912000
NVIDIA GeForce RTX 4070
DOCKER_MISSING
"""


_LOW_END_LINUX = """\
Ubuntu 22.04
x86_64
2
MemTotal:        8000000 kB
    30G
NO_GPU
DOCKER_MISSING
"""


# --- Discovery command ----------------------------------------------------


@pytest.mark.parametrize("os", ["macos", "linux", "windows"])
def test_discovery_command_is_nonempty_per_os(os):
    cmd = discovery_command(os)
    assert cmd and "docker" in cmd.lower()
    assert DISCOVERY_INSTRUCTIONS[os]


def test_discovery_command_unknown_os_returns_placeholder():
    assert "Unsupported" in discovery_command("unknown")


# --- Parsers --------------------------------------------------------------


def test_parse_macos_extracts_all_fields():
    caps = parse_discovery_output("macos", _MACOS_SAMPLE)
    assert caps.os == "macos"
    assert caps.ram_gb == 32.0
    assert caps.cpu_cores == 12
    assert caps.arch == "arm64"
    assert caps.os_version and "macOS 15.1" in caps.os_version
    assert caps.has_gpu is True
    assert caps.gpu_model == "Apple M2 Pro"
    assert caps.docker_available is True
    assert caps.free_disk_gb and caps.free_disk_gb > 100


def test_parse_linux_extracts_all_fields():
    caps = parse_discovery_output("linux", _LINUX_SAMPLE)
    assert caps.os == "linux"
    assert caps.ram_gb == 31.3
    assert caps.cpu_cores == 16
    assert caps.arch == "x86_64"
    assert caps.free_disk_gb == 400.0
    assert caps.has_gpu is True
    assert caps.docker_available is True


def test_parse_windows_extracts_all_fields():
    caps = parse_discovery_output("windows", _WINDOWS_SAMPLE)
    assert caps.os == "windows"
    assert caps.ram_gb == 32.0
    assert caps.cpu_cores == 16
    assert caps.arch == "x86_64"
    assert caps.has_gpu is True
    assert caps.gpu_model and "RTX 4070" in caps.gpu_model
    assert caps.docker_available is False
    assert caps.free_disk_gb and caps.free_disk_gb > 400


def test_parse_empty_output_returns_defaults():
    caps = parse_discovery_output("linux", "")
    assert caps.os == "linux"
    assert caps.ram_gb is None
    assert caps.cpu_cores is None


def test_parse_unknown_os_stashes_raw_only():
    caps = parse_discovery_output("unknown", "whatever")
    assert caps.os == "unknown"
    assert caps.raw_output == "whatever"


# --- Assessment -----------------------------------------------------------


def test_assess_healthy_mac_supports_local():
    caps = parse_discovery_output("macos", _MACOS_SAMPLE)
    verdict = assess_host(caps)
    assert verdict.local_supported is True
    assert verdict.recommended_mode == "local"
    assert not verdict.reasons


def test_assess_low_ram_blocks_local():
    caps = parse_discovery_output("linux", _LOW_END_LINUX)
    verdict = assess_host(caps)
    assert verdict.local_supported is False
    assert verdict.recommended_mode == "cloud"
    assert any(str(MIN_RAM_GB_LOCAL) in r for r in verdict.reasons)
    assert any(str(MIN_DISK_GB_LOCAL) in r for r in verdict.reasons)


def test_assess_windows_without_docker_warns_but_may_still_be_local():
    caps = parse_discovery_output("windows", _WINDOWS_SAMPLE)
    verdict = assess_host(caps)
    # 32 GB RAM, 16 cores, ~500 GB free \u2014 host is fine, docker warning only.
    assert verdict.local_supported is True
    assert any("Docker Desktop" in w for w in verdict.warnings)


def test_assess_unknown_os_forces_cloud():
    verdict = assess_host(HostCapabilities(os="unknown"))
    assert verdict.local_supported is False
    assert verdict.recommended_mode == "cloud"


# --- Wizard integration ---------------------------------------------------


@pytest.fixture
def client():
    return TestClient(app)


def test_wizard_discovery_prompt_endpoint(client):
    r = client.get("/wizard/host/discovery-prompt", params={"os": "linux"})
    assert r.status_code == 200
    body = r.json()
    assert body["os"] == "linux"
    assert "MemTotal" in body["command"]
    assert body["instructions"]


def test_wizard_host_assess_endpoint(client):
    r = client.post(
        "/wizard/host/assess",
        json={"os": "linux", "raw_output": _LINUX_SAMPLE},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["capabilities"]["ram_gb"] == 31.3
    assert body["assessment"]["local_supported"] is True


def test_wizard_host_assess_low_end_flags_cloud(client):
    r = client.post(
        "/wizard/host/assess",
        json={"os": "linux", "raw_output": _LOW_END_LINUX},
    )
    body = r.json()
    assert body["assessment"]["local_supported"] is False
    assert body["assessment"]["recommended_mode"] == "cloud"


def test_yaml_host_block_and_warning_when_local_but_underprovisioned():
    from app.models.stack import StackConfig, StackPreferences, recommend_stack
    from app.models.wizard import WizardSubmission
    from app.services.wizard_yaml import compute_warnings, render_instance_yaml

    caps = parse_discovery_output("linux", _LOW_END_LINUX)
    prefs = StackPreferences(monthly_budget_eur=30, deployment_mode="local")
    sel = recommend_stack(prefs)
    stack = StackConfig(preferences=prefs, selection=sel, host=caps)

    sub = WizardSubmission(
        instance_name="nexus-underprovisioned",
        persona={"display_name": "Test", "kind": "personal"},
        deployment={"modality": "local"},
        llms={
            "enabled_providers": ["anthropic"],
            "roles": {
                "planner": "anthropic:claude-3-5-sonnet",
                "coordinator": "anthropic:claude-3-5-sonnet",
                "worker": "anthropic:claude-3-5-haiku",
                "embeddings": "openai:text-embedding-3-small",
            },
            "monthly_budget_usd": 50,
        },
        memory={"driver": "postgres_pgvector"},
        areas={"enabled": ["personal_organization"]},
        governance={},
        stack=stack,
    )

    yaml_text = render_instance_yaml(sub)
    assert "host:" in yaml_text
    assert "os: linux" in yaml_text
    assert "local_supported: false" in yaml_text
    assert "local_blockers:" in yaml_text

    warnings = compute_warnings(sub)
    assert any("Host does not meet" in w for w in warnings)


def test_yaml_omits_host_block_when_not_provided():
    from app.models.stack import StackConfig, StackPreferences, recommend_stack
    from app.models.wizard import WizardSubmission
    from app.services.wizard_yaml import render_instance_yaml

    prefs = StackPreferences(monthly_budget_eur=100, deployment_mode="cloud")
    stack = StackConfig(preferences=prefs, selection=recommend_stack(prefs))
    sub = WizardSubmission(
        instance_name="no-host",
        persona={"display_name": "Test", "kind": "personal"},
        deployment={"modality": "fly"},
        llms={
            "enabled_providers": ["anthropic"],
            "roles": {
                "planner": "anthropic:claude-3-5-sonnet",
                "coordinator": "anthropic:claude-3-5-sonnet",
                "worker": "anthropic:claude-3-5-haiku",
                "embeddings": "openai:text-embedding-3-small",
            },
            "monthly_budget_usd": 50,
        },
        memory={"driver": "postgres_pgvector"},
        areas={"enabled": ["personal_organization"]},
        governance={},
        stack=stack,
    )
    yaml_text = render_instance_yaml(sub)
    # No host paste \u2014 the block must be absent entirely.
    assert "\n      os: " not in yaml_text
    assert "local_supported:" not in yaml_text
