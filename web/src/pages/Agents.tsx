export default function Agents() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          Agents
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Catalog of agents, areas and coordinators deployable to your instances.
        </p>
      </header>
      <div
        className="border border-dashed border-border rounded-lg p-12 text-center"
        data-testid="empty-agents"
      >
        <h2 className="text-lg font-medium text-text">Agent Factory coming soon</h2>
        <p className="text-sm text-text-muted mt-2 max-w-md mx-auto">
          The catalog will surface core areas, verticals and custom modules. From here you'll deploy
          agents to any registered instance.
        </p>
      </div>
    </div>
  );
}
