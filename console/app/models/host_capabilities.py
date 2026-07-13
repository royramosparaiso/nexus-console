"""Host capability discovery for the wizard.

The operator tells the wizard what machine they have. The wizard uses
that to (a) tell them whether local deployment is realistic and (b)
render OS-specific handoff notes.

The parsers here are tolerant: paste the raw output of the discovery
command and we extract what we can. Missing fields fall back to
``None`` and produce warnings rather than errors.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

OperatingSystem = Literal["macos", "linux", "windows", "unknown"]
Architecture = Literal["x86_64", "arm64", "unknown"]


# Minimum recommended specs for local deployment of the standard stack.
# Below these, we push the operator to cloud and warn.
MIN_RAM_GB_LOCAL = 16
MIN_DISK_GB_LOCAL = 50
MIN_CPU_CORES_LOCAL = 4


class HostCapabilities(BaseModel):
    """What the operator's laptop can actually run."""

    os: OperatingSystem = "unknown"
    os_version: str | None = None
    arch: Architecture = "unknown"
    cpu_cores: int | None = Field(default=None, ge=1, le=1024)
    ram_gb: float | None = Field(default=None, ge=0, le=4096)
    free_disk_gb: float | None = Field(default=None, ge=0, le=1_000_000)
    has_gpu: bool = False
    gpu_model: str | None = None
    docker_available: bool = False
    raw_output: str | None = Field(
        default=None,
        description="Untouched paste from the discovery command. Kept for audit.",
    )

    @field_validator("os_version", "gpu_model", "raw_output")
    @classmethod
    def _trim(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip() or None


class HostAssessment(BaseModel):
    """Verdict on whether local deployment is realistic."""

    local_supported: bool
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommended_mode: Literal["local", "cloud"] = "cloud"


# ---------------------------------------------------------------------------
# Discovery commands \u2014 what the wizard tells the operator to run.
# ---------------------------------------------------------------------------


def discovery_command(os: OperatingSystem) -> str:
    """One command per OS. Output goes into ``HostCapabilities.raw_output``.

    Commands are one-shot, read-only, and produce all fields the parser
    needs in one paste.
    """
    if os == "macos":
        # system_profiler is slow but covers RAM + CPU + GPU + OS in one call.
        # df -k / gives free disk. docker version prints just enough to detect.
        return (
            "{ system_profiler SPHardwareDataType SPDisplaysDataType SPSoftwareDataType; "
            "df -k / | tail -1; "
            "sysctl -n hw.ncpu hw.memsize; "
            "uname -m; "
            "docker version --format 'DOCKER_OK' 2>/dev/null || echo 'DOCKER_MISSING'; }"
        )
    if os == "linux":
        return (
            "{ lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME; "
            "uname -m; "
            "nproc; "
            "grep MemTotal /proc/meminfo; "
            "df -BG --output=avail / | tail -1; "
            "lspci 2>/dev/null | grep -iE 'vga|3d|nvidia|amd/ati' || echo 'NO_GPU'; "
            "docker version --format 'DOCKER_OK' 2>/dev/null || echo 'DOCKER_MISSING'; }"
        )
    if os == "windows":
        # PowerShell one-liner. Works in Windows 10 / 11 default shell.
        return (
            "powershell -NoProfile -Command \""
            "systeminfo | Select-String 'OS Name','OS Version','System Type','Total Physical Memory'; "
            "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty NumberOfCores; "
            "Get-PSDrive C | Select-Object -ExpandProperty Free; "
            "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name; "
            "try { docker version --format 'DOCKER_OK' } catch { 'DOCKER_MISSING' }\""
        )
    return "# Unsupported OS \u2014 fill in HostCapabilities fields manually."


DISCOVERY_INSTRUCTIONS: dict[OperatingSystem, str] = {
    "macos": (
        "Open Terminal (\u2318+Space, type 'Terminal'). Paste the command below "
        "and copy every line of the output back into the wizard."
    ),
    "linux": (
        "Open your terminal. Paste the command below and copy every line of "
        "the output back into the wizard."
    ),
    "windows": (
        "Press Win+X and pick 'Terminal' (or 'PowerShell'). Paste the "
        "command below and copy every line of the output back into the "
        "wizard. If PowerShell blocks scripts, run "
        "'Set-ExecutionPolicy -Scope Process Bypass' first."
    ),
    "unknown": (
        "We don't have a discovery command for your OS. Fill in the fields "
        "manually as best you can."
    ),
}


# ---------------------------------------------------------------------------
# Parsers \u2014 tolerant, one per OS.
# ---------------------------------------------------------------------------


_MEM_MACOS_RE = re.compile(r"hw\.memsize\D+(\d+)")
_CPU_MACOS_RE = re.compile(r"hw\.ncpu\D+(\d+)")
_MEM_LINUX_RE = re.compile(r"MemTotal:\s+(\d+)\s*kB", re.IGNORECASE)
_MEM_WINDOWS_RE = re.compile(
    r"Total Physical Memory:\s*([\d,\.]+)\s*(MB|GB)", re.IGNORECASE,
)
_ARCH_RE = re.compile(
    r"\b(x86_64|x64|amd64|arm64|aarch64)(?:[- ]?based)?\b", re.IGNORECASE,
)


def _normalize_arch(raw: str) -> Architecture:
    m = _ARCH_RE.search(raw)
    if not m:
        return "unknown"
    token = m.group(1).lower()
    if token in ("x86_64", "x64", "amd64"):
        return "x86_64"
    if token in ("arm64", "aarch64"):
        return "arm64"
    return "unknown"


def _parse_macos(raw: str) -> HostCapabilities:
    caps = HostCapabilities(os="macos", raw_output=raw)
    if m := _MEM_MACOS_RE.search(raw):
        caps.ram_gb = round(int(m.group(1)) / (1024**3), 1)
    if m := _CPU_MACOS_RE.search(raw):
        caps.cpu_cores = int(m.group(1))
    caps.arch = _normalize_arch(raw)
    # OS version: "System Version: macOS 15.1 (24B83)"
    if m := re.search(r"macOS\s+([\d\.]+)", raw):
        caps.os_version = f"macOS {m.group(1)}"
    # Disk: "/dev/disk3s1s1  974696448 12345678 400123456    3%    ..."
    if m := re.search(r"^/dev/\S+\s+\d+\s+\d+\s+(\d+)", raw, re.MULTILINE):
        caps.free_disk_gb = round(int(m.group(1)) / (1024**2), 1)
    # GPU: any "Chipset Model:" line under Displays.
    if m := re.search(r"Chipset Model:\s*(.+)", raw):
        caps.gpu_model = m.group(1).strip()
        caps.has_gpu = True
    caps.docker_available = "DOCKER_OK" in raw
    return caps


def _parse_linux(raw: str) -> HostCapabilities:
    caps = HostCapabilities(os="linux", raw_output=raw)
    if m := _MEM_LINUX_RE.search(raw):
        caps.ram_gb = round(int(m.group(1)) / (1024**2), 1)
    # nproc output is just a number on its own line.
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.isdigit() and caps.cpu_cores is None:
            caps.cpu_cores = int(stripped)
            break
    caps.arch = _normalize_arch(raw)
    if m := re.search(r"PRETTY_NAME=\"?(.+?)\"?$", raw, re.MULTILINE):
        caps.os_version = m.group(1)
    # df -BG --output=avail: "Avail\n  400G"
    if m := re.search(r"^\s*(\d+)G\s*$", raw, re.MULTILINE):
        caps.free_disk_gb = float(m.group(1))
    # GPU: any lspci line that mentions NVIDIA / AMD / VGA and is not NO_GPU.
    gpu_line = re.search(
        r"^.*(?:VGA|3D controller|NVIDIA|AMD/ATI).*$", raw, re.MULTILINE
    )
    if gpu_line and "NO_GPU" not in gpu_line.group(0):
        caps.has_gpu = True
        # Extract the model after the colon.
        parts = gpu_line.group(0).split(":", 2)
        caps.gpu_model = parts[-1].strip() if parts else gpu_line.group(0)
    caps.docker_available = "DOCKER_OK" in raw
    return caps


def _parse_windows(raw: str) -> HostCapabilities:
    caps = HostCapabilities(os="windows", raw_output=raw)
    if m := _MEM_WINDOWS_RE.search(raw):
        value = float(m.group(1).replace(",", "").replace(".", ""))
        unit = m.group(2).upper()
        if unit == "MB":
            caps.ram_gb = round(value / 1024, 1)
        else:
            caps.ram_gb = round(value, 1)
    # System Type: "x64-based PC" or "ARM64-based PC"
    caps.arch = _normalize_arch(raw)
    if m := re.search(r"OS Name:\s*(.+)", raw):
        caps.os_version = m.group(1).strip()
    # Cores: bare number on its own line (Get-CimInstance ...NumberOfCores).
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.isdigit() and 1 <= int(stripped) <= 512 and caps.cpu_cores is None:
            caps.cpu_cores = int(stripped)
            break
    # Free bytes on C:. Get-PSDrive .Free prints bytes as a big integer.
    if m := re.search(r"^\s*(\d{9,})\s*$", raw, re.MULTILINE):
        caps.free_disk_gb = round(int(m.group(1)) / (1024**3), 1)
    # GPU: any line with common GPU vendor tokens.
    if m := re.search(
        r"^.*(NVIDIA|AMD|Intel.*Graphics|Radeon|GeForce|RTX|Quadro).*$",
        raw, re.MULTILINE,
    ):
        caps.has_gpu = True
        caps.gpu_model = m.group(0).strip()
    caps.docker_available = "DOCKER_OK" in raw
    return caps


def parse_discovery_output(os: OperatingSystem, raw: str) -> HostCapabilities:
    """Parse the paste from ``discovery_command`` into ``HostCapabilities``.

    Never raises \u2014 unrecognised fields stay as ``None``. The wizard
    surfaces missing fields as warnings so the operator can fill them
    in by hand.
    """
    if not raw or not raw.strip():
        return HostCapabilities(os=os)
    if os == "macos":
        return _parse_macos(raw)
    if os == "linux":
        return _parse_linux(raw)
    if os == "windows":
        return _parse_windows(raw)
    return HostCapabilities(os="unknown", raw_output=raw)


# ---------------------------------------------------------------------------
# Assessment \u2014 does the host meet the local-deployment bar?
# ---------------------------------------------------------------------------


def assess_host(caps: HostCapabilities) -> HostAssessment:
    reasons: list[str] = []
    warnings: list[str] = []

    if caps.os == "unknown":
        warnings.append("Operating system not detected \u2014 defaulting to cloud.")
        return HostAssessment(
            local_supported=False,
            reasons=["OS unknown"],
            warnings=warnings,
            recommended_mode="cloud",
        )

    if caps.ram_gb is None:
        warnings.append("RAM not detected \u2014 assuming insufficient for local.")
    elif caps.ram_gb < MIN_RAM_GB_LOCAL:
        reasons.append(
            f"RAM {caps.ram_gb} GB < {MIN_RAM_GB_LOCAL} GB minimum for local Postgres + Qdrant + LLM proxy."
        )

    if caps.cpu_cores is None:
        warnings.append("CPU core count not detected.")
    elif caps.cpu_cores < MIN_CPU_CORES_LOCAL:
        reasons.append(
            f"CPU {caps.cpu_cores} cores < {MIN_CPU_CORES_LOCAL} cores minimum."
        )

    if caps.free_disk_gb is None:
        warnings.append("Free disk not detected.")
    elif caps.free_disk_gb < MIN_DISK_GB_LOCAL:
        reasons.append(
            f"Free disk {caps.free_disk_gb} GB < {MIN_DISK_GB_LOCAL} GB minimum."
        )

    if caps.os == "windows" and not caps.docker_available:
        warnings.append(
            "Docker Desktop not detected on Windows. Local mode requires "
            "Docker Desktop or WSL2 \u2014 the handoff will add extra setup steps."
        )
    elif not caps.docker_available and caps.os in ("macos", "linux"):
        warnings.append(
            "Docker not detected. Local mode needs Docker or Podman for "
            "Postgres/Qdrant containers."
        )

    if caps.arch == "unknown":
        warnings.append("CPU architecture not detected.")

    local_supported = not reasons
    return HostAssessment(
        local_supported=local_supported,
        reasons=reasons,
        warnings=warnings,
        recommended_mode="local" if local_supported else "cloud",
    )
