import { useEffect, useState } from "react";
import { googleAuth, login, register } from "../lib/api.js";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const id = "google-client";
    if (document.getElementById(id)) return;

    const s = document.createElement("script");
    s.id = id;
    s.src = "https://accounts.google.com/gsi/client";
    s.async = true;
    s.defer = true;
    document.body.appendChild(s);

    s.onload = () => {
      if (!window.google) return;
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || "",
        callback: async (res) => {
          try {
            const token = await googleAuth(res.credential);
            localStorage.setItem("token", token.access_token);
            nav("/");
          } catch (e) {
            setMsg(e?.response?.data?.detail || "Google sign-in failed");
          }
        }
      });
      window.google.accounts.id.renderButton(
        document.getElementById("googleSignInDiv"),
        { theme: "outline", size: "large", type: "standard" }
      );
    };
  }, [nav]);

  async function doLogin() {
    try {
      const t = await login(email, pw);
      localStorage.setItem("token", t.access_token);
      nav("/");
    } catch (e) {
      setMsg(e?.response?.data?.detail || "Login failed");
    }
  }
  async function doRegister() {
    try {
      const t = await register(email, pw);
      localStorage.setItem("token", t.access_token);
      nav("/");
    } catch (e) {
      setMsg(e?.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div className="card">
      <h2>Sign in</h2>
      {msg && <p style={{color:"crimson"}}>{msg}</p>}
      <div id="googleSignInDiv" style={{marginBottom:12}}></div>

      <h3>Or with email</h3>
      <input placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
      <input type="password" placeholder="Password" value={pw} onChange={(e)=>setPw(e.target.value)} />
      <div style={{display:"flex", gap:8}}>
        <button onClick={doLogin}>Login</button>
        <button onClick={doRegister}>Register</button>
      </div>
    </div>
  );
}
