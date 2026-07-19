"""Validation for the managed-platform (v1alpha1) contract schemas and docs.

These contracts are TARGET-STATE design artifacts (no Hub/Operator/Registry
code exists yet). This test guards three things so the docs cannot silently
rot:

1. Every schema in docs/schemas/v1alpha1 is itself a valid JSON Schema 2020-12.
2. Every example fixture validates against the schema declared in
   docs/schemas/examples/index.json.
3. No example fixture leaks a plaintext secret value.
4. Every relative Markdown link under docs/ resolves to a file that exists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "docs" / "schemas" / "v1alpha1"
EXAMPLE_DIR = REPO_ROOT / "docs" / "schemas" / "examples"
DOCS_DIR = REPO_ROOT / "docs"


def _load_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def _registry() -> Registry:
    registry = Registry()
    for schema_path in SCHEMA_DIR.glob("*.json"):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            schema["$id"], Resource.from_contents(schema)
        )
    return registry


SCHEMA_FILES = sorted(SCHEMA_DIR.glob("*.json"))
CASES = _load_doc(EXAMPLE_DIR / "index.json")["cases"]

# Keys that must never appear carrying a plaintext secret value in a fixture.
_FORBIDDEN_SECRET_KEYS = {"value", "secret", "plaintext", "ciphertext", "api_key", "password", "token"}
# Signature/credential reference fields legitimately use these names for
# non-secret references; allow them explicitly.
_ALLOWED_VALUE_CONTEXT = {"enrollment_token"}  # single-use, short-lived, not a standing secret


@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_is_valid_2020_12(schema_path: Path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert "$id" in schema, f"{schema_path.name} is missing $id"
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["example"])
def test_example_validates_against_schema(case: dict):
    schema = json.loads((SCHEMA_DIR / case["schema"]).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, registry=_registry())
    document = _load_doc(EXAMPLE_DIR / case["example"])
    errors = sorted(validator.iter_errors(document), key=lambda e: e.path)
    assert not errors, "\n".join(
        f"{list(e.path)}: {e.message}" for e in errors
    )


def test_every_schema_has_an_example():
    referenced = {c["schema"] for c in CASES}
    # common.defs is a shared $defs library; setup.task is exercised transitively
    # through setup.plan (its items $ref setup.task). Neither is instantiated alone.
    indirect = {"common.defs.schema.json", "setup.task.schema.json"}
    expected = {p.name for p in SCHEMA_FILES if p.name not in indirect}
    assert expected <= referenced, f"schemas without an example: {expected - referenced}"


@pytest.mark.parametrize(
    "example_path",
    sorted(list(EXAMPLE_DIR.glob("*.json")) + list(EXAMPLE_DIR.glob("*.yaml"))),
    ids=lambda p: p.name,
)
def test_no_plaintext_secret_values(example_path: Path):
    if example_path.name == "index.json":
        return
    document = _load_doc(example_path)

    def walk(node, key_path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                lowered = str(k).lower()
                if lowered in _FORBIDDEN_SECRET_KEYS and k not in _ALLOWED_VALUE_CONTEXT:
                    # Only signature.value (base64 signature, not a secret) is allowed.
                    assert "signature" in key_path or "hub_public_key" in key_path or "public_key" in key_path, (
                        f"{example_path.name}: suspicious secret-bearing key '{k}' at {key_path}"
                    )
                walk(v, f"{key_path}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{key_path}[{i}]")

    walk(document)


def _validator(schema_name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def _base_desired_state() -> dict:
    return json.loads(
        (EXAMPLE_DIR / "desired-state.example.json").read_text(encoding="utf-8")
    )


def test_age_is_rejected_as_signing_algorithm():
    """age is envelope encryption only; it must never validate as a signature."""
    common = json.loads((SCHEMA_DIR / "common.defs.schema.json").read_text(encoding="utf-8"))
    sig_schema = {"$schema": common["$schema"], **common["$defs"]["Signature"]}
    validator = Draft202012Validator(sig_schema)
    bad = {"algorithm": "age", "key_id": "k", "value": "x", "canonicalization": "jcs"}
    assert list(validator.iter_errors(bad)), "age must not be a valid Signature.algorithm"
    good = {"algorithm": "ed25519", "key_id": "k", "value": "x", "canonicalization": "jcs"}
    assert not list(validator.iter_errors(good))


def test_desired_state_requires_ed25519_and_rejects_sigstore_and_age():
    """The control plane pins ed25519; Sigstore/keyless and age are rejected."""
    validator = _validator("desired-state.schema.json")
    for bad_alg in ("sigstore-cosign", "age", "minisign"):
        doc = _base_desired_state()
        doc["signature"]["algorithm"] = bad_alg
        assert list(validator.iter_errors(doc)), (
            f"desired-state must reject signature algorithm {bad_alg!r}"
        )
    # The unmodified ed25519 example (with trust_domain) must still validate,
    # proving Sigstore/transparency-log availability is NOT required here.
    assert not list(validator.iter_errors(_base_desired_state()))


def test_desired_state_requires_trust_domain():
    validator = _validator("desired-state.schema.json")
    doc = _base_desired_state()
    doc["signature"].pop("trust_domain", None)
    assert list(validator.iter_errors(doc)), "desired-state signature must require trust_domain"


def test_pack_requires_spdx_license():
    validator = _validator("nexus.pack.schema.json")
    pack = yaml.safe_load(
        (EXAMPLE_DIR / "pack.real-estate-agency.yaml").read_text(encoding="utf-8")
    )
    assert not list(validator.iter_errors(pack))
    pack["metadata"].pop("license", None)
    assert list(validator.iter_errors(pack)), "pack must require an SPDX license"


def test_pack_offline_signature_only_minisign_or_ed25519():
    validator = _validator("nexus.pack.schema.json")
    pack = yaml.safe_load(
        (EXAMPLE_DIR / "pack.real-estate-agency.yaml").read_text(encoding="utf-8")
    )
    pack["metadata"]["offline_signature"]["algorithm"] = "sigstore-cosign"
    assert list(validator.iter_errors(pack)), (
        "offline_signature must reject sigstore-cosign (no offline infra dependency)"
    )


def test_secrets_manifest_forbids_ciphertext_and_requires_age_x25519():
    validator = _validator("secrets-bundle-manifest.schema.json")
    manifest = json.loads(
        (EXAMPLE_DIR / "secrets-bundle-manifest.example.json").read_text(encoding="utf-8")
    )
    assert not list(validator.iter_errors(manifest))
    # Any entry carrying ciphertext/plaintext must be rejected by construction.
    leaky = json.loads(json.dumps(manifest))
    leaky["entries"][0]["ciphertext"] = "AAAA"
    assert list(validator.iter_errors(leaky)), "manifest entries must forbid ciphertext"
    # age/X25519 recipient is mandatory; a non-age scheme must be rejected.
    non_age = json.loads(json.dumps(manifest))
    non_age["encryption"]["scheme"] = "jwe"
    assert list(validator.iter_errors(non_age)), "secrets bundle must pin age scheme"


def test_docs_relative_links_resolve():
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for md in DOCS_DIR.rglob("*.md"):
        for match in link_re.finditer(md.read_text(encoding="utf-8")):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{md.relative_to(REPO_ROOT)} -> {target}")
    assert not broken, "Broken relative doc links:\n" + "\n".join(broken)
