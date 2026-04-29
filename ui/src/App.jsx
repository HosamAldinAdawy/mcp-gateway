import { useState, useEffect, useRef } from "react";

const API_BASE = "http://localhost:8000";

const COLORS = {
  bg: "#0a0a0f",
  surface: "#13131a",
  border: "#1e1e2e",
  borderHover: "#2e2e4e",
  accent: "#6366f1",
  accentGlow: "rgba(99,102,241,0.15)",
  success: "#22c55e",
  danger: "#ef4444",
  warning: "#f59e0b",
  text: "#e2e8f0",
  textMuted: "#64748b",
  textDim: "#334155",
};

const css = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@400;600;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: ${COLORS.bg};
    color: ${COLORS.text};
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: ${COLORS.bg}; }
  ::-webkit-scrollbar-thumb { background: ${COLORS.border}; border-radius: 2px; }

  .mono { font-family: 'JetBrains Mono', monospace; }

  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  @keyframes spin { to { transform: rotate(360deg); } }

  .fade-in { animation: fadeIn 0.3s ease forwards; }

  .btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px; border-radius: 8px; border: none;
    font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.15s; letter-spacing: 0.02em;
  }
  .btn-primary { background: ${COLORS.accent}; color: white; }
  .btn-primary:hover { background: #7c3aed; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(99,102,241,0.4); }
  .btn-primary:disabled { background: ${COLORS.textDim}; cursor: not-allowed; transform: none; box-shadow: none; }
  .btn-ghost { background: transparent; color: ${COLORS.textMuted}; border: 1px solid ${COLORS.border}; }
  .btn-ghost:hover { color: ${COLORS.text}; border-color: ${COLORS.borderHover}; background: rgba(255,255,255,0.03); }

  .card {
    background: ${COLORS.surface};
    border: 1px solid ${COLORS.border};
    border-radius: 12px;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: ${COLORS.borderHover}; }

  .badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 8px; border-radius: 100px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
  }
  .badge-green { background: rgba(34,197,94,0.1); color: ${COLORS.success}; }
  .badge-red { background: rgba(239,68,68,0.1); color: ${COLORS.danger}; }
  .badge-blue { background: rgba(99,102,241,0.15); color: #818cf8; }
  .badge-yellow { background: rgba(245,158,11,0.1); color: ${COLORS.warning}; }

  .input {
    background: ${COLORS.bg}; color: ${COLORS.text};
    border: 1px solid ${COLORS.border}; border-radius: 8px;
    padding: 9px 12px; font-size: 13px; outline: none; width: 100%;
    font-family: 'JetBrains Mono', monospace;
    transition: border-color 0.15s;
  }
  .input:focus { border-color: ${COLORS.accent}; box-shadow: 0 0 0 3px ${COLORS.accentGlow}; }
  .input::placeholder { color: ${COLORS.textDim}; }

  select.input { cursor: pointer; }

  .tag {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
    background: rgba(99,102,241,0.08); color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.2); cursor: pointer;
    transition: all 0.15s;
  }
  .tag:hover { background: rgba(99,102,241,0.2); }
  .tag.active { background: rgba(99,102,241,0.25); color: white; border-color: ${COLORS.accent}; }

  .log-entry {
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    padding: 8px 12px; border-radius: 6px; margin-bottom: 4px;
    border-left: 2px solid transparent;
    animation: fadeIn 0.2s ease;
  }
  .log-ok { border-left-color: ${COLORS.success}; background: rgba(34,197,94,0.04); }
  .log-err { border-left-color: ${COLORS.danger}; background: rgba(239,68,68,0.04); }

  .spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.2); border-top-color: white; border-radius: 50%; animation: spin 0.6s linear infinite; }

  .dot { width: 7px; height: 7px; border-radius: 50%; animation: pulse 2s infinite; }
  .dot-green { background: ${COLORS.success}; }
  .dot-red { background: ${COLORS.danger}; }

  .nav-tab-bar {
    display: flex;
    border-bottom: 1px solid ${COLORS.border};
    background: ${COLORS.surface};
    padding: 0 24px;
  }
  .nav-tab {
    padding: 12px 18px; font-size: 13px; font-weight: 600;
    color: ${COLORS.textMuted}; cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.15s; letter-spacing: 0.02em;
    font-family: 'Syne', sans-serif;
  }
  .nav-tab:hover { color: ${COLORS.text}; }
  .nav-tab.active { color: ${COLORS.accent}; border-bottom-color: ${COLORS.accent}; }

  .tpl-card {
    background: ${COLORS.surface};
    border: 1px solid ${COLORS.border};
    border-radius: 10px; padding: 12px;
    cursor: pointer; transition: all 0.15s;
  }
  .tpl-card:hover { border-color: ${COLORS.borderHover}; }
  .tpl-card.selected { border-color: ${COLORS.accent}; background: ${COLORS.accentGlow}; }

  .output-tab {
    padding: 5px 14px; font-size: 12px; font-weight: 600;
    border-radius: 6px; cursor: pointer;
    border: 1px solid ${COLORS.border};
    background: transparent; color: ${COLORS.textMuted};
    font-family: 'Syne', sans-serif; transition: all 0.15s;
  }
  .output-tab:hover { color: ${COLORS.text}; }
  .output-tab.active { background: ${COLORS.borderHover}; color: ${COLORS.text}; border-color: ${COLORS.borderHover}; }
`;

// ── Templates ──────────────────────────────────────────────────────────────────
const TEMPLATES = {
  qa: [
    { id: "jira", name: "Jira", tools: ["create_issue","search_issues","update_issue","get_issue","add_comment"],
      creds: [{ key: "jira_url", label: "Jira URL", placeholder: "https://company.atlassian.net" }, { key: "jira_email", label: "Email", placeholder: "you@company.com" }, { key: "jira_token", label: "API token", placeholder: "ATATT..." }] },
    { id: "testrail", name: "TestRail", tools: ["get_test_cases","create_test_case","add_result","create_run"],
      creds: [{ key: "testrail_url", label: "TestRail URL", placeholder: "https://company.testrail.io" }, { key: "testrail_user", label: "Username", placeholder: "you@company.com" }, { key: "testrail_key", label: "API key", placeholder: "your-api-key" }] },
    { id: "pytest", name: "Pytest", tools: ["run_tests","run_suite","get_coverage"],
      creds: [{ key: "project_path", label: "Project path", placeholder: "/home/user/project" }] },
  ],
  dev: [
    { id: "github", name: "GitHub", tools: ["create_issue","list_prs","merge_pr","create_branch","get_commits"],
      creds: [{ key: "github_token", label: "GitHub token", placeholder: "ghp_..." }] },
    { id: "git-local", name: "Git local", tools: ["status","diff","commit","log","branch"],
      creds: [{ key: "repo_path", label: "Repo path", placeholder: "/home/user/myrepo" }] },
    { id: "azure", name: "Azure DevOps", tools: ["create_work_item","get_pipeline","run_pipeline"],
      creds: [{ key: "azure_org", label: "Organization", placeholder: "myorg" }, { key: "azure_token", label: "PAT token", placeholder: "your-pat" }] },
    { id: "code-runner", name: "Code runner", tools: ["run_python","run_shell","run_javascript"], creds: [] },
  ],
  general: [
    { id: "filesystem", name: "Filesystem", tools: ["read_file","write_file","search_files","list_dir"],
      creds: [{ key: "base_path", label: "Base path", placeholder: "/home/user" }] },
    { id: "slack", name: "Slack", tools: ["send_message","list_channels","get_messages"],
      creds: [{ key: "slack_token", label: "Bot token", placeholder: "xoxb-..." }] },
    { id: "rest-api", name: "REST API", tools: ["get","post","put","patch","delete"],
      creds: [{ key: "base_url", label: "Base URL", placeholder: "https://api.example.com" }] },
    { id: "web-search", name: "Web search", tools: ["search","fetch_page"], creds: [] },
  ],
};

const CAT_COLORS = { qa: COLORS.success, dev: COLORS.accent, general: COLORS.warning };
const CAT_LABELS  = { qa: "QA Tools", dev: "Dev Tools", general: "General" };

// ── Status Bar ─────────────────────────────────────────────────────────────────
function StatusBar({ apiKey, status }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 24px", borderBottom: `1px solid ${COLORS.border}`, background: COLORS.surface }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: "-0.02em" }}>
          MCP<span style={{ color: COLORS.accent }}>·</span>Gateway
        </div>
        <span className="badge badge-blue mono">v1.0.0</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {status && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: COLORS.textMuted }}>
            <div className={`dot ${status.servers_healthy > 0 ? "dot-green" : "dot-red"}`} />
            <span className="mono">{status.servers_healthy}/{status.servers_registered} servers</span>
          </div>
        )}
        {apiKey && (
          <span className="mono" style={{ fontSize: 11, color: COLORS.textMuted, background: COLORS.bg, padding: "4px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}` }}>
            {apiKey.slice(0, 8)}***
          </span>
        )}
      </div>
    </div>
  );
}

// ── Auth Screen ────────────────────────────────────────────────────────────────
function AuthScreen({ onAuth }) {
  const [mode, setMode]       = useState("have");   // "have" | "new"
  const [key, setKey]         = useState("");
  const [generated, setGenerated] = useState("");
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedEnv, setCopiedEnv] = useState(false);
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const generateKey = () => {
    const arr = new Uint8Array(24);
    crypto.getRandomValues(arr);
    const newKey = Array.from(arr).map(b => b.toString(16).padStart(2,"0")).join("");
    setGenerated(newKey);
    setCopiedKey(false);
    setCopiedEnv(false);
  };

  const copyKey = () => {
    navigator.clipboard.writeText(generated).catch(() => {});
    setCopiedKey(true); setTimeout(() => setCopiedKey(false), 1500);
  };

  const copyEnvLine = () => {
    navigator.clipboard.writeText(`MCP_API_KEYS=${generated}`).catch(() => {});
    setCopiedEnv(true); setTimeout(() => setCopiedEnv(false), 1500);
  };

  const submit = async () => {
    if (!key.trim()) return;
    setLoading(true); setError("");
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": key } });
      if (r.ok) { onAuth(key); }
      else { setError("Invalid API key — make sure it matches MCP_API_KEYS in your .env"); }
    } catch {
      setError("Cannot reach gateway — is it running? Try: make run");
    }
    setLoading(false);
  };

  const S = {
    page:    { minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 24 },
    card:    { width: "100%", maxWidth: 460, padding: 40 },
    title:   { fontSize: 32, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 8 },
    sub:     { color: COLORS.textMuted, fontSize: 14, marginBottom: 32, textAlign: "center" },
    tabs:    { display: "flex", gap: 0, border: `1px solid ${COLORS.border}`, borderRadius: 8, overflow: "hidden", marginBottom: 24 },
    tab:     (active) => ({ flex: 1, padding: "9px 0", fontSize: 13, fontWeight: 600, cursor: "pointer", background: active ? COLORS.accent : "transparent", color: active ? "white" : COLORS.textMuted, border: "none", fontFamily: "'Syne', sans-serif", transition: "all 0.15s" }),
    label:   { fontSize: 11, color: COLORS.textMuted, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" },
    hint:    { fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6, padding: "10px 14px", background: COLORS.bg, borderRadius: 8, border: `1px solid ${COLORS.border}` },
    hintIcon:{ color: COLORS.accent, marginRight: 6 },
    genBox:  { background: COLORS.bg, border: `1px solid ${COLORS.borderHover}`, borderRadius: 8, padding: "12px 14px" },
    mono:    { fontFamily: "JetBrains Mono, monospace", fontSize: 12, color: "#a5b4fc", wordBreak: "break-all", lineHeight: 1.6 },
    copyBtn: (copied) => ({ background: "transparent", border: `1px solid ${COLORS.border}`, borderRadius: 5, padding: "3px 10px", fontSize: 11, cursor: "pointer", color: copied ? COLORS.success : COLORS.textMuted, fontFamily: "JetBrains Mono, monospace", whiteSpace: "nowrap" }),
    step:    { display: "flex", gap: 10, alignItems: "flex-start" },
    stepNum: { width: 20, height: 20, borderRadius: "50%", background: COLORS.accentGlow, border: `1px solid ${COLORS.accent}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: COLORS.accent, flexShrink: 0, marginTop: 1 },
    stepTxt: { fontSize: 13, color: COLORS.text, lineHeight: 1.5 },
    stepSub: { fontSize: 11, color: COLORS.textMuted, marginTop: 3 },
  };

  return (
    <div style={S.page}>
      <div className="card fade-in" style={S.card}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 4 }}>
          <div style={S.title}>MCP<span style={{ color: COLORS.accent }}>·</span>Gateway</div>
        </div>
        <div style={S.sub}>Choose how to get started</div>

        {/* Mode tabs */}
        <div style={S.tabs}>
          <button style={S.tab(mode === "have")} onClick={() => { setMode("have"); setError(""); }}>I have an API key</button>
          <button style={S.tab(mode === "new")}  onClick={() => { setMode("new");  setError(""); }}>Generate a new key</button>
        </div>

        {/* ── Mode: have key ── */}
        {mode === "have" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <div style={S.label}>API Key</div>
              <input className="input" type="password" placeholder="your-api-key-here" value={key}
                onChange={e => setKey(e.target.value)} onKeyDown={e => e.key === "Enter" && submit()} autoFocus />
            </div>
            <div style={S.hint}>
              <span style={S.hintIcon}>🔑</span>
              Your key is stored in <span style={{ color: COLORS.text, fontFamily: "JetBrains Mono, monospace" }}>.env</span> under the line <span style={{ color: COLORS.text, fontFamily: "JetBrains Mono, monospace" }}>MCP_API_KEYS=</span>
              <div style={{ marginTop: 6, color: COLORS.textDim, fontSize: 11 }}>
                Don't have one yet? Switch to "Generate a new key" above
              </div>
            </div>
            {error && <div style={{ fontSize: 12, color: COLORS.danger, padding: "8px 12px", background: "rgba(239,68,68,0.08)", borderRadius: 6 }}>{error}</div>}
            <button className="btn btn-primary" onClick={submit} disabled={loading || !key.trim()} style={{ width: "100%", justifyContent: "center", padding: "11px" }}>
              {loading ? <div className="spinner" /> : "Connect →"}
            </button>
          </div>
        )}

        {/* ── Mode: new key ── */}
        {mode === "new" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Why hint */}
            <div style={S.hint}>
              <span style={S.hintIcon}>🔒</span>
              The API key protects your gateway — without it, no one can call your tools
            </div>

            {/* Step 1 — generate */}
            <div style={S.step}>
              <div style={S.stepNum}>1</div>
              <div style={{ flex: 1 }}>
                <div style={S.stepTxt}>Generate a secure key</div>
                <div style={S.stepSub}>A random key is generated for you — no need to type one</div>
                {!generated && (
                  <button className="btn btn-ghost" onClick={generateKey} style={{ marginTop: 10, fontSize: 12 }}>
                    Generate key
                  </button>
                )}
                {generated && (
                  <div style={{ ...S.genBox, marginTop: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
                      <div style={S.mono}>{generated}</div>
                      <button style={S.copyBtn(copiedKey)} onClick={copyKey}>{copiedKey ? "Copied ✓" : "Copy"}</button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Step 2 — add to .env */}
            {generated && (
              <div style={S.step}>
                <div style={S.stepNum}>2</div>
                <div style={{ flex: 1 }}>
                  <div style={S.stepTxt}>Add it to your <span style={{ fontFamily: "JetBrains Mono, monospace", color: COLORS.accent }}>.env</span></div>
                  <div style={S.stepSub}>Open the file and add this line</div>
                  <div style={{ ...S.genBox, marginTop: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
                      <div style={S.mono}>MCP_API_KEYS={generated}</div>
                      <button style={S.copyBtn(copiedEnv)} onClick={copyEnvLine}>{copiedEnv ? "Copied ✓" : "Copy"}</button>
                    </div>
                  </div>
                  <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 8, fontFamily: "JetBrains Mono, monospace" }}>
                    The .env file is in your gateway root folder
                  </div>
                </div>
              </div>
            )}

            {/* Step 3 — restart & connect */}
            {generated && (
              <div style={S.step}>
                <div style={S.stepNum}>3</div>
                <div style={{ flex: 1 }}>
                  <div style={S.stepTxt}>Restart the gateway</div>
                  <div style={{ ...S.genBox, marginTop: 10 }}>
                    <div style={S.mono}>make run</div>
                  </div>
                </div>
              </div>
            )}

            {/* After steps: use the key */}
            {generated && (
              <div style={{ borderTop: `1px solid ${COLORS.border}`, paddingTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ fontSize: 12, color: COLORS.textMuted, textAlign: "center" }}>Once done — enter your key below to connect</div>
                <input className="input" type="password" placeholder={generated.slice(0,8) + "..."} value={key}
                  onChange={e => setKey(e.target.value)} onKeyDown={e => e.key === "Enter" && submit()} />
                {error && <div style={{ fontSize: 12, color: COLORS.danger, padding: "8px 12px", background: "rgba(239,68,68,0.08)", borderRadius: 6 }}>{error}</div>}
                <button className="btn btn-primary" onClick={submit} disabled={loading || !key.trim()} style={{ width: "100%", justifyContent: "center", padding: "11px" }}>
                  {loading ? <div className="spinner" /> : "Connect →"}
                </button>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}

// ── Quick Setup ────────────────────────────────────────────────────────────────
function QuickSetup({ apiKey }) {
  const [selected, setSelected]   = useState(null);
  const [creds, setCreds]         = useState({});
  const [outputMode, setOutputMode] = useState("cursor");
  const [generated, setGenerated] = useState(false);
  const [copied, setCopied]       = useState(false);

  const selectTemplate = (tpl) => { setSelected(tpl); setCreds({}); setGenerated(false); };

  const allFilled = () => selected && selected.creds.every(c => creds[c.key]?.trim());

  const buildConfig = (mode) => {
    if (!selected) return "";
    if (mode === "cursor") {
      return JSON.stringify({ mcpServers: { [selected.id]: { url: `${API_BASE}/mcp`, headers: { "X-API-Key": apiKey } } } }, null, 2);
    }
    return JSON.stringify({ mcpServers: { [selected.id]: { command: "npx", args: ["-y", "@modelcontextprotocol/server-proxy", `${API_BASE}/mcp`], env: { X_API_KEY: apiKey } } } }, null, 2);
  };

  const configText = buildConfig(outputMode);
  const configHint = outputMode === "cursor"
    ? "Add it to .cursor/mcp.json in your project folder"
    : "Add it to ~/Library/Application Support/Claude/claude_desktop_config.json";

  const copyConfig = () => {
    navigator.clipboard.writeText(configText).catch(() => {});
    setCopied(true); setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", height: "calc(100vh - 101px)" }}>

      {/* Left — template picker */}
      <div style={{ borderRight: `1px solid ${COLORS.border}`, padding: 24, overflowY: "auto" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 16 }}>
          Choose a template
        </div>
        {Object.entries(TEMPLATES).map(([cat, list]) => (
          <div key={cat} style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: CAT_COLORS[cat], letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10, fontFamily: "JetBrains Mono, monospace" }}>
              {CAT_LABELS[cat]}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
              {list.map(tpl => (
                <div key={tpl.id} className={`tpl-card ${selected?.id === tpl.id ? "selected" : ""}`} onClick={() => selectTemplate(tpl)}>
                  <div style={{ width: 28, height: 28, borderRadius: 6, marginBottom: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, fontFamily: "JetBrains Mono, monospace", background: `${CAT_COLORS[cat]}22`, color: CAT_COLORS[cat] }}>
                    {tpl.name[0]}
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 3 }}>{tpl.name}</div>
                  <div style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "JetBrains Mono, monospace" }}>
                    {tpl.tools.slice(0,2).join(", ")}{tpl.tools.length > 2 ? ` +${tpl.tools.length - 2}` : ""}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Right — credentials + output */}
      <div style={{ padding: 24, overflowY: "auto", display: "flex", flexDirection: "column", gap: 16 }}>
        {!selected && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flexDirection: "column", gap: 12, color: COLORS.textDim }}>
            <div style={{ fontSize: 28 }}>←</div>
            <div style={{ fontSize: 14 }}>Select a template to get started</div>
          </div>
        )}

        {selected && (
          <>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14 }}>
                {selected.name} — credentials
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {selected.creds.map(c => (
                  <div key={c.key}>
                    <div style={{ fontSize: 11, color: COLORS.textMuted, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" }}>{c.label}</div>
                    <input className="input" placeholder={c.placeholder} value={creds[c.key] || ""}
                      onChange={e => { setCreds(p => ({ ...p, [c.key]: e.target.value })); setGenerated(false); }} />
                  </div>
                ))}
              </div>
            </div>

            <button className="btn btn-primary" onClick={() => setGenerated(true)}
              disabled={selected.creds.length > 0 && !allFilled()}
              style={{ width: "100%", justifyContent: "center", padding: "11px" }}>
              Generate config ↓
            </button>

            {generated && (
              <div className="fade-in">
                <div style={{ display: "flex", gap: 6, marginBottom: 10 }}>
                  {["cursor", "claude"].map(m => (
                    <button key={m} className={`output-tab ${outputMode === m ? "active" : ""}`} onClick={() => setOutputMode(m)}>
                      {m === "cursor" ? "Cursor" : "Claude Desktop"}
                    </button>
                  ))}
                </div>

                <div style={{ position: "relative", background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: "16px 14px" }}>
                  <button onClick={copyConfig} style={{ position: "absolute", top: 8, right: 8, background: COLORS.surface, border: `1px solid ${COLORS.borderHover}`, color: copied ? COLORS.success : COLORS.textMuted, borderRadius: 5, padding: "3px 10px", fontSize: 11, cursor: "pointer", fontFamily: "JetBrains Mono, monospace" }}>
                    {copied ? "Copied ✓" : "Copy"}
                  </button>
                  <pre style={{ fontSize: 11, fontFamily: "JetBrains Mono, monospace", color: "#a5b4fc", lineHeight: 1.7, overflowX: "auto", paddingRight: 48 }}>
                    {configText}
                  </pre>
                </div>

                <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 10 }}>{configHint}</div>

                <div style={{ marginTop: 12, padding: "10px 14px", background: COLORS.surface, borderRadius: 8, border: `1px solid ${COLORS.border}` }}>
                  <div style={{ fontSize: 11, color: COLORS.textMuted, marginBottom: 6, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>Available tools</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                    {selected.tools.map(t => <span key={t} className="tag">{t}</span>)}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Servers Panel ──────────────────────────────────────────────────────────────
function ServersPanel({ servers, selected, onSelect }) {
  const categories = {
    qa: servers.filter(s => ["jira","testrail","pytest-runner","xray","zephyr","allure-reporter","bdd-generator"].includes(s.name)),
    dev: servers.filter(s => ["github","git-local","azure-devops","code-runner"].includes(s.name)),
    general: servers.filter(s => !["jira","testrail","pytest-runner","xray","zephyr","github","git-local","azure-devops","code-runner"].includes(s.name)),
  };
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {Object.entries(categories).map(([cat, list]) =>
        list.length > 0 && (
          <div key={cat}>
            <div style={{ fontSize: 10, fontWeight: 700, color: CAT_COLORS[cat], letterSpacing: "0.1em", textTransform: "uppercase", padding: "8px 0 6px", fontFamily: "JetBrains Mono, monospace" }}>
              {CAT_LABELS[cat]}
            </div>
            {list.map(s => (
              <div key={s.name} onClick={() => onSelect(s)} className="card"
                style={{ padding: "10px 14px", marginBottom: 4, cursor: "pointer", borderColor: selected?.name === s.name ? COLORS.accent : COLORS.border, background: selected?.name === s.name ? COLORS.accentGlow : COLORS.surface }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>{s.name}</span>
                  <span style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "JetBrains Mono, monospace" }}>{s.tools.length} tools</span>
                </div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.description}</div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}

// ── Tool Runner ────────────────────────────────────────────────────────────────
function ToolRunner({ server, apiKey, onLog }) {
  const [tool, setTool]     = useState(server.tools[0] || "");
  const [args, setArgs]     = useState("{}");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  useEffect(() => { setTool(server.tools[0] || ""); setArgs("{}"); setResult(null); setError(""); }, [server]);

  const run = async () => {
    let parsed;
    try { parsed = JSON.parse(args); } catch { setError("Invalid JSON in arguments"); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await fetch(`${API_BASE}/v1/call`, { method: "POST", headers: { "X-API-Key": apiKey, "Content-Type": "application/json" }, body: JSON.stringify({ server: server.name, tool, arguments: parsed }) });
      const data = await r.json();
      setResult(data);
      onLog({ ts: new Date().toISOString(), server: server.name, tool, success: data.success, error: data.error });
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  return (
    <div className="card fade-in" style={{ padding: 24 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <div style={{ fontSize: 16, fontWeight: 700 }}>{server.name}</div>
        <span className="badge badge-blue">{server.transport}</span>
        <span style={{ fontSize: 11, color: COLORS.textMuted, fontFamily: "JetBrains Mono, monospace", marginLeft: "auto" }}>{server.url}</span>
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: COLORS.textMuted, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>Tool</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {server.tools.map(t => <span key={t} className={`tag ${tool === t ? "active" : ""}`} onClick={() => setTool(t)}>{t}</span>)}
        </div>
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: COLORS.textMuted, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Arguments (JSON)</div>
        <textarea className="input" rows={4} value={args} onChange={e => setArgs(e.target.value)} placeholder='{"key": "value"}' style={{ resize: "vertical" }} />
      </div>
      {error && <div style={{ fontSize: 12, color: COLORS.danger, padding: "8px 12px", background: "rgba(239,68,68,0.08)", borderRadius: 6, marginBottom: 12, fontFamily: "JetBrains Mono, monospace" }}>{error}</div>}
      <button className="btn btn-primary" onClick={run} disabled={loading} style={{ marginBottom: result ? 16 : 0 }}>
        {loading ? <><div className="spinner" /> Running...</> : "▶ Run Tool"}
      </button>
      {result && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <span className={`badge ${result.success ? "badge-green" : "badge-red"}`}>{result.success ? "SUCCESS" : "ERROR"}</span>
            <span style={{ fontSize: 11, color: COLORS.textMuted, fontFamily: "JetBrains Mono, monospace" }}>{server.name} / {tool}</span>
          </div>
          <pre style={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: 16, fontSize: 11, fontFamily: "JetBrains Mono, monospace", color: result.success ? COLORS.success : COLORS.danger, overflowX: "auto", maxHeight: 300, whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
            {JSON.stringify(result.success ? result.result : result.error, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

// ── Add Server Modal ───────────────────────────────────────────────────────────
function AddServerModal({ apiKey, onClose, onAdded }) {
  const [form, setForm] = useState({ name: "", description: "", url: "http://localhost:8001", tools: "", transport: "http" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    if (!form.name || !form.url || !form.tools) { setError("Name, URL, and tools are required"); return; }
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { method: "POST", headers: { "X-API-Key": apiKey, "Content-Type": "application/json" }, body: JSON.stringify({ ...form, tools: form.tools.split(",").map(t => t.trim()).filter(Boolean) }) });
      if (r.ok) { onAdded(); onClose(); }
      else { const d = await r.json(); setError(d.detail || "Failed"); }
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 24 }}>
      <div className="card fade-in" style={{ width: "100%", maxWidth: 480, padding: 32 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 16, fontWeight: 700 }}>Add Server to Registry</div>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: "4px 10px" }}>✕</button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[{ key: "name", label: "Server name", placeholder: "my-tool" }, { key: "description", label: "Description", placeholder: "What does it do?" }, { key: "url", label: "URL", placeholder: "http://localhost:8001" }, { key: "tools", label: "Tools (comma separated)", placeholder: "tool1, tool2, tool3" }].map(f => (
            <div key={f.key}>
              <div style={{ fontSize: 11, color: COLORS.textMuted, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" }}>{f.label}</div>
              <input className="input" placeholder={f.placeholder} value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))} />
            </div>
          ))}
          {error && <div style={{ fontSize: 12, color: COLORS.danger, padding: "8px 12px", background: "rgba(239,68,68,0.08)", borderRadius: 6 }}>{error}</div>}
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <button className="btn btn-ghost" onClick={onClose} style={{ flex: 1, justifyContent: "center" }}>Cancel</button>
            <button className="btn btn-primary" onClick={submit} disabled={loading} style={{ flex: 2, justifyContent: "center" }}>
              {loading ? <div className="spinner" /> : "Add to Registry"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Logs Panel ─────────────────────────────────────────────────────────────────
function LogsPanel({ logs }) {
  const ref = useRef(null);
  useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [logs]);
  return (
    <div className="card" style={{ padding: 20, height: 280 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.textMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 12 }}>
        Audit Log <span style={{ color: COLORS.textDim, fontWeight: 400 }}>— live</span>
      </div>
      <div ref={ref} style={{ height: 220, overflowY: "auto" }}>
        {logs.length === 0 && <div style={{ color: COLORS.textDim, fontSize: 12, fontFamily: "JetBrains Mono, monospace", padding: "20px 0" }}>No calls yet — run a tool to see logs here.</div>}
        {logs.map((l, i) => (
          <div key={i} className={`log-entry ${l.success ? "log-ok" : "log-err"}`}>
            <span style={{ color: COLORS.textMuted }}>{new Date(l.ts).toLocaleTimeString()} </span>
            <span style={{ color: l.success ? COLORS.success : COLORS.danger }}>{l.success ? "OK" : "ERR"} </span>
            <span style={{ color: COLORS.text }}>{l.server}</span>
            <span style={{ color: COLORS.textMuted }}>/</span>
            <span style={{ color: "#a5b4fc" }}>{l.tool}</span>
            {l.error && <span style={{ color: COLORS.danger }}> — {l.error}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────────────────
export default function App() {
  const [apiKey, setApiKey]   = useState(localStorage.getItem("mcp_key") || "");
  const [authed, setAuthed]   = useState(false);
  const [servers, setServers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [status, setStatus]   = useState(null);
  const [logs, setLogs]       = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [activeTab, setActiveTab] = useState("setup");

  const addLog = (entry) => setLogs(prev => [...prev.slice(-100), entry]);

  const auth = (key) => { setApiKey(key); localStorage.setItem("mcp_key", key); setAuthed(true); };

  const loadServers = async () => {
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": apiKey } });
      if (r.ok) { const d = await r.json(); setServers(d); if (!selected && d.length > 0) setSelected(d[0]); }
    } catch {}
  };

  const loadStatus = async () => {
    try { const r = await fetch(`${API_BASE}/status`); if (r.ok) setStatus(await r.json()); } catch {}
  };

  useEffect(() => { if (authed) { loadServers(); loadStatus(); } }, [authed]);

  useEffect(() => {
    if (apiKey) {
      fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": apiKey } })
        .then(r => { if (r.ok) setAuthed(true); }).catch(() => {});
    }
  }, []);

  if (!authed) return (<><style>{css}</style><AuthScreen onAuth={auth} /></>);

  return (
    <>
      <style>{css}</style>
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <StatusBar apiKey={apiKey} status={status} />

        <div className="nav-tab-bar">
          <div className={`nav-tab ${activeTab === "setup" ? "active" : ""}`} onClick={() => setActiveTab("setup")}>Quick Setup</div>
          <div className={`nav-tab ${activeTab === "dashboard" ? "active" : ""}`} onClick={() => setActiveTab("dashboard")}>Dashboard</div>
        </div>

        {activeTab === "setup" && <QuickSetup apiKey={apiKey} />}

        {activeTab === "dashboard" && (
          <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", flex: 1 }}>
            <div style={{ borderRight: `1px solid ${COLORS.border}`, padding: 16, overflowY: "auto", height: "calc(100vh - 101px)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: "0.08em" }}>Servers ({servers.length})</div>
                <button className="btn btn-ghost" onClick={() => setShowAdd(true)} style={{ padding: "3px 8px", fontSize: 11 }}>+ Add</button>
              </div>
              <ServersPanel servers={servers} selected={selected} onSelect={setSelected} />
            </div>
            <div style={{ padding: 24, overflowY: "auto", height: "calc(100vh - 101px)", display: "flex", flexDirection: "column", gap: 20 }}>
              {status && (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                  {[{ label: "Servers", value: status.servers_registered, color: COLORS.accent }, { label: "Healthy", value: status.servers_healthy, color: COLORS.success }, { label: "Calls Today", value: logs.length, color: COLORS.warning }].map(s => (
                    <div key={s.label} className="card" style={{ padding: "16px 20px" }}>
                      <div style={{ fontSize: 28, fontWeight: 800, color: s.color, letterSpacing: "-0.02em" }}>{s.value}</div>
                      <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 2 }}>{s.label}</div>
                    </div>
                  ))}
                </div>
              )}
              {selected ? <ToolRunner server={selected} apiKey={apiKey} onLog={addLog} /> : (
                <div className="card fade-in" style={{ padding: 40, textAlign: "center", color: COLORS.textMuted }}>
                  <div style={{ fontSize: 32, marginBottom: 12 }}>←</div>
                  <div style={{ fontSize: 14 }}>Select a server to start calling tools</div>
                </div>
              )}
              <LogsPanel logs={logs} />
            </div>
          </div>
        )}
      </div>
      {showAdd && <AddServerModal apiKey={apiKey} onClose={() => setShowAdd(false)} onAdded={loadServers} />}
    </>
  );
}
