// Types must mirror app/models/wizard.py

export type PersonaKind = "personal" | "family" | "company" | "community" | "client" | "custom";
export type Modality = "local" | "fly" | "k8s" | "onprem" | "saas";
export type LlmProvider =
  | "anthropic" | "openai" | "openrouter" | "perplexity"
  | "groq" | "together" | "mistral" | "ollama";
export type MemoryDriver = "sqlite" | "postgres" | "postgres_pgvector";
export type GraphDriver = "none" | "neo4j" | "postgres_graph";
export type AutonomyLevel = "read_only" | "propose" | "act_with_approval" | "act_autonomously";

export type PersonaConfig = {
  display_name: string;
  kind: PersonaKind;
  description: string;
  default_locale: string;
};

export type DeploymentConfig = {
  modality: Modality;
  domain: string | null;
  region: string | null;
  tls: boolean;
  autoscale: boolean;
};

export type LlmRoleAssignment = {
  planner: string;
  coordinator: string;
  worker: string;
  embeddings: string;
};

export type LlmConfig = {
  enabled_providers: LlmProvider[];
  roles: LlmRoleAssignment;
  allow_fallback: boolean;
  monthly_budget_usd: number;
};

export type MemoryConfig = {
  driver: MemoryDriver;
  graph: GraphDriver;
  retention_days: number;
  encryption_at_rest: boolean;
};

export type AreasConfig = {
  enabled: string[];
};

export type GovernanceConfig = {
  default_autonomy: AutonomyLevel;
  kill_switch_enabled: boolean;
  audit_retention_days: number;
  monthly_budget_alert_pct: number;
  require_2fa_for_superadmin: boolean;
};

export type StackRole =
  | "app_compute" | "frontend_hosting" | "postgres" | "graph_db"
  | "vector_db" | "cache_queue" | "gpu_serverless" | "llm_gateway"
  | "object_storage" | "auth" | "dns_cdn" | "error_monitoring"
  | "log_platform" | "product_analytics" | "llm_observability"
  | "email_transactional" | "background_jobs" | "ci_cd";

export type BudgetTier = "free" | "hobby" | "standard" | "scale";
export type DeploymentMode = "local" | "cloud" | "hybrid";

export type StackService = {
  slug: string;
  name: string;
  vendor: string;
  role: StackRole;
  tiers: BudgetTier[];
  price_free_usd: number;
  price_entry_usd: number;
  price_scale_usd: number;
  self_hostable: boolean;
  scale_to_zero: boolean;
  open_source: boolean;
  homepage: string;
  notes: string;
  handoff_playbook: string | null;
};

export type StackPreferences = {
  monthly_budget_eur: number;
  deployment_mode: DeploymentMode;
  team_size: number;
  needs_graph_db: boolean;
  needs_voice_gpu: boolean;
  needs_llm_observability: boolean;
  needs_product_analytics: boolean;
  needs_background_jobs: boolean;
  prefer_open_source: boolean;
  prefer_scale_to_zero: boolean;
  region: string;
};

export type StackSelection = {
  services: Partial<Record<StackRole, string>>;
  estimated_monthly_usd: number;
  tier: BudgetTier;
  rationale: string;
};

export type StackConfig = {
  preferences: StackPreferences;
  selection: StackSelection;
  overrides: Partial<Record<StackRole, string>>;
};

export type WizardSubmission = {
  instance_name: string;
  persona: PersonaConfig;
  deployment: DeploymentConfig;
  llms: LlmConfig;
  memory: MemoryConfig;
  areas: AreasConfig;
  governance: GovernanceConfig;
  stack?: StackConfig | null;
};

export type AvailableArea = {
  slug: string;
  label: string;
  tier: "core" | "vertical";
  default: boolean;
};

export type WizardSchema = {
  steps: { id: string; label: string }[];
  persona_kinds: { value: PersonaKind; label: string }[];
  modalities: { value: Modality; label: string }[];
  llm_providers: LlmProvider[];
  memory_drivers: { value: MemoryDriver; label: string }[];
  graph_drivers: { value: GraphDriver; label: string }[];
  autonomy_levels: { value: AutonomyLevel; label: string }[];
  available_areas: AvailableArea[];
  defaults: Omit<WizardSubmission, "instance_name">;
};

export type WizardPreview = {
  yaml: string;
  warnings: string[];
};

export type WizardSubmitResult = {
  instance_id: string;
  status: string;
  yaml_path: string;
  next_steps: string[];
};
