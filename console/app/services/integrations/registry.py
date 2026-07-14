"""Static catalogue of integration adapters.

Each :class:`Adapter` is honest data: it declares *how* to connect (a
:class:`ProbeKind`), *what* the operator must supply (``fields`` + ``secrets``,
where secrets are referenced by environment-variable name and never stored as
plaintext), *what capability* it provides, and any real limitation (``notes``).

Design rules:

* Local open-model families (Phi, Gemma, Llama, Qwen) are represented through a
  real OpenAI-compatible *runtime* endpoint (Ollama by default) — never as a
  fabricated direct cloud API.
* Frameworks are HTTP/MCP bridge sidecars, not LLM providers.
* Nothing here makes a network call. Adapters are inert descriptors; probing
  lives in :mod:`app.services.integrations.probes`.
* An adapter existing is what lets the ecosystem registry mark a provider
  ``configurable`` (a real config + health path exists) — it is never enough to
  claim ``available`` (that requires an enabled, tested runtime path).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ProbeKind(str, Enum):
    """How a profile's reachability is verified."""

    openai_compat = "openai_compat"  # GET {base}{probe_path} + Bearer api_key
    header_key = "header_key"  # GET {base}{probe_path} + custom auth header
    query_key = "query_key"  # GET {base}{probe_path}?{query_param}=<key>
    basic_auth = "basic_auth"  # GET {base}{probe_path} + HTTP basic auth
    http_health = "http_health"  # GET {base}{probe_path}, optional Bearer
    postgres = "postgres"  # connect DSN + SELECT 1
    key_present = "key_present"  # secret env var set? (no network probe)
    no_probe = "no_probe"  # config-only; documented reason in notes


class FieldSpec(BaseModel):
    """A non-secret configuration field an operator may set on a profile."""

    key: str
    label: str
    default: str | None = None
    required: bool = False
    placeholder: str | None = None


class SecretSpec(BaseModel):
    """A secret referenced by environment-variable name — never a value.

    ``env`` is the default env var the value is read from at probe/resolve time.
    A profile may override the env name, but the value itself is never persisted
    or returned by the API.
    """

    key: str
    label: str
    env: str
    required: bool = True


class Adapter(BaseModel):
    id: str
    name: str
    category: str
    provider: str
    capabilities: list[str]
    probe: ProbeKind
    # ``external`` (a sidecar / hosted service Nexus talks to) or ``native``.
    integration: str = "external"
    base_url_default: str | None = None
    probe_path: str = "/health"
    # header_key only: the header name + optional scheme prefix ("Bearer").
    auth_header: str | None = None
    auth_scheme: str | None = None
    # query_key only.
    query_param: str | None = None
    fields: list[FieldSpec] = Field(default_factory=list)
    secrets: list[SecretSpec] = Field(default_factory=list)
    docs_url: str | None = None
    template_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Honest limitation, e.g. "no unauthenticated probe; verifies creds only".
    notes: str | None = None


# ---------------------------------------------------------------------------
# Builders — keep the catalogue compact and consistent.
# ---------------------------------------------------------------------------

def _bearer_secret(env: str, label: str = "API key", required: bool = True) -> SecretSpec:
    return SecretSpec(key="api_key", label=label, env=env, required=required)


def _base_url_field(default: str, required: bool = False) -> FieldSpec:
    return FieldSpec(
        key="base_url",
        label="Base URL",
        default=default,
        required=required,
        placeholder=default,
    )


def _openai_compat(
    *, id: str, name: str, category: str, provider: str, base: str,
    env: str | None, docs: str, template_id: str, capabilities: list[str],
    tags: list[str], require_key: bool = True,
) -> Adapter:
    secrets = [_bearer_secret(env, required=require_key)] if env else []
    return Adapter(
        id=id, name=name, category=category, provider=provider,
        capabilities=capabilities, probe=ProbeKind.openai_compat,
        base_url_default=base, probe_path="/models",
        fields=[_base_url_field(base)], secrets=secrets,
        docs_url=docs, template_id=template_id, tags=tags,
    )


def _http_sidecar(
    *, id: str, name: str, category: str, provider: str, base: str,
    docs: str, template_id: str, capabilities: list[str], tags: list[str],
    health_path: str = "/health", env: str | None = None, notes: str | None = None,
) -> Adapter:
    secrets = [_bearer_secret(env, required=False)] if env else []
    return Adapter(
        id=id, name=name, category=category, provider=provider,
        capabilities=capabilities, probe=ProbeKind.http_health,
        base_url_default=base, probe_path=health_path,
        fields=[_base_url_field(base, required=True)], secrets=secrets,
        docs_url=docs, template_id=template_id, tags=tags, notes=notes,
    )


def _build() -> list[Adapter]:
    a: list[Adapter] = []

    # -- LLMs -------------------------------------------------------------
    a += [
        _openai_compat(
            id="llm_openai", name="OpenAI", category="llm", provider="openai",
            base="https://api.openai.com/v1", env="OPENAI_API_KEY",
            docs="https://platform.openai.com/docs/api-reference",
            template_id="llm_provider", capabilities=["chat", "completion"],
            tags=["llm", "openai", "openai-compatible"],
        ),
        Adapter(
            id="llm_anthropic", name="Anthropic Claude", category="llm",
            provider="anthropic", capabilities=["chat"], probe=ProbeKind.header_key,
            base_url_default="https://api.anthropic.com", probe_path="/v1/models",
            auth_header="x-api-key", auth_scheme=None,
            fields=[
                _base_url_field("https://api.anthropic.com"),
                FieldSpec(key="anthropic_version", label="API version", default="2023-06-01"),
            ],
            secrets=[_bearer_secret("ANTHROPIC_API_KEY")],
            docs_url="https://docs.anthropic.com/en/api", template_id="llm_provider",
            tags=["llm", "claude", "anthropic"],
        ),
        Adapter(
            id="llm_gemini", name="Google Gemini", category="llm", provider="google",
            capabilities=["chat"], probe=ProbeKind.query_key,
            base_url_default="https://generativelanguage.googleapis.com",
            probe_path="/v1beta/models", query_param="key",
            fields=[_base_url_field("https://generativelanguage.googleapis.com")],
            secrets=[_bearer_secret("GEMINI_API_KEY")],
            docs_url="https://ai.google.dev/api", template_id="llm_provider",
            tags=["llm", "gemini", "google"],
        ),
        _openai_compat(
            id="llm_mistral", name="Mistral", category="llm", provider="mistral",
            base="https://api.mistral.ai/v1", env="MISTRAL_API_KEY",
            docs="https://docs.mistral.ai/api/", template_id="llm_provider",
            capabilities=["chat", "completion"], tags=["llm", "mistral", "openai-compatible"],
        ),
        _openai_compat(
            id="llm_deepseek", name="DeepSeek", category="llm", provider="deepseek",
            base="https://api.deepseek.com/v1", env="DEEPSEEK_API_KEY",
            docs="https://api-docs.deepseek.com/", template_id="llm_provider",
            capabilities=["chat", "completion"], tags=["llm", "deepseek", "openai-compatible"],
        ),
        _openai_compat(
            id="llm_groq", name="Groq", category="llm", provider="groq",
            base="https://api.groq.com/openai/v1", env="GROQ_API_KEY",
            docs="https://console.groq.com/docs", template_id="llm_provider",
            capabilities=["chat", "completion"], tags=["llm", "groq", "openai-compatible"],
        ),
        _openai_compat(
            id="llm_together", name="Together AI", category="llm", provider="together",
            base="https://api.together.xyz/v1", env="TOGETHER_API_KEY",
            docs="https://docs.together.ai/docs/openai-api-compatibility",
            template_id="llm_provider", capabilities=["chat", "completion"],
            tags=["llm", "together", "openai-compatible"],
        ),
        Adapter(
            id="llm_cohere", name="Cohere", category="llm", provider="cohere",
            capabilities=["chat"], probe=ProbeKind.header_key,
            base_url_default="https://api.cohere.com", probe_path="/v1/models",
            auth_header="Authorization", auth_scheme="Bearer",
            fields=[_base_url_field("https://api.cohere.com")],
            secrets=[_bearer_secret("COHERE_API_KEY")],
            docs_url="https://docs.cohere.com/reference/about", template_id="llm_provider",
            tags=["llm", "cohere"],
        ),
        Adapter(
            id="llm_bedrock", name="Amazon Bedrock", category="llm", provider="bedrock",
            capabilities=["chat"], probe=ProbeKind.no_probe,
            fields=[FieldSpec(key="region", label="AWS region", default="us-east-1", required=True)],
            secrets=[
                SecretSpec(key="access_key_id", label="AWS access key id", env="AWS_ACCESS_KEY_ID"),
                SecretSpec(key="secret_access_key", label="AWS secret access key", env="AWS_SECRET_ACCESS_KEY"),
            ],
            docs_url="https://docs.aws.amazon.com/bedrock/", template_id="llm_provider",
            tags=["llm", "bedrock", "aws"],
            notes="Bedrock uses AWS SigV4; there is no unauthenticated probe. Nexus verifies that credentials + region are present but cannot exercise the API without the AWS SDK on the runtime.",
        ),
        _openai_compat(
            id="llm_ollama", name="Ollama (local)", category="llm", provider="ollama",
            base="http://localhost:11434/v1", env=None,
            docs="https://github.com/ollama/ollama/blob/main/docs/openai.md",
            template_id="llm_provider", capabilities=["chat", "completion"],
            tags=["llm", "ollama", "local", "openai-compatible"], require_key=False,
        ),
    ]

    # -- Open LLMs access (local families via runtime + HF gateway) -------
    for pid, label, hint in [
        ("phi4", "Phi-4", "phi4"),
        ("gemma3", "Gemma 3", "gemma3"),
        ("llama4", "Llama 4", "llama4"),
        ("qwen3", "Qwen 3", "qwen3"),
    ]:
        a.append(
            Adapter(
                id=f"open_{pid}", name=label, category="open_model_access",
                provider="ollama", capabilities=["chat", "completion"],
                probe=ProbeKind.openai_compat,
                base_url_default="http://localhost:11434/v1", probe_path="/models",
                fields=[
                    _base_url_field("http://localhost:11434/v1", required=True),
                    FieldSpec(key="model", label="Model tag", default=hint, placeholder=hint),
                ],
                secrets=[],
                docs_url="https://ollama.com/library",
                template_id="open_model_gateway", tags=["open-models", "local", pid],
                notes=f"{label} is an open-weights family served through a local OpenAI-compatible runtime (Ollama by default), not a direct cloud API. Point base_url at any OpenAI-compatible server hosting the weights.",
            )
        )
    a.append(
        Adapter(
            id="open_huggingface", name="Hugging Face", category="open_model_access",
            provider="huggingface", capabilities=["chat", "completion", "embeddings"],
            probe=ProbeKind.header_key, base_url_default="https://huggingface.co",
            probe_path="/api/whoami-v2", auth_header="Authorization", auth_scheme="Bearer",
            fields=[_base_url_field("https://huggingface.co")],
            secrets=[_bearer_secret("HF_TOKEN")],
            docs_url="https://huggingface.co/docs/api-inference", template_id="open_model_gateway",
            tags=["open-models", "huggingface"],
        )
    )

    # -- Embeddings -------------------------------------------------------
    a.append(
        _openai_compat(
            id="embed_openai", name="OpenAI Embeddings", category="embeddings",
            provider="openai", base="https://api.openai.com/v1", env="OPENAI_API_KEY",
            docs="https://platform.openai.com/docs/guides/embeddings",
            template_id="embeddings_provider", capabilities=["embeddings"],
            tags=["embeddings", "openai"],
        )
    )
    a.append(
        Adapter(
            id="embed_voyage", name="Voyage AI", category="embeddings", provider="voyage",
            capabilities=["embeddings"], probe=ProbeKind.key_present,
            secrets=[_bearer_secret("VOYAGE_API_KEY")],
            docs_url="https://docs.voyageai.com/", template_id="embeddings_provider",
            tags=["embeddings", "voyage"],
            notes="Voyage exposes only a POST /embeddings endpoint (billed per call); Nexus verifies the API key is present rather than making a paid probe request.",
        )
    )
    a.append(
        Adapter(
            id="embed_google", name="Google (Gecko / EmbeddingGemma)", category="embeddings",
            provider="google", capabilities=["embeddings"], probe=ProbeKind.query_key,
            base_url_default="https://generativelanguage.googleapis.com",
            probe_path="/v1beta/models", query_param="key",
            fields=[_base_url_field("https://generativelanguage.googleapis.com")],
            secrets=[_bearer_secret("GEMINI_API_KEY")],
            docs_url="https://ai.google.dev/gemini-api/docs/embeddings",
            template_id="embeddings_provider", tags=["embeddings", "google"],
        )
    )
    a.append(
        Adapter(
            id="embed_cohere", name="Cohere Embed", category="embeddings", provider="cohere",
            capabilities=["embeddings"], probe=ProbeKind.header_key,
            base_url_default="https://api.cohere.com", probe_path="/v1/models",
            auth_header="Authorization", auth_scheme="Bearer",
            fields=[_base_url_field("https://api.cohere.com")],
            secrets=[_bearer_secret("COHERE_API_KEY")],
            docs_url="https://docs.cohere.com/reference/embed", template_id="embeddings_provider",
            tags=["embeddings", "cohere"],
        )
    )
    a.append(
        _http_sidecar(
            id="embed_nomic", name="Nomic (local embed server)", category="embeddings",
            provider="nomic", base="http://localhost:8080", docs="https://docs.nomic.ai/",
            template_id="embeddings_provider", capabilities=["embeddings"],
            tags=["embeddings", "nomic", "local"], health_path="/health",
            notes="Run nomic-embed via a local text-embeddings server; Nexus talks to that endpoint rather than bundling the model weights.",
        )
    )
    a.append(
        _http_sidecar(
            id="embed_sbert", name="SentenceTransformers / SBERT", category="embeddings",
            provider="sbert", base="http://localhost:8080",
            docs="https://huggingface.co/docs/text-embeddings-inference/index",
            template_id="embeddings_provider", capabilities=["embeddings"],
            tags=["embeddings", "sbert", "local"], health_path="/health",
            notes="Serve SBERT models via a local Text-Embeddings-Inference (or equivalent) server; Nexus never bundles the multi-GB models.",
        )
    )

    # -- Vector databases -------------------------------------------------
    a.append(
        _http_sidecar(
            id="vdb_chroma", name="Chroma", category="vector_db", provider="chroma",
            base="http://localhost:8000", docs="https://docs.trychroma.com/",
            template_id="vector_store", capabilities=["vector_search"],
            tags=["vector-db", "chroma"], health_path="/api/v1/heartbeat",
        )
    )
    a.append(
        Adapter(
            id="vdb_qdrant", name="Qdrant", category="vector_db", provider="qdrant",
            capabilities=["vector_search"], probe=ProbeKind.header_key,
            base_url_default="http://localhost:6333", probe_path="/healthz",
            auth_header="api-key", auth_scheme=None,
            fields=[_base_url_field("http://localhost:6333", required=True)],
            secrets=[_bearer_secret("QDRANT_API_KEY", required=False)],
            docs_url="https://qdrant.tech/documentation/", template_id="vector_store",
            tags=["vector-db", "qdrant"],
        )
    )
    a.append(
        Adapter(
            id="vdb_pinecone", name="Pinecone", category="vector_db", provider="pinecone",
            capabilities=["vector_search"], probe=ProbeKind.header_key,
            base_url_default="https://api.pinecone.io", probe_path="/indexes",
            auth_header="Api-Key", auth_scheme=None,
            fields=[_base_url_field("https://api.pinecone.io")],
            secrets=[_bearer_secret("PINECONE_API_KEY")],
            docs_url="https://docs.pinecone.io/reference/api", template_id="vector_store",
            tags=["vector-db", "pinecone"],
        )
    )
    a.append(
        _http_sidecar(
            id="vdb_weaviate", name="Weaviate", category="vector_db", provider="weaviate",
            base="http://localhost:8080", docs="https://weaviate.io/developers/weaviate",
            template_id="vector_store", capabilities=["vector_search"],
            tags=["vector-db", "weaviate"], health_path="/v1/.well-known/ready",
            env="WEAVIATE_API_KEY",
        )
    )
    a.append(
        _http_sidecar(
            id="vdb_milvus", name="Milvus", category="vector_db", provider="milvus",
            base="http://localhost:9091", docs="https://milvus.io/docs",
            template_id="vector_store", capabilities=["vector_search"],
            tags=["vector-db", "milvus"], health_path="/healthz",
            notes="Milvus data plane is gRPC; the HTTP probe hits the health port (9091 by default).",
        )
    )
    a.append(
        Adapter(
            id="vdb_pgvector", name="PostgreSQL / pgvector", category="vector_db",
            provider="pgvector", capabilities=["vector_search"], probe=ProbeKind.postgres,
            fields=[],
            secrets=[SecretSpec(key="dsn", label="Connection DSN", env="PGVECTOR_DSN")],
            docs_url="https://github.com/pgvector/pgvector", template_id="vector_store",
            tags=["vector-db", "pgvector", "postgres"],
            notes="Probe opens the DSN and runs SELECT 1. The pgvector extension must be installed in the target database.",
        )
    )
    a.append(
        Adapter(
            id="vdb_cassandra", name="Cassandra (vector)", category="vector_db",
            provider="cassandra", capabilities=["vector_search"], probe=ProbeKind.no_probe,
            fields=[
                FieldSpec(key="contact_points", label="Contact points", placeholder="host1,host2", required=True),
                FieldSpec(key="keyspace", label="Keyspace", placeholder="nexus"),
            ],
            secrets=[
                SecretSpec(key="username", label="Username", env="CASSANDRA_USERNAME", required=False),
                SecretSpec(key="password", label="Password", env="CASSANDRA_PASSWORD", required=False),
            ],
            docs_url="https://cassandra.apache.org/doc/latest/", template_id="vector_store",
            tags=["vector-db", "cassandra"],
            notes="Cassandra uses the binary CQL protocol; there is no HTTP health probe. Config is validated but connectivity is verified by the driver on the runtime.",
        )
    )
    a.append(
        Adapter(
            id="vdb_opensearch", name="OpenSearch", category="vector_db", provider="opensearch",
            capabilities=["vector_search"], probe=ProbeKind.basic_auth,
            base_url_default="https://localhost:9200", probe_path="/_cluster/health",
            fields=[_base_url_field("https://localhost:9200", required=True)],
            secrets=[
                SecretSpec(key="username", label="Username", env="OPENSEARCH_USERNAME", required=False),
                SecretSpec(key="password", label="Password", env="OPENSEARCH_PASSWORD", required=False),
            ],
            docs_url="https://opensearch.org/docs/latest/", template_id="vector_store",
            tags=["vector-db", "opensearch"],
        )
    )

    # -- Frameworks (HTTP/MCP bridge sidecars) ----------------------------
    for pid, label, base, docs in [
        ("langchain", "LangChain (LangServe)", "http://localhost:8100", "https://python.langchain.com/docs/langserve"),
        ("llamaindex", "LlamaIndex", "http://localhost:8101", "https://docs.llamaindex.ai/"),
        ("haystack", "Haystack (Hayhooks)", "http://localhost:1416", "https://docs.haystack.deepset.ai/"),
        ("txtai", "txtai", "http://localhost:8102", "https://neuml.github.io/txtai/"),
    ]:
        a.append(
            _http_sidecar(
                id=f"fw_{pid}", name=label, category="framework", provider=pid,
                base=base, docs=docs, template_id="framework_bridge",
                capabilities=["framework_bridge"], tags=["framework", "orchestration", pid],
                notes="Runs as an external agent/framework service; Nexus calls it over HTTP (or its MCP endpoint), it is not embedded in the Console.",
            )
        )

    # -- Data extraction --------------------------------------------------
    a.append(
        _http_sidecar(
            id="extract_crawl4ai", name="Crawl4AI", category="data_extraction",
            provider="crawl4ai", base="http://localhost:11235",
            docs="https://docs.crawl4ai.com/", template_id="web_extraction",
            capabilities=["web_extraction"], tags=["extraction", "scraping", "crawl4ai"],
            health_path="/health",
        )
    )
    a.append(
        _http_sidecar(
            id="extract_firecrawl", name="FireCrawl", category="data_extraction",
            provider="firecrawl", base="https://api.firecrawl.dev",
            docs="https://docs.firecrawl.dev/", template_id="web_extraction",
            capabilities=["web_extraction"], tags=["extraction", "scraping", "firecrawl"],
            health_path="/v1/health", env="FIRECRAWL_API_KEY",
            notes="Works against the hosted API (with FIRECRAWL_API_KEY) or a self-hosted instance; point base_url accordingly.",
        )
    )
    a.append(
        _http_sidecar(
            id="extract_scrapegraphai", name="ScrapeGraphAI", category="data_extraction",
            provider="scrapegraphai", base="http://localhost:8103",
            docs="https://scrapegraphai.com/", template_id="web_extraction",
            capabilities=["web_extraction"], tags=["extraction", "scraping", "scrapegraphai"],
        )
    )
    a.append(
        _http_sidecar(
            id="extract_megaparser", name="MegaParser", category="data_extraction",
            provider="megaparser", base="http://localhost:8104",
            docs="https://github.com/QuivrHQ/MegaParse", template_id="web_extraction",
            capabilities=["document_extraction"], tags=["extraction", "parsing", "megaparser"],
        )
    )
    a.append(
        _http_sidecar(
            id="extract_docling", name="Docling", category="data_extraction",
            provider="docling", base="http://localhost:5001",
            docs="https://ds4sd.github.io/docling/", template_id="web_extraction",
            capabilities=["document_extraction"], tags=["extraction", "parsing", "docling"],
            health_path="/health",
        )
    )
    a.append(
        Adapter(
            id="extract_llamaparse", name="LlamaParse", category="data_extraction",
            provider="llamaparse", capabilities=["document_extraction"],
            probe=ProbeKind.key_present,
            secrets=[_bearer_secret("LLAMA_CLOUD_API_KEY")],
            docs_url="https://docs.cloud.llamaindex.ai/llamaparse/getting_started",
            template_id="web_extraction", tags=["extraction", "parsing", "llamaparse"],
            notes="LlamaParse is a hosted upload/poll API with no public health endpoint; Nexus verifies the API key is present.",
        )
    )
    a.append(
        _http_sidecar(
            id="extract_extractthinker", name="ExtractThinker", category="data_extraction",
            provider="extractthinker", base="http://localhost:8105",
            docs="https://enoch3712.github.io/ExtractThinker/", template_id="web_extraction",
            capabilities=["document_extraction"], tags=["extraction", "parsing", "extractthinker"],
        )
    )

    # -- Evaluation -------------------------------------------------------
    a.append(
        _http_sidecar(
            id="eval_giskard", name="Giskard", category="evaluation", provider="giskard",
            base="http://localhost:9080", docs="https://docs.giskard.ai/",
            template_id="model_evaluation", capabilities=["evaluation"],
            tags=["evaluation", "quality", "giskard"], health_path="/health",
        )
    )
    a.append(
        _http_sidecar(
            id="eval_ragas", name="Ragas", category="evaluation", provider="ragas",
            base="http://localhost:8106", docs="https://docs.ragas.io/",
            template_id="model_evaluation", capabilities=["evaluation"],
            tags=["evaluation", "quality", "ragas"],
            notes="Ragas is a Python eval library; expose it behind a small HTTP eval service and point base_url at that sidecar.",
        )
    )
    a.append(
        _http_sidecar(
            id="eval_deepeval", name="DeepEval", category="evaluation", provider="deepeval",
            base="http://localhost:8107", docs="https://docs.confident-ai.com/",
            template_id="model_evaluation", capabilities=["evaluation"],
            tags=["evaluation", "quality", "deepeval"],
            notes="DeepEval is a Python eval library; expose it behind a small HTTP eval service and point base_url at that sidecar.",
        )
    )

    return a


ADAPTERS: list[Adapter] = _build()

_BY_ID: dict[str, Adapter] = {ad.id: ad for ad in ADAPTERS}


def adapter_by_id(adapter_id: str) -> Adapter | None:
    return _BY_ID.get(adapter_id)


def adapters_by_category(category: str) -> list[Adapter]:
    return [ad for ad in ADAPTERS if ad.category == category]
