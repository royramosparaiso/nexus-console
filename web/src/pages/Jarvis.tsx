export default function Jarvis() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          Jarvis-Console
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Natural-language operator for Console. Ask to create instances, sync providers, deploy agents.
        </p>
      </header>
      <div
        className="border border-dashed border-border rounded-lg p-12 text-center"
        data-testid="empty-jarvis"
      >
        <h2 className="text-lg font-medium text-text">Coming after Instance Registry v1</h2>
        <p className="text-sm text-text-muted mt-2 max-w-md mx-auto">
          Jarvis-Console will translate operator intents into signed commands to the target Platform.
        </p>
      </div>
    </div>
  );
}
