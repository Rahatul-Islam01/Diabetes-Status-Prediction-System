import { Link, NavLink } from "react-router-dom";
import { Moon, Sun, Activity } from "lucide-react";
import { useTheme } from "../hooks/useTheme.jsx";

export default function Layout({ children }) {
  const { dark, toggle } = useTheme();
  const nav = [
    { to: "/", label: "Dashboard" },
    { to: "/assess", label: "Assessment" },
    { to: "/history", label: "History" },
    { to: "/insights", label: "Model Insights" },
  ];
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white/80 dark:bg-slate-800/80 backdrop-blur border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-semibold text-primary">
            <Activity className="w-5 h-5" /> Diabetes Status Predictor
          </Link>
          <nav className="hidden md:flex gap-1">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm ${isActive ? "bg-primary text-white" : "hover:bg-slate-100 dark:hover:bg-slate-700"}`
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
          <button onClick={toggle} className="p-2 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700">
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
        <nav className="md:hidden flex gap-1 px-4 pb-2 overflow-x-auto">
          {nav.map((n) => (
            <NavLink key={n.to} to={n.to} className="px-3 py-1.5 rounded-md text-sm bg-slate-100 dark:bg-slate-700 whitespace-nowrap">
              {n.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">{children}</main>
      <footer className="text-center text-xs text-slate-500 py-4">
        Research/educational tool. Not a medical diagnosis.
      </footer>
    </div>
  );
}
