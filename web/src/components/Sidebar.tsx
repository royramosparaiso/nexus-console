import { Link, useLocation } from "wouter";
import { Boxes, Cpu, Key, Layers, Mic, Settings, Sparkles } from "lucide-react";

const items = [
  { href: "/", label: "Instances", icon: Boxes, testid: "nav-instances" },
  { href: "/providers", label: "LLM Providers", icon: Key, testid: "nav-providers" },
  { href: "/ecosystem", label: "Ecosystem", icon: Layers, testid: "nav-ecosystem" },
  { href: "/agents", label: "Agents", icon: Cpu, testid: "nav-agents" },
  { href: "/voice", label: "Voice", icon: Mic, testid: "nav-voice" },
  { href: "/jarvis", label: "Jarvis-Console", icon: Sparkles, testid: "nav-jarvis" },
  { href: "/settings", label: "Settings", icon: Settings, testid: "nav-settings" },
];

export default function Sidebar() {
  const [location] = useLocation();

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-surface flex flex-col" data-testid="sidebar">
      <div className="h-14 flex items-center px-5 border-b border-border">
        <Logo />
        <span className="ml-2 font-semibold tracking-tight text-text" data-testid="text-brand">
          Nexus Console
        </span>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {items.map((item) => {
          const active = location === item.href || (item.href !== "/" && location.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              data-testid={item.testid}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-surface-alt text-text"
                  : "text-text-muted hover:bg-surface-alt hover:text-text"
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border text-xs text-text-faint" data-testid="text-version">
        v0.1.0 · <span className="text-text-muted">local mode</span>
      </div>
    </aside>
  );
}

function Logo() {
  return (
    <svg width="24" height="24" viewBox="0 0 32 32" fill="none" aria-label="Nexus Console">
      <rect width="32" height="32" rx="8" className="fill-primary" />
      <path
        d="M8 22V10L16 18V10M24 10V22L16 14"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-bg"
      />
    </svg>
  );
}
