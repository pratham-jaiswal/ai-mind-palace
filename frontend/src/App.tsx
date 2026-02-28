import { Routes, Route, Link, useLocation } from "react-router-dom";
import ChatWindow from "./Components/ChatWindow";
import Dashboard from "./pages/Dashboard";
import MindMap from "./pages/MindMap";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import "./App.css";
import "./colors.css";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";

function App() {
  const location = useLocation();

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <img src="/logo192.png" alt="Logo" className="logo" />
          <span className="org-name">AI Mind Palace</span>
          <SignedIn>
            <nav className="header-nav">
              <Link to="/chat" className={location.pathname === "/chat" || location.pathname === "/" ? "active" : ""}>Chat</Link>
              <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : ""}>Dashboard</Link>
              <Link to="/mindmap" className={location.pathname === "/mindmap" ? "active" : ""}>Mind Map</Link>
            </nav>
          </SignedIn>
        </div>
        <div className="header-right">
          <SignedOut>
            <SignInButton>
              <button className="signin-btn">Log In</button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="*" element={
            <>
              <SignedOut>
                <div className="signout-prompt">
                  <h2>Welcome to AI Mind Palace</h2>
                  <p>Please sign in to access your second brain.</p>
                  <footer style={{ marginTop: '3rem', paddingTop: '1.5rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--subtext-color)' }}>
                    <span>AI can make mistakes. Consider verifying important information.</span>
                    <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
                    <span>&copy; {new Date().getFullYear()} Pratham Jaiswal</span>
                    <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
                    <a href="https://github.com/pratham-jaiswal/ai-mind-palace" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>GitHub</a>
                    <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
                    <Link to="/terms" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>Terms</Link>
                    <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
                    <Link to="/privacy" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>Privacy</Link>
                  </footer>
                </div>
              </SignedOut>
              <SignedIn>
                <Routes>
                  <Route path="/" element={<ChatWindow />} />
                  <Route path="/chat" element={<ChatWindow />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/mindmap" element={<MindMap />} />
                </Routes>
              </SignedIn>
            </>
          } />
        </Routes>
      </main>
    </div>
  );
}

export default App;
