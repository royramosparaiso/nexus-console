export default function SettingsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          Settings
        </h1>
        <p className="text-sm text-text-muted mt-1">Console-level configuration.</p>
      </header>

      <section className="border border-border bg-surface rounded-lg p-5 space-y-3">
        <h2 className="text-sm font-semibold text-text">Console keys</h2>
        <p className="text-xs text-text-muted">
          Ed25519 keypair used to sign commands to Platform instances. Rotate periodically.
        </p>
        <button
          className="text-xs text-primary hover:underline"
          data-testid="button-rotate-keys"
        >
          Rotate keys…
        </button>
      </section>
    </div>
  );
}
