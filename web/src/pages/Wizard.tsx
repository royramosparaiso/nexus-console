import { useEffect, useMemo, useState } from "react";
import { useLocation } from "wouter";
import { ArrowLeft, ArrowRight, CheckCircle2, Loader2 } from "lucide-react";

import { apiFetch } from "@/lib/api";
import type {
  WizardPreview,
  WizardSchema,
  WizardSubmission,
  WizardSubmitResult,
} from "@/lib/wizardTypes";

import Step1Persona from "@/components/wizard/Step1Persona";
import Step2Deployment from "@/components/wizard/Step2Deployment";
import Step3Llms from "@/components/wizard/Step3Llms";
import Step4Memory from "@/components/wizard/Step4Memory";
import Step5Areas from "@/components/wizard/Step5Areas";
import Step6Governance from "@/components/wizard/Step6Governance";
import Preview from "@/components/wizard/Preview";

const TOTAL_STEPS = 6;

export default function Wizard() {
  const [, setLocation] = useLocation();
  const [schema, setSchema] = useState<WizardSchema | null>(null);
  const [schemaError, setSchemaError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const [submission, setSubmission] = useState<WizardSubmission | null>(null);
  const [preview, setPreview] = useState<WizardPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<WizardSubmitResult | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Load schema + hydrate submission with defaults
  useEffect(() => {
    apiFetch<WizardSchema>("/wizard/schema")
      .then((s) => {
        setSchema(s);
        setSubmission({
          instance_name: "",
          ...s.defaults,
        });
      })
      .catch((e) => setSchemaError(String(e)));
  }, []);

  // Debounced preview render on every submission change
  useEffect(() => {
    if (!submission) return;
    if (!submission.instance_name || !submission.persona.display_name) {
      setPreview(null);
      return;
    }
    const t = setTimeout(() => {
      setPreviewLoading(true);
      setPreviewError(null);
      apiFetch<WizardPreview>("/wizard/preview", {
        method: "POST",
        body: JSON.stringify(submission),
      })
        .then(setPreview)
        .catch((e) => setPreviewError(String(e)))
        .finally(() => setPreviewLoading(false));
    }, 300);
    return () => clearTimeout(t);
  }, [submission]);

  const canAdvance = useMemo(() => {
    if (!submission) return false;
    switch (step) {
      case 1:
        return submission.instance_name.length > 0 && submission.persona.display_name.length > 0;
      case 3:
        return submission.llms.enabled_providers.length > 0;
      case 5:
        return submission.areas.enabled.length > 0;
      default:
        return true;
    }
  }, [step, submission]);

  if (schemaError) {
    return (
      <div className="p-8 max-w-4xl mx-auto text-error" data-testid="schema-error">
        Failed to load wizard schema: {schemaError}
      </div>
    );
  }
  if (!schema || !submission) {
    return (
      <div className="p-8 max-w-4xl mx-auto text-text-muted flex items-center gap-2" data-testid="schema-loading">
        <Loader2 className="w-4 h-4 animate-spin" /> Loading wizard…
      </div>
    );
  }

  if (submitResult) {
    return <SuccessCard result={submitResult} onDone={() => setLocation("/")} />;
  }

  const patch = <K extends keyof WizardSubmission>(section: K, delta: Partial<WizardSubmission[K]>) => {
    setSubmission((prev) =>
      prev
        ? { ...prev, [section]: { ...(prev[section] as object), ...(delta as object) } as WizardSubmission[K] }
        : prev
    );
  };

  const onSubmit = async () => {
    if (!submission) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await apiFetch<WizardSubmitResult>("/wizard/submit", {
        method: "POST",
        body: JSON.stringify(submission),
      });
      setSubmitResult(result);
    } catch (e) {
      setSubmitError(String(e));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          New instance
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Six steps to emit <code className="text-xs bg-surface-alt px-1 py-0.5 rounded">nexus.instance.yaml</code> and
          bootstrap a Nexus Platform.
        </p>
      </header>

      <ProgressBar current={step} total={TOTAL_STEPS} steps={schema.steps.map((s) => s.label)} />

      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-6 mt-6">
        <div className="space-y-4">
          {step === 1 && (
            <Step1Persona
              schema={schema}
              instanceName={submission.instance_name}
              onInstanceNameChange={(v) => setSubmission((p) => (p ? { ...p, instance_name: v } : p))}
              value={submission.persona}
              onChange={(delta) => patch("persona", delta)}
            />
          )}
          {step === 2 && (
            <Step2Deployment
              schema={schema}
              value={submission.deployment}
              onChange={(delta) => patch("deployment", delta)}
            />
          )}
          {step === 3 && (
            <Step3Llms
              schema={schema}
              value={submission.llms}
              onChange={(delta) => patch("llms", delta)}
            />
          )}
          {step === 4 && (
            <Step4Memory
              schema={schema}
              value={submission.memory}
              onChange={(delta) => patch("memory", delta)}
            />
          )}
          {step === 5 && (
            <Step5Areas
              schema={schema}
              value={submission.areas}
              onChange={(delta) => patch("areas", delta)}
            />
          )}
          {step === 6 && (
            <Step6Governance
              schema={schema}
              value={submission.governance}
              onChange={(delta) => patch("governance", delta)}
            />
          )}

          {submitError && (
            <div className="text-sm text-error border border-error rounded-md p-3" data-testid="submit-error">
              {submitError}
            </div>
          )}

          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() => (step > 1 ? setStep(step - 1) : setLocation("/"))}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm text-text hover:bg-surface-alt transition-colors"
              data-testid="button-back"
            >
              <ArrowLeft className="w-4 h-4" />
              {step === 1 ? "Cancel" : "Back"}
            </button>
            {step < TOTAL_STEPS ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                disabled={!canAdvance}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-bg text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                data-testid="button-next"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={onSubmit}
                disabled={submitting}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-bg text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-40"
                data-testid="button-submit"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                {submitting ? "Creating…" : "Create instance"}
              </button>
            )}
          </div>
        </div>

        <Preview data={preview} loading={previewLoading} error={previewError} />
      </div>
    </div>
  );
}

function ProgressBar({
  current,
  total,
  steps,
}: {
  current: number;
  total: number;
  steps: string[];
}) {
  return (
    <div className="flex items-center gap-2" data-testid="progress-bar">
      {Array.from({ length: total }, (_, i) => i + 1).map((n) => {
        const active = n === current;
        const done = n < current;
        return (
          <div key={n} className="flex-1 flex flex-col items-start gap-1">
            <div
              className={`h-1 w-full rounded-full transition-colors ${
                done ? "bg-primary" : active ? "bg-primary" : "bg-border"
              }`}
            />
            <span
              className={`text-xs ${
                active ? "text-text" : done ? "text-text-muted" : "text-text-faint"
              }`}
              data-testid={`progress-step-${n}`}
            >
              {n}. {steps[n - 1]}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function SuccessCard({
  result,
  onDone,
}: {
  result: WizardSubmitResult;
  onDone: () => void;
}) {
  return (
    <div className="p-8 max-w-3xl mx-auto" data-testid="success-card">
      <div className="border border-success bg-surface rounded-lg p-8 space-y-5">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-8 h-8 text-success" />
          <div>
            <h1 className="text-xl font-semibold text-text">Instance registered</h1>
            <p className="text-sm text-text-muted mt-1">
              Status: <span className="text-text">{result.status}</span>
            </p>
          </div>
        </div>
        <dl className="text-sm space-y-1">
          <div className="flex gap-3">
            <dt className="text-text-muted w-28">Instance ID</dt>
            <dd className="text-text font-mono text-xs" data-testid="text-instance-id">{result.instance_id}</dd>
          </div>
          <div className="flex gap-3">
            <dt className="text-text-muted w-28">YAML</dt>
            <dd className="text-text font-mono text-xs">{result.yaml_path}</dd>
          </div>
        </dl>
        <div>
          <h2 className="text-sm font-semibold text-text mb-2">Next steps</h2>
          <ul className="list-disc list-inside text-sm text-text-muted space-y-1">
            {result.next_steps.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ul>
        </div>
        <button
          type="button"
          onClick={onDone}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-bg text-sm font-medium hover:bg-primary-hover transition-colors"
          data-testid="button-done"
        >
          Back to instances
        </button>
      </div>
    </div>
  );
}
