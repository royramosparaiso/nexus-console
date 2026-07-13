export default function NotFound() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
        Page not found
      </h1>
      <p className="text-sm text-text-muted mt-2">The route you requested doesn't exist.</p>
    </div>
  );
}
