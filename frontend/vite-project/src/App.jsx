import { Outlet, Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { me } from "./lib/api.js";

export default function App() {
  const [user, setUser] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const m = await me();
        setUser({ email: m.email });
      } catch {
        setUser(null);
      }
    })();
  }, []);

  return (
    <div className="container">
      <header style={{display:"flex", alignItems:"center", gap:12, justifyContent:"space-between"}}>
        <h1><Link to="/">Notebook ML</Link></h1>
        <div>
          {user ? (
            <>
              <span style={{marginRight:8}}>Signed in as {user.email}</span>
              <button
                onClick={() => {
                  localStorage.removeItem("token");
                  setUser(null);
                  nav("/login");
                }}
              >
                Sign out
              </button>
            </>
          ) : (
            <Link to="/login">Sign in</Link>
          )}
        </div>
      </header>
      <main><Outlet /></main>
    </div>
  );
}
