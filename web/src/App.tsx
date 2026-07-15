import { Route, Router, Switch } from "wouter";
import { useHashLocation } from "wouter/use-hash-location";
import Sidebar from "./components/Sidebar";
import { ToastProvider } from "./components/Toast";
import Instances from "./pages/Instances";
import Wizard from "./pages/Wizard";
import Providers from "./pages/Providers";
import Ecosystem from "./pages/Ecosystem";
import Agents from "./pages/Agents";
import Jarvis from "./pages/Jarvis";
import Voice from "./pages/Voice";
import SettingsPage from "./pages/Settings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <ToastProvider>
      <Router hook={useHashLocation}>
        <div className="flex h-full min-h-screen bg-bg">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <Switch>
              <Route path="/" component={Instances} />
              <Route path="/wizard" component={Wizard} />
              <Route path="/providers" component={Providers} />
              <Route path="/ecosystem" component={Ecosystem} />
              <Route path="/agents" component={Agents} />
              <Route path="/jarvis" component={Jarvis} />
              <Route path="/voice" component={Voice} />
              <Route path="/settings" component={SettingsPage} />
              <Route component={NotFound} />
            </Switch>
          </main>
        </div>
      </Router>
    </ToastProvider>
  );
}
