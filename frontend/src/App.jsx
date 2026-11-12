import { Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./hooks/useTheme.jsx";
import Layout from "./layouts/Layout";
import Home from "./pages/Home";
import Assessment from "./pages/Assessment";
import Result from "./pages/Result";
import HistoryPage from "./pages/History";
import Insights from "./pages/Insights";

export default function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/assess" element={<Assessment />} />
          <Route path="/result" element={<Result />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/insights" element={<Insights />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  );
}
