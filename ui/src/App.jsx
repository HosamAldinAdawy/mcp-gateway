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
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }
  .theme-dark {
    --bg: #0a0a0f; --surface: #13131a; --border: #1e1e2e;
    --border-hover: #2e2e4e; --text: #e2e8f0;
    --text-muted: #64748b; --text-dim: #334155;
  }
  .theme-light {
    --bg: #f8fafc; --surface: #ffffff; --border: #e2e8f0;
    --border-hover: #cbd5e1; --text: #0f172a;
    --text-muted: #64748b; --text-dim: #94a3b8;
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
  .btn-danger { background: rgba(239,68,68,0.1); color: ${COLORS.danger}; border: 1px solid rgba(239,68,68,0.2); }
  .btn-danger:hover { background: rgba(239,68,68,0.2); }

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
      creds: [{ key: "jira_url", label: "Jira URL", placeholder: "https://company.atlassian.net" }, { key: "jira_email", label: "Email", placeholder: "you@company.com" }, { key: "jira_token", label: "API token", placeholder: "ATATT...", secret: true }] },
    { id: "testrail", name: "TestRail", tools: ["get_test_cases","create_test_case","add_result","create_run"],
      creds: [{ key: "testrail_url", label: "TestRail URL", placeholder: "https://company.testrail.io" }, { key: "testrail_user", label: "Username", placeholder: "you@company.com" }, { key: "testrail_key", label: "API key", placeholder: "your-api-key", secret: true }] },
    { id: "pytest", name: "Pytest", tools: ["run_tests","run_suite","get_coverage"],
      creds: [{ key: "project_path", label: "Project path", placeholder: "/home/user/project" }] },
    { id: "selenium", name: "Selenium", tools: ["navigate","click","type","get_text","screenshot","execute_script","find_elements","get_page_source","back","refresh","close"],
      creds: [{ key: "selenium_browser", label: "Browser", placeholder: "chrome" }, { key: "selenium_headless", label: "Headless (true/false)", placeholder: "true" }] },
  ],
  dev: [
    { id: "github", name: "GitHub", tools: ["create_issue","list_prs","merge_pr","create_branch","get_commits"],
      creds: [{ key: "github_token", label: "GitHub token", placeholder: "ghp_...", secret: true }] },
    { id: "git-local", name: "Git local", tools: ["status","diff","commit","log","branch"],
      creds: [{ key: "repo_path", label: "Repo path", placeholder: "/home/user/myrepo" }] },
    { id: "azure", name: "Azure DevOps", tools: ["create_work_item","get_pipeline","run_pipeline"],
      creds: [{ key: "azure_org", label: "Organization", placeholder: "myorg" }, { key: "azure_token", label: "PAT token", placeholder: "your-pat", secret: true }] },
    { id: "code-runner", name: "Code runner", tools: ["run_python","run_shell","run_javascript"], creds: [] },
  ],
  general: [
    { id: "filesystem", name: "Filesystem", tools: ["read_file","write_file","search_files","list_dir"],
      creds: [{ key: "base_path", label: "Base path", placeholder: "/home/user" }] },
    { id: "slack", name: "Slack", tools: ["send_message","list_channels","get_messages"],
      creds: [{ key: "slack_token", label: "Bot token", placeholder: "xoxb-...", secret: true }] },
    { id: "rest-api", name: "REST API", tools: ["get","post","put","patch","delete"],
      creds: [{ key: "base_url", label: "Base URL", placeholder: "https://api.example.com" }] },
    { id: "web-search", name: "Web search", tools: ["search","fetch_page"], creds: [] },
  ],
};

const CAT_COLORS = { qa: COLORS.success, dev: COLORS.accent, general: COLORS.warning };
const CAT_LABELS  = { qa: "QA Tools", dev: "Dev Tools", general: "General" };

// ── Translations ──────────────────────────────────────────────────────────────
const T = {
  en: {
    appName: "MCP·Gateway",
    chooseLanguage: "Choose your language",
    chooseStart: "Choose how to get started",
    haveKey: "I have an API key",
    generateKey: "Generate a new key",
    apiKey: "API Key",
    keyHint: "Your key is stored in",
    keyHintUnder: "under",
    keyHintSwitch: "Don't have one yet? Switch to \"Generate a new key\" above",
    connect: "Connect →",
    invalidKey: "Invalid API key — make sure it matches MCP_API_KEYS in your .env",
    cantReach: "Cannot reach gateway — is it running? Try: make run",
    generateSecure: "Generate a secure key",
    generateSub: "A random key is generated for you — no need to type one",
    generateBtn: "Generate key",
    addToEnv: "Add it to your",
    addToEnvSub: "Open the file and add this line",
    envLocation: "The .env file is in your gateway root folder",
    restart: "Restart the gateway",
    onceDone: "Once done — enter your key below to connect",
    keyProtects: "The API key protects your gateway — without it, no one can call your tools",
    chooseTemplate: "Choose a template",
    credentials: "credentials",
    generateConfig: "Connect & Generate config ↓",
    connecting: "Connecting...",
    selectTemplate: "Select a template to get started",
    cursor: "Cursor",
    claudeDesktop: "Claude Desktop",
    copied: "Copied ✓",
    copy: "Copy",
    availableTools: "Available tools",
    cursorHint: "Add it to .cursor/mcp.json in your project folder",
    claudeHint: "Add it to ~/Library/Application Support/Claude/claude_desktop_config.json",
    serverStarted: "server started — ready",
    serverFailed: "Failed to start server",
    cantReachGw: "Cannot reach gateway — is it running?",
    totalCalls: "Total calls",
    successful: "Successful",
    failed: "Failed",
    filterPlaceholder: "Filter by server, tool, or key...",
    refresh: "↻ Refresh",
    auditLog: "Audit Log",
    loading: "loading...",
    noLogs: "No log entries yet — run a tool to see logs here.",
    customServer: "Custom MCP Server",
    customDesc: "Register any MCP server and optionally start it automatically.",
    serverName: "Server name",
    description: "Description",
    serverUrl: "Server URL",
    toolsLabel: "Tools (comma-separated)",
    transport: "Transport",
    startCommand: "Start command",
    startCommandNote: "(optional — auto-starts server)",
    addRegistry: "Add to Registry →",
    addStart: "Add & Start Server →",
    adding: "Adding...",
    starting: "Starting...",
    howItWorks: "How it works",
    serverAdded: "added to registry ✓",
    serverAddedStarted: "added and started ✓",
    quickSetup: "Quick Setup",
    dashboard: "Dashboard",
    logs: "Logs",
    customTab: "Custom Server",
    servers: "Servers",
    healthy: "Healthy",
    callsToday: "Calls Today",
    addServer: "+ Add",
    selectServer: "Select a server to start calling tools",
    tool: "Tool",
    argumentsJson: "Arguments (JSON)",
    running: "Running...",
    runTool: "▶ Run Tool",
    addToRegistryModal: "Add Server to Registry",
    cancel: "Cancel",
    nameUrlRequired: "Name, URL, and tools are required",
  },
  ar: {
    appName: "MCP·Gateway",
    chooseLanguage: "اختار لغتك",
    chooseStart: "ابدأ من هنا",
    haveKey: "عندي API key",
    generateKey: "ولّد key جديد",
    apiKey: "API Key",
    keyHint: "الـ key موجود في ملف",
    keyHintUnder: "في السطر",
    keyHintSwitch: "مش عندك key؟ اختار \"ولّد key جديد\" فوق",
    connect: "اتصال →",
    invalidKey: "الـ key غلط — تأكد إنه موجود في MCP_API_KEYS في الـ .env",
    cantReach: "مش قادر يوصل للـ gateway — شغّله أولاً",
    generateSecure: "ولّد key آمن",
    generateSub: "بيتولد تلقائي — مش محتاج تكتبه",
    generateBtn: "ولّد key",
    addToEnv: "حطه في ملف",
    addToEnvSub: "افتح الملف وضيف السطر ده",
    envLocation: "الملف موجود في فولدر الـ gateway",
    restart: "أعد تشغيل الـ gateway",
    onceDone: "بعد ما تخلص — حط الـ key هنا",
    keyProtects: "الـ key بيحمي الـ gateway — من غيره محدش يقدر يوصل",
    chooseTemplate: "اختار template",
    credentials: "بيانات الدخول",
    generateConfig: "اتصال وولّد الـ config ↓",
    connecting: "جاري الاتصال...",
    selectTemplate: "اختار template للبدء",
    cursor: "Cursor",
    claudeDesktop: "Claude Desktop",
    copied: "تم النسخ ✓",
    copy: "نسخ",
    availableTools: "الأدوات المتاحة",
    cursorHint: "حطه في .cursor/mcp.json في فولدر المشروع",
    claudeHint: "حطه في ~/Library/Application Support/Claude/claude_desktop_config.json",
    serverStarted: "server شغال — جاهز",
    serverFailed: "فشل تشغيل الـ server",
    cantReachGw: "مش قادر يوصل للـ gateway",
    totalCalls: "إجمالي الطلبات",
    successful: "ناجح",
    failed: "فاشل",
    filterPlaceholder: "فلتر بالـ server أو الـ tool أو الـ key...",
    refresh: "↻ تحديث",
    auditLog: "سجل العمليات",
    loading: "جاري التحميل...",
    noLogs: "مفيش سجلات لسه — شغّل أي tool",
    customServer: "سيرفر مخصص",
    customDesc: "سجّل أي MCP server وشغّله تلقائي.",
    serverName: "اسم الـ server",
    description: "وصف",
    serverUrl: "رابط الـ server",
    toolsLabel: "الأدوات (مفصولة بفواصل)",
    transport: "نوع الاتصال",
    startCommand: "أمر التشغيل",
    startCommandNote: "(اختياري — يشغّل تلقائي)",
    addRegistry: "إضافة للـ Registry →",
    addStart: "إضافة وتشغيل →",
    adding: "جاري الإضافة...",
    starting: "جاري التشغيل...",
    howItWorks: "كيف يعمل",
    serverAdded: "أُضيف للـ registry ✓",
    serverAddedStarted: "أُضيف وشغّل ✓",
    quickSetup: "إعداد سريع",
    dashboard: "لوحة التحكم",
    logs: "السجلات",
    customTab: "سيرفر مخصص",
    servers: "السيرفرات",
    healthy: "يعمل",
    callsToday: "طلبات اليوم",
    addServer: "+ إضافة",
    selectServer: "اختار server لتشغيل الأدوات",
    tool: "الأداة",
    argumentsJson: "المعاملات (JSON)",
    running: "جاري التشغيل...",
    runTool: "▶ تشغيل",
    addToRegistryModal: "إضافة server للـ Registry",
    cancel: "إلغاء",
    nameUrlRequired: "الاسم والـ URL والأدوات مطلوبة",
  },
  fr: {
    appName: "MCP·Gateway",
    chooseLanguage: "Choisissez votre langue",
    chooseStart: "Choisissez comment démarrer",
    haveKey: "J'ai une clé API",
    generateKey: "Générer une nouvelle clé",
    apiKey: "Clé API",
    keyHint: "Votre clé est dans le fichier",
    keyHintUnder: "sous la ligne",
    keyHintSwitch: "Pas de clé ? Passez à \"Générer une nouvelle clé\" ci-dessus",
    connect: "Connecter →",
    invalidKey: "Clé API invalide — vérifiez MCP_API_KEYS dans votre .env",
    cantReach: "Impossible d'atteindre le gateway — est-il en cours d'exécution ?",
    generateSecure: "Générer une clé sécurisée",
    generateSub: "Une clé aléatoire est générée pour vous",
    generateBtn: "Générer la clé",
    addToEnv: "Ajoutez-la à votre",
    addToEnvSub: "Ouvrez le fichier et ajoutez cette ligne",
    envLocation: "Le fichier .env est dans le dossier racine du gateway",
    restart: "Redémarrer le gateway",
    onceDone: "Une fois terminé — entrez votre clé ci-dessous",
    keyProtects: "La clé API protège votre gateway — sans elle, personne ne peut accéder à vos outils",
    chooseTemplate: "Choisir un template",
    credentials: "identifiants",
    generateConfig: "Connecter & Générer la config ↓",
    connecting: "Connexion...",
    selectTemplate: "Sélectionnez un template pour commencer",
    cursor: "Cursor",
    claudeDesktop: "Claude Desktop",
    copied: "Copié ✓",
    copy: "Copier",
    availableTools: "Outils disponibles",
    cursorHint: "Ajoutez-le dans .cursor/mcp.json dans votre dossier de projet",
    claudeHint: "Ajoutez-le dans ~/Library/Application Support/Claude/claude_desktop_config.json",
    serverStarted: "server démarré — prêt",
    serverFailed: "Échec du démarrage du server",
    cantReachGw: "Impossible d'atteindre le gateway",
    totalCalls: "Total des appels",
    successful: "Réussis",
    failed: "Échoués",
    filterPlaceholder: "Filtrer par server, outil ou clé...",
    refresh: "↻ Actualiser",
    auditLog: "Journal d'audit",
    loading: "chargement...",
    noLogs: "Aucune entrée — exécutez un outil pour voir les logs.",
    customServer: "Serveur personnalisé",
    customDesc: "Enregistrez n'importe quel serveur MCP et démarrez-le automatiquement.",
    serverName: "Nom du serveur",
    description: "Description",
    serverUrl: "URL du serveur",
    toolsLabel: "Outils (séparés par des virgules)",
    transport: "Transport",
    startCommand: "Commande de démarrage",
    startCommandNote: "(optionnel — démarre automatiquement)",
    addRegistry: "Ajouter au Registry →",
    addStart: "Ajouter & Démarrer →",
    adding: "Ajout...",
    starting: "Démarrage...",
    howItWorks: "Comment ça marche",
    serverAdded: "ajouté au registry ✓",
    serverAddedStarted: "ajouté et démarré ✓",
    quickSetup: "Configuration rapide",
    dashboard: "Tableau de bord",
    logs: "Journaux",
    customTab: "Serveur personnalisé",
    servers: "Serveurs",
    healthy: "En ligne",
    callsToday: "Appels aujourd'hui",
    addServer: "+ Ajouter",
    selectServer: "Sélectionnez un serveur pour utiliser les outils",
    tool: "Outil",
    argumentsJson: "Arguments (JSON)",
    running: "En cours...",
    runTool: "▶ Exécuter",
    addToRegistryModal: "Ajouter un serveur au Registry",
    cancel: "Annuler",
    nameUrlRequired: "Nom, URL et outils sont requis",
  },
};

// ── Splash / Loading Screen ────────────────────────────────────────────────────
function SplashScreen({ onDone }) {
  useEffect(() => {
    const total = 4200;
    const t = setTimeout(onDone, total);
    return () => clearTimeout(t);
  }, []);

  return (
    <div style={{ minHeight:"100vh", background:COLORS.bg, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:20 }}>
      <div id="splash-stage" style={{ position:"relative", width:200, height:160, display:"flex", alignItems:"center", justifyContent:"center" }}>
        <svg id="svgB" width="200" height="160" viewBox="0 0 200 160" style={{ position:"absolute", top:0, left:0, opacity:0, transition:"opacity .5s, transform .6s" }}>
          <rect x="76" y="24" width="16" height="112" rx="3" fill="none" stroke="#6366f1" strokeWidth="2.5"/>
          <rect x="108" y="24" width="16" height="112" rx="3" fill="none" stroke="#6366f1" strokeWidth="2.5"/>
          {[[56,48,.4],[56,80,1],[56,112,.4],[144,48,.4],[144,80,1],[144,112,.4]].map(([x,y,o],i)=>(
            <line key={i} x1={i<3?76:124} y1={y} x2={x} y2={y} stroke="#6366f1" strokeWidth="2" strokeLinecap="round" opacity={o}/>
          ))}
          <circle cx="100" cy="80" r="5" fill="#6366f1"/>
        </svg>

        <svg id="svgC" width="200" height="160" viewBox="0 0 200 160" style={{ position:"absolute", top:0, left:0, opacity:0, transition:"opacity .5s, transform .6s" }}>
          <path d="M80 20 L60 20 L60 140 L80 140" fill="none" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M120 20 L140 20 L140 140 L120 140" fill="none" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="100" cy="80" r="6" fill="#6366f1"/>
          <circle cx="100" cy="80" r="14" fill="none" stroke="#6366f1" strokeWidth="1.5" opacity=".4"/>
        </svg>

        <svg id="svgA" width="200" height="160" viewBox="0 0 200 160" style={{ position:"absolute", top:0, left:0, opacity:0, transition:"opacity .5s, transform .7s cubic-bezier(.34,1.56,.64,1)" }}>
          <path d="M100 10 L148 28 L148 76 C148 110 124 136 100 148 C76 136 52 110 52 76 L52 28 Z" fill="#6366f1" opacity=".1" stroke="#6366f1" strokeWidth="2.5" strokeLinejoin="round"/>
          <line x1="100" y1="60" x2="100" y2="100" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round"/>
          <line x1="80" y1="80" x2="120" y2="80" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="100" cy="80" r="5" fill="#6366f1"/>
        </svg>
      </div>

      <div id="splash-name" style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:20, fontWeight:800, color:COLORS.text, letterSpacing:"-.02em", opacity:0, transition:"opacity .6s" }}>
        MCP<span style={{color:COLORS.accent}}>·</span>Gateway
      </div>
      <div id="splash-slogan" style={{ fontSize:10, color:COLORS.textDim, letterSpacing:".14em", textTransform:"uppercase", opacity:0, transition:"opacity .6s" }}>
        Control Your MCP
      </div>

      <SplashAnimator />
    </div>
  );
}

function SplashAnimator() {
  useEffect(() => {
    const wait = (ms) => new Promise(r => setTimeout(r, ms));
    const show = (id, extra={}) => {
      const el = document.getElementById(id);
      if (el) Object.assign(el.style, { opacity:"1", ...extra });
    };
    const hide = (id, extra={}) => {
      const el = document.getElementById(id);
      if (el) Object.assign(el.style, { opacity:"0", ...extra });
    };

    (async () => {
      await wait(200);
      show("svgB");
      await wait(900);
      show("svgC");
      await wait(900);
      show("svgA");
      await wait(900);
      hide("svgB", { transform:"scale(.6)" });
      hide("svgC", { transform:"scale(.6)" });
      show("svgA", { transform:"scale(1.15)" });
      await wait(400);
      const a = document.getElementById("svgA");
      if (a) a.style.transform = "scale(1)";
      await wait(400);
      show("splash-name");
      await wait(300);
      show("splash-slogan");
    })();
  }, []);
  return null;
}

// ── Notification System ────────────────────────────────────────────────────────
function NotificationContainer({ notifications }) {
  return (
    <div style={{ position:"fixed", top:16, right:16, zIndex:9999, display:"flex", flexDirection:"column", gap:8, maxWidth:320 }}>
      {notifications.map(n => (
        <div key={n.id} className="fade-in" style={{
          background: n.type==="success" ? "rgba(34,197,94,0.12)" : n.type==="error" ? "rgba(239,68,68,0.12)" : "rgba(99,102,241,0.12)",
          border: `1px solid ${n.type==="success"?"rgba(34,197,94,0.3)":n.type==="error"?"rgba(239,68,68,0.3)":"rgba(99,102,241,0.3)"}`,
          borderRadius: 8, padding: "10px 14px", display:"flex", alignItems:"flex-start", gap:10,
          backdropFilter: "blur(8px)",
        }}>
          <span style={{fontSize:14,flexShrink:0}}>
            {n.type==="success"?"✅":n.type==="error"?"❌":"ℹ️"}
          </span>
          <div style={{flex:1}}>
            {n.title && <div style={{fontSize:12,fontWeight:700,color:n.type==="success"?COLORS.success:n.type==="error"?COLORS.danger:"#818cf8",marginBottom:2}}>{n.title}</div>}
            <div style={{fontSize:11,color:COLORS.textMuted,fontFamily:"JetBrains Mono, monospace"}}>{n.message}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Language Selector Screen ───────────────────────────────────────────────────
function LanguageScreen({ onSelect }) {
  const langs = [
    { code: "en", label: "English",  flag: "🇬🇧" },
    { code: "ar", label: "العربية",  flag: "🇪🇬", rtl: true },
    { code: "fr", label: "Français", flag: "🇫🇷" },
  ];
  return (
    <div style={{ minHeight:"100vh", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", padding:24, background:COLORS.bg }}>
      <div className="card fade-in" style={{ width:"100%", maxWidth:360, padding:40, textAlign:"center" }}>
        <div style={{ fontSize:28, fontWeight:800, letterSpacing:"-0.02em", marginBottom:8 }}>
          MCP<span style={{color:COLORS.accent}}>·</span>Gateway
        </div>
        <div style={{ fontSize:14, color:COLORS.textMuted, marginBottom:32 }}>Choose your language / اختار لغتك / Choisissez votre langue</div>
        <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
          {langs.map(l => (
            <button key={l.code} className="btn btn-ghost" onClick={() => onSelect(l.code)}
              style={{ width:"100%", justifyContent:"center", padding:"12px", fontSize:15, gap:12,
                direction: l.rtl ? "rtl" : "ltr" }}>
              <span style={{fontSize:20}}>{l.flag}</span>
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}


// ── Status Bar ─────────────────────────────────────────────────────────────────
function StatusBar({ apiKey, status, dark = true, onChangeLang }) {
  const [showKey, setShowKey] = useState(false);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 24px", borderBottom: `1px solid ${dark?"#1e1e2e":"#e2e8f0"}`, background: dark?"#0d0d14":"#ffffff" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: "-0.02em" }}>
          MCP<span style={{ color: COLORS.accent }}>·</span>Gateway
        </div>
        <span className="badge badge-blue mono">v1.0.0</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {status && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: COLORS.textMuted }}>
            <div className={`dot ${status.servers_healthy > 0 ? "dot-green" : "dot-red"}`} />
            <span className="mono">{status.servers_healthy}/{status.servers_registered} servers</span>
          </div>
        )}
        {apiKey && (
          <div style={{ display:"flex", alignItems:"center", gap:4 }}>
            <span className="mono" style={{ fontSize: 11, color: COLORS.textMuted, background: COLORS.bg, padding: "4px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, letterSpacing: showKey?".02em":".1em", transition:"all .2s" }}>
              {showKey ? apiKey : apiKey.slice(0,4) + "••••••••••••" + apiKey.slice(-4)}
            </span>
            <button onClick={()=>setShowKey(p=>!p)} style={{ background:"transparent", border:"none", cursor:"pointer", color:COLORS.textMuted, fontSize:13, padding:"2px 4px", lineHeight:1 }} title={showKey?"Hide key":"Show key"}>
              {showKey ? "🙈" : "👁"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Auth Screen ────────────────────────────────────────────────────────────────
function AuthScreen({ onAuth, t = T.en }) {
  const [mode, setMode]           = useState("have");
  const [key, setKey]             = useState("");
  const [generated, setGenerated] = useState("");
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedEnv, setCopiedEnv] = useState(false);
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);

  const generateKey = () => {
    const arr = new Uint8Array(24);
    crypto.getRandomValues(arr);
    setGenerated(Array.from(arr).map(b => b.toString(16).padStart(2,"0")).join(""));
    setCopiedKey(false); setCopiedEnv(false);
  };

  const copyKey = () => { navigator.clipboard.writeText(generated).catch(()=>{}); setCopiedKey(true); setTimeout(()=>setCopiedKey(false),1500); };
  const copyEnvLine = () => { navigator.clipboard.writeText(`MCP_API_KEYS=${generated}`).catch(()=>{}); setCopiedEnv(true); setTimeout(()=>setCopiedEnv(false),1500); };

  const submit = async () => {
    if (!key.trim()) return;
    setLoading(true); setError("");
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": key } });
      if (r.ok) { onAuth(key); }
      else { setError(t.invalidKey); }
    } catch { setError(t.cantReach); }
    setLoading(false);
  };

  const S = {
    page:    { minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 24 },
    card:    { width: "100%", maxWidth: 460, padding: 40 },
    title:   { fontSize: 32, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 8 },
    sub:     { color: COLORS.textMuted, fontSize: 14, marginBottom: 32, textAlign: "center" },
    tabs:    { display: "flex", border: `1px solid ${COLORS.border}`, borderRadius: 8, overflow: "hidden", marginBottom: 24 },
    tab:     (a) => ({ flex:1, padding:"9px 0", fontSize:13, fontWeight:600, cursor:"pointer", background: a?COLORS.accent:"transparent", color: a?"white":COLORS.textMuted, border:"none", fontFamily:"'Syne',sans-serif", transition:"all 0.15s" }),
    label:   { fontSize: 11, color: COLORS.textMuted, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" },
    hint:    { fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6, padding: "10px 14px", background: COLORS.bg, borderRadius: 8, border: `1px solid ${COLORS.border}` },
    hintIcon:{ color: COLORS.accent, marginRight: 6 },
    genBox:  { background: COLORS.bg, border: `1px solid ${COLORS.borderHover}`, borderRadius: 8, padding: "12px 14px" },
    mono:    { fontFamily: "JetBrains Mono, monospace", fontSize: 12, color: "#a5b4fc", wordBreak: "break-all", lineHeight: 1.6 },
    copyBtn: (c) => ({ background:"transparent", border:`1px solid ${COLORS.border}`, borderRadius:5, padding:"3px 10px", fontSize:11, cursor:"pointer", color: c?COLORS.success:COLORS.textMuted, fontFamily:"JetBrains Mono, monospace", whiteSpace:"nowrap" }),
    step:    { display: "flex", gap: 10, alignItems: "flex-start" },
    stepNum: { width:20, height:20, borderRadius:"50%", background:COLORS.accentGlow, border:`1px solid ${COLORS.accent}`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:10, fontWeight:700, color:COLORS.accent, flexShrink:0, marginTop:1 },
    stepTxt: { fontSize: 13, color: COLORS.text, lineHeight: 1.5 },
    stepSub: { fontSize: 11, color: COLORS.textMuted, marginTop: 3 },
  };

  return (
    <div style={S.page}>
      <div className="card fade-in" style={S.card}>
        <div style={{ textAlign:"center", marginBottom:4 }}>
          <div style={S.title}>MCP<span style={{color:COLORS.accent}}>·</span>Gateway</div>
        </div>
        <div style={S.sub}>{t.chooseStart}</div>
        <div style={S.tabs}>
          <button style={S.tab(mode==="have")} onClick={()=>{setMode("have");setError("");}}>{t.haveKey}</button>
          <button style={S.tab(mode==="new")}  onClick={()=>{setMode("new");setError("");}}>{t.generateKey}</button>
        </div>

        {mode === "have" && (
          <div style={{display:"flex",flexDirection:"column",gap:12}}>
            <div>
              <div style={S.label}>{t.apiKey}</div>
              <input className="input" type="password" placeholder="your-api-key-here" value={key}
                onChange={e=>setKey(e.target.value)} onKeyDown={e=>e.key==="Enter"&&submit()} autoFocus />
            </div>
            <div style={S.hint}>
              <span style={S.hintIcon}>🔑</span>
              Your key is stored in <span style={{color:COLORS.text,fontFamily:"JetBrains Mono, monospace"}}>.env</span> under <span style={{color:COLORS.text,fontFamily:"JetBrains Mono, monospace"}}>MCP_API_KEYS=</span>
              <div style={{marginTop:6,color:COLORS.textDim,fontSize:11}}>Don't have one yet? Switch to "Generate a new key" above</div>
            </div>
            {error && <div style={{fontSize:12,color:COLORS.danger,padding:"8px 12px",background:"rgba(239,68,68,0.08)",borderRadius:6}}>{error}</div>}
            <button className="btn btn-primary" onClick={submit} disabled={loading||!key.trim()} style={{width:"100%",justifyContent:"center",padding:"11px"}}>
              {loading ? <div className="spinner"/> : t.connect}
            </button>
          </div>
        )}

        {mode === "new" && (
          <div style={{display:"flex",flexDirection:"column",gap:16}}>
            <div style={S.hint}><span style={S.hintIcon}>🔒</span>The API key protects your gateway — without it, no one can call your tools</div>
            <div style={S.step}>
              <div style={S.stepNum}>1</div>
              <div style={{flex:1}}>
                <div style={S.stepTxt}>Generate a secure key</div>
                <div style={S.stepSub}>A random key is generated for you — no need to type one</div>
                {!generated && <button className="btn btn-ghost" onClick={generateKey} style={{marginTop:10,fontSize:12}}>Generate key</button>}
                {generated && (
                  <div style={{...S.genBox,marginTop:10}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:10}}>
                      <div style={S.mono}>{generated}</div>
                      <button style={S.copyBtn(copiedKey)} onClick={copyKey}>{copiedKey?"Copied ✓":"Copy"}</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
            {generated && (
              <div style={S.step}>
                <div style={S.stepNum}>2</div>
                <div style={{flex:1}}>
                  <div style={S.stepTxt}>Add it to your <span style={{fontFamily:"JetBrains Mono, monospace",color:COLORS.accent}}>.env</span></div>
                  <div style={S.stepSub}>Open the file and add this line</div>
                  <div style={{...S.genBox,marginTop:10}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:10}}>
                      <div style={S.mono}>MCP_API_KEYS={generated}</div>
                      <button style={S.copyBtn(copiedEnv)} onClick={copyEnvLine}>{copiedEnv?"Copied ✓":"Copy"}</button>
                    </div>
                  </div>
                  <div style={{fontSize:11,color:COLORS.textDim,marginTop:8,fontFamily:"JetBrains Mono, monospace"}}>The .env file is in your gateway root folder</div>
                </div>
              </div>
            )}
            {generated && (
              <div style={S.step}>
                <div style={S.stepNum}>3</div>
                <div style={{flex:1}}>
                  <div style={S.stepTxt}>Restart the gateway</div>
                  <div style={{...S.genBox,marginTop:10}}><div style={S.mono}>make run</div></div>
                </div>
              </div>
            )}
            {generated && (
              <div style={{borderTop:`1px solid ${COLORS.border}`,paddingTop:16,display:"flex",flexDirection:"column",gap:10}}>
                <div style={{fontSize:12,color:COLORS.textMuted,textAlign:"center"}}>Once done — enter your key below to connect</div>
                <input className="input" type="password" placeholder={generated.slice(0,8)+"..."} value={key}
                  onChange={e=>setKey(e.target.value)} onKeyDown={e=>e.key==="Enter"&&submit()} />
                {error && <div style={{fontSize:12,color:COLORS.danger,padding:"8px 12px",background:"rgba(239,68,68,0.08)",borderRadius:6}}>{error}</div>}
                <button className="btn btn-primary" onClick={submit} disabled={loading||!key.trim()} style={{width:"100%",justifyContent:"center",padding:"11px"}}>
                  {loading ? <div className="spinner"/> : "Connect →"}
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
function QuickSetup({ apiKey, t = T.en, isRtl = false, notify = ()=>{} }) {
  const [selected, setSelected]         = useState(null);
  const [creds, setCreds]               = useState({});
  const [outputMode, setOutputMode]     = useState("cursor");
  const [generated, setGenerated]       = useState(false);
  const [copied, setCopied]             = useState(false);
  const [connecting, setConnecting]     = useState(false);
  const [serverStatus, setServerStatus] = useState(null);
  const [serverMsg, setServerMsg]       = useState("");

  const selectTemplate = (tpl) => { setSelected(tpl); setCreds({}); setGenerated(false); setServerStatus(null); };
  const allFilled = () => selected && selected.creds.every(c => creds[c.key]?.trim());

  const ENV_MAP = {
    jira_url:"JIRA_URL", jira_email:"JIRA_EMAIL", jira_token:"JIRA_TOKEN",
    testrail_url:"TESTRAIL_URL", testrail_user:"TESTRAIL_USER", testrail_key:"TESTRAIL_KEY",
    github_token:"GITHUB_TOKEN", gitlab_token:"GITLAB_TOKEN", gitlab_url:"GITLAB_URL",
    azure_org:"AZURE_ORG", azure_token:"AZURE_TOKEN",
    confluence_url:"CONFLUENCE_URL", confluence_email:"CONFLUENCE_EMAIL", confluence_token:"CONFLUENCE_TOKEN",
    linear_api_key:"LINEAR_API_KEY", slack_token:"SLACK_TOKEN",
    notion_token:"NOTION_TOKEN", asana_token:"ASANA_TOKEN", figma_token:"FIGMA_TOKEN",
    project_path:"PLAYWRIGHT_PROJECT_PATH", base_path:"FILESYSTEM_BASE_PATH",
    base_url:"REST_API_BASE_URL", selenium_browser:"SELENIUM_BROWSER",
    selenium_headless:"SELENIUM_HEADLESS", repo_path:"GIT_REPO_PATH",
  };

  const connect = async () => {
    if (!selected) return;
    setConnecting(true); setServerStatus(null); setServerMsg("");
    const credentials = {};
    selected.creds.forEach(c => {
      const envKey = ENV_MAP[c.key] || c.key.toUpperCase();
      if (creds[c.key]) credentials[envKey] = creds[c.key];
    });
    try {
      const r = await fetch(`${API_BASE}/v1/setup`, {
        method: "POST",
        headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
        body: JSON.stringify({ server: selected.id, credentials }),
      });
      const data = await r.json();
      if (r.ok && data.started) {
        setServerStatus("ok");
        setServerMsg(`${selected.name} server started — ready`);
        notify("success", `${selected.name} started ✅`, `Running on port — ready to use`);
      } else {
        setServerStatus("error");
        setServerMsg(data.message || "Failed to start server");
        notify("error", `${selected.name} failed`, data.message || "Check your credentials");
      }
      setGenerated(true);
    } catch (e) {
      setServerStatus("error");
      setServerMsg("Cannot reach gateway — is it running?");
    }
    setConnecting(false);
  };

  const buildConfig = (mode) => {
    if (!selected) return "";
    if (mode === "cursor")
      return JSON.stringify({ mcpServers: { [selected.id]: { url: `${API_BASE}/mcp`, headers: { "X-API-Key": apiKey } } } }, null, 2);
    return JSON.stringify({ mcpServers: { [selected.id]: { url: `${API_BASE}/mcp`, headers: { "X-API-Key": apiKey } } } }, null, 2);
  };

  const configText = buildConfig(outputMode);
  const configHint = outputMode === "cursor"
    ? "Add it to .cursor/mcp.json in your project folder"
    : lang === "ar"
      ? "حطّه في %APPDATA%\\Claude\\claude_desktop_config.json (Windows) أو ~/Library/Application Support/Claude/claude_desktop_config.json (Mac)"
      : "Add it to %APPDATA%\\Claude\\claude_desktop_config.json (Windows) or ~/Library/Application Support/Claude/claude_desktop_config.json (Mac)";

  const copyConfig = () => {
    navigator.clipboard.writeText(configText).catch(()=>{});
    setCopied(true); setTimeout(()=>setCopied(false),1500);
    notify("success", "Config copied!", `${selected?.name} config ready — paste it in ${outputMode==="cursor"?"Cursor":"Claude Desktop"}`);
  };

  return (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", height:"calc(100vh - 101px)" }}>
      <div style={{ borderRight:`1px solid ${COLORS.border}`, padding:24, overflowY:"auto" }}>
        <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:16 }}>{t.chooseTemplate}</div>
        {Object.entries(TEMPLATES).map(([cat, list]) => (
          <div key={cat} style={{ marginBottom:20 }}>
            <div style={{ fontSize:10, fontWeight:700, color:CAT_COLORS[cat], letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:10, fontFamily:"JetBrains Mono, monospace" }}>{CAT_LABELS[cat]}</div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(2, 1fr)", gap:8 }}>
              {list.map(tpl => (
                <div key={tpl.id} className={`tpl-card ${selected?.id===tpl.id?"selected":""}`} onClick={()=>selectTemplate(tpl)}>
                  <div style={{ width:28, height:28, borderRadius:6, marginBottom:8, display:"flex", alignItems:"center", justifyContent:"center", fontSize:12, fontWeight:700, fontFamily:"JetBrains Mono, monospace", background:`${CAT_COLORS[cat]}22`, color:CAT_COLORS[cat] }}>{tpl.name[0]}</div>
                  <div style={{ fontSize:13, fontWeight:600, marginBottom:3 }}>{tpl.name}</div>
                  <div style={{ fontSize:10, color:COLORS.textMuted, fontFamily:"JetBrains Mono, monospace" }}>{tpl.tools.slice(0,2).join(", ")}{tpl.tools.length>2?` +${tpl.tools.length-2}`:""}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{ padding:24, overflowY:"auto", display:"flex", flexDirection:"column", gap:16 }}>
        {!selected && (
          <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"100%", flexDirection:"column", gap:12, color:COLORS.textDim }}>
            <div style={{ fontSize:28 }}>←</div>
            <div style={{ fontSize:14 }}>{t.selectTemplate}</div>
          </div>
        )}
        {selected && (
          <>
            <div>
              <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:14 }}>{selected.name} — credentials</div>
              <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                {selected.creds.map(c => {
                  const [show, setShow] = useState(false);
                  return (
                    <div key={c.key}>
                      <div style={{ fontSize:11, color:COLORS.textMuted, marginBottom:5, textTransform:"uppercase", letterSpacing:"0.06em" }}>{c.label}</div>
                      <div style={{position:"relative"}}>
                        <input className="input" type={c.secret && !show ? "password" : "text"}
                          placeholder={c.placeholder} value={creds[c.key]||""}
                          onChange={e=>{setCreds(p=>({...p,[c.key]:e.target.value}));setGenerated(false);}}
                          style={{paddingRight: c.secret ? "32px" : "12px"}} />
                        {c.secret && (
                          <button onClick={()=>setShow(p=>!p)} style={{position:"absolute",right:8,top:"50%",transform:"translateY(-50%)",background:"transparent",border:"none",cursor:"pointer",color:COLORS.textMuted,fontSize:13,lineHeight:1,padding:0}}>
                            {show ? "🙈" : "👁"}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <button className="btn btn-primary" onClick={connect} disabled={connecting||(selected.creds.length>0&&!allFilled())} style={{width:"100%",justifyContent:"center",padding:"11px"}}>{connecting?<><div className="spinner"/> {t.connecting}</>:t.generateConfig}</button>
            {serverStatus && (
              <div className="fade-in" style={{ display:"flex", alignItems:"center", gap:8, padding:"8px 12px", background: serverStatus==="ok"?"rgba(34,197,94,0.06)":"rgba(239,68,68,0.06)", border:`1px solid ${serverStatus==="ok"?"rgba(34,197,94,0.2)":"rgba(239,68,68,0.2)"}`, borderRadius:6 }}>
                <div style={{ width:6, height:6, borderRadius:"50%", background: serverStatus==="ok"?COLORS.success:COLORS.danger, flexShrink:0 }}/>
                <span style={{ fontSize:11, color: serverStatus==="ok"?COLORS.success:COLORS.danger }}>{serverMsg}</span>
              </div>
            )}
            {generated && (
              <div className="fade-in">
                <div style={{ display:"flex", gap:6, marginBottom:10 }}>
                  {["cursor","claude"].map(m => (
                    <button key={m} className={`output-tab ${outputMode===m?"active":""}`} onClick={()=>setOutputMode(m)}>{m==="cursor"?t.cursor:t.claudeDesktop}</button>
                  ))}
                </div>
                <div style={{ position:"relative", background:COLORS.bg, border:`1px solid ${COLORS.border}`, borderRadius:8, padding:"16px 14px" }}>
                  <button onClick={copyConfig} style={{ position:"absolute", top:8, right:8, background:COLORS.surface, border:`1px solid ${COLORS.borderHover}`, color:copied?COLORS.success:COLORS.textMuted, borderRadius:5, padding:"3px 10px", fontSize:11, cursor:"pointer", fontFamily:"JetBrains Mono, monospace" }}>{copied?t.copied:t.copy}</button>
                  <pre style={{ fontSize:11, fontFamily:"JetBrains Mono, monospace", color:"#a5b4fc", lineHeight:1.7, overflowX:"auto", paddingRight:48 }}>{configText}</pre>
                </div>
                <div style={{ fontSize:12, color:COLORS.textMuted, marginTop:10 }}>{configHint}</div>
                <div style={{ marginTop:12, padding:"10px 14px", background:COLORS.surface, borderRadius:8, border:`1px solid ${COLORS.border}` }}>
                  <div style={{ fontSize:11, color:COLORS.textMuted, marginBottom:6, fontWeight:700, textTransform:"uppercase", letterSpacing:"0.06em" }}>{t.availableTools}</div>
                  <div style={{ display:"flex", flexWrap:"wrap", gap:5 }}>{selected.tools.map(t=><span key={t} className="tag">{t}</span>)}</div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Settings Tab ──────────────────────────────────────────────────────────────
function SettingsTab({ apiKey, notify = ()=>{} }) {
  const [form, setForm] = useState({
    port: "8000", rate_limit: "60", cors_origins: "*",
    log_level: "info",
  });
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded]   = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/v1/settings`, { headers: { "X-API-Key": apiKey } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) { setForm(f => ({...f,...d})); } setLoaded(true); })
      .catch(() => setLoaded(true));
  }, []);

  const restart = async () => {
    setLoading(true);
    try {
      // Save first then restart
      const credentials = {
        PORT: form.port,
        RATE_LIMIT_PER_MINUTE: form.rate_limit,
        ALLOWED_ORIGINS: form.cors_origins,
        LOG_LEVEL: form.log_level,
      };
      await fetch(`${API_BASE}/v1/setup`, {
        method: "POST",
        headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
        body: JSON.stringify({ server: "_settings", credentials }),
      });
      // Call restart endpoint
      const r = await fetch(`${API_BASE}/v1/restart`, {
        method: "POST",
        headers: { "X-API-Key": apiKey },
      });
      notify("success", "Restarting... ↺", "Gateway will restart in 2 seconds — reconnecting");
      // Wait then reload page
      setTimeout(() => window.location.reload(), 3000);
    } catch {
      // Gateway restarted — reload anyway
      notify("success", "Restarting... ↺", "Reconnecting in 3 seconds");
      setTimeout(() => window.location.reload(), 3000);
    }
    setLoading(false);
  };

  const save = async () => {
    setLoading(true);
    try {
      const credentials = {
        PORT: form.port,
        RATE_LIMIT_PER_MINUTE: form.rate_limit,
        ALLOWED_ORIGINS: form.cors_origins,
        LOG_LEVEL: form.log_level,
      };
      const r = await fetch(`${API_BASE}/v1/setup`, {
        method: "POST",
        headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
        body: JSON.stringify({ server: "_settings", credentials }),
      });
      if (r.ok) {
        notify("success", "Settings saved ✅", "Restart gateway to apply port changes");
      } else {
        notify("error", "Failed to save", "Check gateway logs");
      }
    } catch (e) { notify("error", "Error", e.message); }
    setLoading(false);
  };

  const fields = [
    { key:"port",         label:"Port",             placeholder:"8000",  hint:"Gateway port (restart required)" },
    { key:"rate_limit",   label:"Rate limit / min", placeholder:"60",    hint:"Max requests per minute per API key" },
    { key:"cors_origins", label:"CORS origins",     placeholder:"*",     hint:"Comma-separated origins or * for all" },
    { key:"log_level",    label:"Log level",        placeholder:"info",  hint:"debug / info / warning / error" },
  ];

  return (
    <div style={{ padding:24, height:"calc(100vh - 101px)", overflowY:"auto" }}>
      <div style={{ maxWidth:520 }}>
        <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:4 }}>Settings</div>
        <div style={{ fontSize:13, color:COLORS.textMuted, marginBottom:24 }}>Configure gateway — saved to .env automatically.</div>

        <div className="card" style={{ padding:24 }}>
          <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
            {fields.map(f => (
              <div key={f.key}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"baseline", marginBottom:5 }}>
                  <div style={{ fontSize:11, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em" }}>{f.label}</div>
                  <div style={{ fontSize:10, color:COLORS.textDim }}>{f.hint}</div>
                </div>
                <input className="input" placeholder={f.placeholder} value={form[f.key]}
                  onChange={e=>setForm(p=>({...p,[f.key]:e.target.value}))} />
              </div>
            ))}

            <div style={{ borderTop:`1px solid ${COLORS.border}`, paddingTop:16, display:"flex", gap:10 }}>
              <button className="btn btn-primary" onClick={save} disabled={loading}
                style={{ flex:2, justifyContent:"center", padding:"10px" }}>
                {loading ? <><div className="spinner"/> Saving...</> : "Save Settings →"}
              </button>
              <button className="btn btn-ghost" onClick={restart} disabled={loading}
                style={{ flex:1, justifyContent:"center", padding:"10px", color:COLORS.warning, borderColor:COLORS.warning }}>
                {loading ? <><div className="spinner"/> ...</> : "↺ Restart"}
              </button>
            </div>
          </div>
        </div>

        <div style={{ marginTop:14, padding:"10px 14px", background:COLORS.surface, borderRadius:8, border:`1px solid ${COLORS.border}` }}>
          <div style={{ fontSize:11, color:COLORS.textMuted, lineHeight:1.7 }}>
            ⚠️ Changing the <span style={{color:"#a5b4fc",fontFamily:"JetBrains Mono,monospace"}}>PORT</span> requires restarting the gateway to take effect.
          </div>
        </div>
      </div>
    </div>
  );
}


// ── Server Details Panel ───────────────────────────────────────────────────────
function ServerDetails({ server, apiKey, health = {}, notify = ()=>{} }) {
  const [logs, setLogs]       = useState([]);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/v1/logs?limit=200`, { headers: { "X-API-Key": apiKey } })
      .then(r => r.ok ? r.json() : [])
      .then(all => setLogs(all.filter(l => l.server === server.name)))
      .catch(() => {});
  }, [server.name]);

  const testConnection = async () => {
    setTesting(true); setTestResult(null);
    try {
      const r = await fetch(`${server.url}/health`, { signal: AbortSignal.timeout(3000) });
      setTestResult({ ok: true, status: r.status });
      notify("success", `${server.name} is online ✅`, `Responded with ${r.status}`);
    } catch (e) {
      setTestResult({ ok: false, error: e.message });
      notify("error", `${server.name} is offline`, e.message);
    }
    setTesting(false);
  };

  const todayLogs = logs.filter(l => new Date(l.timestamp).toDateString() === new Date().toDateString());
  const okCount   = todayLogs.filter(l => l.success).length;
  const errCount  = todayLogs.filter(l => !l.success).length;
  const lastErr   = logs.filter(l => !l.success)[0];

  return (
    <div className="card fade-in" style={{ padding:24 }}>
      {/* Header */}
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:20 }}>
        <div style={{ width:8, height:8, borderRadius:"50%", flexShrink:0,
          background: health[server.name]===true?COLORS.success:health[server.name]===false?COLORS.danger:COLORS.textDim }} />
        <div style={{ fontSize:18, fontWeight:700 }}>{server.name}</div>
        <span className="badge badge-blue">{server.transport}</span>
        <span style={{ fontSize:11, color:COLORS.textMuted, fontFamily:"JetBrains Mono, monospace", marginLeft:"auto" }}>{server.url}</span>
      </div>

      {/* Stats */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:10, marginBottom:16 }}>
        {[
          { label:"Calls today", value:todayLogs.length, color:COLORS.accent },
          { label:"Successful",  value:okCount,           color:COLORS.success },
          { label:"Failed",      value:errCount,          color:COLORS.danger },
        ].map(s => (
          <div key={s.label} style={{ background:COLORS.bg, border:`1px solid ${COLORS.border}`, borderRadius:8, padding:"10px 14px" }}>
            <div style={{ fontSize:20, fontWeight:800, color:s.color }}>{s.value}</div>
            <div style={{ fontSize:11, color:COLORS.textMuted, marginTop:1 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Tools */}
      <div style={{ marginBottom:16 }}>
        <div style={{ fontSize:11, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:8 }}>Tools ({server.tools.length})</div>
        <div style={{ display:"flex", flexWrap:"wrap", gap:5 }}>
          {server.tools.map(t => <span key={t} className="tag">{t}</span>)}
        </div>
      </div>

      {/* Last error */}
      {lastErr && (
        <div style={{ marginBottom:16, padding:"10px 12px", background:"rgba(239,68,68,0.06)", border:"1px solid rgba(239,68,68,0.2)", borderRadius:8 }}>
          <div style={{ fontSize:10, color:COLORS.danger, fontWeight:700, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:4 }}>Last error</div>
          <div style={{ fontSize:11, color:COLORS.textMuted, fontFamily:"JetBrains Mono, monospace" }}>
            {lastErr.tool} — {String(lastErr.error).slice(0,120)}
          </div>
          <div style={{ fontSize:10, color:COLORS.textDim, marginTop:4 }}>{lastErr.timestamp ? new Date(lastErr.timestamp).toLocaleString() : ""}</div>
        </div>
      )}

      {/* Test connection */}
      <div style={{ display:"flex", alignItems:"center", gap:10 }}>
        <button className="btn btn-ghost" onClick={testConnection} disabled={testing}
          style={{ fontSize:12 }}>
          {testing ? <><div className="spinner"/> Testing...</> : "⚡ Test connection"}
        </button>
        {testResult && (
          <span style={{ fontSize:11, color:testResult.ok?COLORS.success:COLORS.danger, fontFamily:"JetBrains Mono, monospace" }}>
            {testResult.ok ? `✓ Online (${testResult.status})` : `✗ ${testResult.error}`}
          </span>
        )}
      </div>
    </div>
  );
}


// ── Export Logs ────────────────────────────────────────────────────────────────
function exportLogsCSV(logs) {
  if (!logs.length) return;
  const headers = ["timestamp","server","tool","success","api_key","error"];
  const rows = logs.map(l =>
    headers.map(h => {
      const v = l[h] ?? "";
      return `"${String(v).replace(/"/g,'""')}"`;
    }).join(",")
  );
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type:"text/csv" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url; a.download = `mcp-gateway-logs-${new Date().toISOString().slice(0,10)}.csv`;
  a.click(); URL.revokeObjectURL(url);
}

// ── Keys Tab ───────────────────────────────────────────────────────────────────
function KeysTab({ apiKey, notify = ()=>{} }) {
  const [keys, setKeys]       = useState([]);
  const [newKey, setNewKey]   = useState("");
  const [newName, setNewName] = useState("");
  const [showKeys, setShowKeys] = useState({});

  const loadKeys = () => {
    const stored = localStorage.getItem("mcp_keys");
    if (stored) {
      try { setKeys(JSON.parse(stored)); } catch {}
    } else {
      // Init with current key
      const initial = [{ id: 1, name: "Default", key: apiKey, created: new Date().toISOString() }];
      setKeys(initial);
      localStorage.setItem("mcp_keys", JSON.stringify(initial));
    }
  };

  useEffect(() => { loadKeys(); }, []);

  const generateKey = () => {
    const arr = new Uint8Array(24);
    crypto.getRandomValues(arr);
    setNewKey(Array.from(arr).map(b=>b.toString(16).padStart(2,"0")).join(""));
  };

  const addKey = () => {
    if (!newKey.trim() || !newName.trim()) return;
    const updated = [...keys, { id: Date.now(), name: newName, key: newKey, created: new Date().toISOString() }];
    setKeys(updated);
    localStorage.setItem("mcp_keys", JSON.stringify(updated));
    setNewKey(""); setNewName("");
    notify("success", "Key added", `"${newName}" added to key store`);
  };

  const removeKey = (id) => {
    const updated = keys.filter(k => k.id !== id);
    setKeys(updated);
    localStorage.setItem("mcp_keys", JSON.stringify(updated));
    notify("info", "Key removed", "Key deleted from local store");
  };

  const copyKey = (k) => {
    navigator.clipboard.writeText(k.key).catch(()=>{});
    notify("success", "Copied!", `"${k.name}" key copied to clipboard`);
  };

  return (
    <div style={{ padding:24, height:"calc(100vh - 101px)", overflowY:"auto" }}>
      <div style={{ maxWidth:600 }}>
        <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:4 }}>API Keys</div>
        <div style={{ fontSize:13, color:COLORS.textMuted, marginBottom:24 }}>Manage API keys for accessing your gateway.</div>

        {/* Existing keys */}
        <div style={{ display:"flex", flexDirection:"column", gap:8, marginBottom:24 }}>
          {keys.map(k => (
            <div key={k.id} className="card" style={{ padding:"14px 16px" }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:10 }}>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:13, fontWeight:600, marginBottom:4 }}>{k.name}</div>
                  <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                    <span className="mono" style={{ fontSize:11, color:COLORS.textMuted, background:COLORS.bg, padding:"2px 8px", borderRadius:4, border:`1px solid ${COLORS.border}` }}>
                      {showKeys[k.id] ? k.key : k.key.slice(0,6)+"••••••••••••"+k.key.slice(-4)}
                    </span>
                    <button onClick={()=>setShowKeys(p=>({...p,[k.id]:!p[k.id]}))} style={{background:"transparent",border:"none",cursor:"pointer",color:COLORS.textMuted,fontSize:12,padding:0}}>
                      {showKeys[k.id]?"🙈":"👁"}
                    </button>
                  </div>
                  <div style={{ fontSize:10, color:COLORS.textDim, marginTop:4 }}>
                    Created: {new Date(k.created).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ display:"flex", gap:6, flexShrink:0 }}>
                  <button className="btn btn-ghost" onClick={()=>copyKey(k)} style={{padding:"4px 10px",fontSize:11}}>Copy</button>
                  {keys.length > 1 && (
                    <button className="btn btn-danger" onClick={()=>removeKey(k.id)} style={{padding:"4px 10px",fontSize:11}}>×</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Add new key */}
        <div className="card" style={{ padding:20 }}>
          <div style={{ fontSize:12, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:14 }}>Add New Key</div>
          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            <div>
              <div style={{ fontSize:10, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:4 }}>Name</div>
              <input className="input" placeholder="e.g. Team A, CI/CD, John" value={newName} onChange={e=>setNewName(e.target.value)} />
            </div>
            <div>
              <div style={{ fontSize:10, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:4 }}>API Key</div>
              <div style={{ display:"flex", gap:8 }}>
                <input className="input" placeholder="Paste or generate..." value={newKey} onChange={e=>setNewKey(e.target.value)} style={{flex:1}} />
                <button className="btn btn-ghost" onClick={generateKey} style={{whiteSpace:"nowrap",fontSize:11}}>Generate</button>
              </div>
            </div>
            <button className="btn btn-primary" onClick={addKey} disabled={!newKey.trim()||!newName.trim()} style={{width:"100%",justifyContent:"center",padding:"10px"}}>
              Add Key →
            </button>
          </div>
        </div>

        <div style={{ marginTop:14, padding:"10px 14px", background:COLORS.surface, borderRadius:8, border:`1px solid ${COLORS.border}` }}>
          <div style={{ fontSize:11, color:COLORS.textMuted, lineHeight:1.7 }}>
            💡 Keys are stored locally. To activate a new key on the gateway — add it to <span style={{color:"#a5b4fc",fontFamily:"JetBrains Mono,monospace"}}>MCP_API_KEYS</span> in your <span style={{color:"#a5b4fc",fontFamily:"JetBrains Mono,monospace"}}>.env</span> (comma-separated).
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Logs Tab ───────────────────────────────────────────────────────────────────
function LogsTab({ apiKey, t = T.en }) {
  const [statusFilter, setStatusFilter] = useState("all"); // all | ok | err
  const [logs, setLogs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState("");
  const ref = useRef(null);

  const fetchLogs = async () => {
    try {
      const r = await fetch(`${API_BASE}/v1/logs`, { headers: { "X-API-Key": apiKey } });
      if (r.ok) setLogs(await r.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchLogs(); const t = setInterval(fetchLogs, 5000); return () => clearInterval(t); }, []);
  useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [logs]);

  const filtered = logs.filter(l => {
    const matchText = !filter || l.server?.includes(filter) || l.tool?.includes(filter) || l.api_key?.includes(filter);
    const matchStatus = statusFilter === "all" || (statusFilter === "ok" && l.success) || (statusFilter === "err" && !l.success);
    return matchText && matchStatus;
  });

  const stats = {
    total: logs.length,
    ok: logs.filter(l => l.success).length,
    err: logs.filter(l => !l.success).length,
  };

  return (
    <div style={{ padding:24, height:"calc(100vh - 101px)", display:"flex", flexDirection:"column", gap:16, overflowY:"auto" }}>
      {/* Stats */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 }}>
        {[{label:t.totalCalls,value:stats.total,color:COLORS.accent},{label:t.successful,value:stats.ok,color:COLORS.success},{label:t.failed,value:stats.err,color:COLORS.danger}].map(s=>(
          <div key={s.label} className="card" style={{padding:"14px 18px"}}>
            <div style={{fontSize:26,fontWeight:800,color:s.color,letterSpacing:"-0.02em"}}>{s.value}</div>
            <div style={{fontSize:12,color:COLORS.textMuted,marginTop:2}}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filter + Refresh */}
      <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
        <input className="input" placeholder={t.filterPlaceholder} value={filter} onChange={e=>setFilter(e.target.value)} style={{flex:1,minWidth:180}} />
        {["all","ok","err"].map(s=>(
          <button key={s} className={`btn ${statusFilter===s?"btn-primary":"btn-ghost"}`}
            onClick={()=>setStatusFilter(s)}
            style={{padding:"6px 12px",fontSize:11}}>
            {s==="all"?"All":s==="ok"?"✅ OK":"❌ Err"}
          </button>
        ))}
        <button className="btn btn-ghost" onClick={fetchLogs} style={{whiteSpace:"nowrap"}}>{t.refresh}</button>
        <button className="btn btn-ghost" onClick={()=>exportLogsCSV(filtered)} style={{whiteSpace:"nowrap",fontSize:11}}>⬇ CSV</button>
      </div>

      {/* Log list */}
      <div className="card" style={{flex:1,padding:16,overflowY:"auto",minHeight:0}} ref={ref}>
        <div style={{fontSize:11,fontWeight:700,color:COLORS.textMuted,textTransform:"uppercase",letterSpacing:"0.06em",marginBottom:12}}>
          {t.auditLog} {loading && <span style={{color:COLORS.textDim}}>— {t.loading}</span>}
        </div>
        {filtered.length === 0 && !loading && (
          <div style={{color:COLORS.textDim,fontSize:12,fontFamily:"JetBrains Mono, monospace",padding:"20px 0"}}>{t.noLogs}</div>
        )}
        {[...filtered].reverse().map((l,i) => (
          <div key={i} className={`log-entry ${l.success?"log-ok":"log-err"}`}>
            <span style={{color:COLORS.textMuted}}>{l.timestamp ? new Date(l.timestamp).toLocaleTimeString() : "—"} </span>
            <span style={{color:l.success?COLORS.success:COLORS.danger}}>{l.success?"OK":"ERR"} </span>
            <span style={{color:COLORS.text}}>{l.server}</span>
            <span style={{color:COLORS.textMuted}}>/</span>
            <span style={{color:"#a5b4fc"}}>{l.tool}</span>
            {l.api_key && <span style={{color:COLORS.textDim}}> [{l.api_key.slice(0,8)}...]</span>}
            {l.error && <span style={{color:COLORS.danger}}> — {String(l.error).slice(0,80)}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Custom Server Builder ──────────────────────────────────────────────────────
function CustomTab({ apiKey, onAdded, t = T.en }) {
  const [form, setForm] = useState({
    name:"", description:"", url:"http://localhost:8001",
    tools:"", transport:"http", start_command:""
  });
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");
  const [success, setSuccess]     = useState("");
  const [serverStatus, setServerStatus] = useState(null);

  const submit = async () => {
    if (!form.name||!form.url||!form.tools) { setError("Name, URL, and tools are required"); return; }
    setLoading(true); setError(""); setSuccess(""); setServerStatus(null);
    try {
      // 1. Add to registry
      const r = await fetch(`${API_BASE}/v1/servers`, {
        method: "POST",
        headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, tools: form.tools.split(",").map(t=>t.trim()).filter(Boolean) })
      });
      if (!r.ok) {
        const d = await r.json();
        setError(d.detail || "Failed to add server");
        setLoading(false); return;
      }

      // 2. If start_command provided — start the server
      if (form.start_command.trim()) {
        const r2 = await fetch(`${API_BASE}/v1/start-process`, {
          method: "POST",
          headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
          body: JSON.stringify({ name: form.name, command: form.start_command.trim() })
        });
        const d2 = await r2.json();
        if (r2.ok && d2.started) {
          setServerStatus("ok");
          setSuccess(`Server "${form.name}" added and started ✓`);
        } else {
          setServerStatus("error");
          setSuccess(`Server "${form.name}" added to registry — but failed to start: ${d2.message||""}`);
        }
      } else {
        setSuccess(`Server "${form.name}" added to registry ✓`);
      }

      setForm({ name:"", description:"", url:"http://localhost:8001", tools:"", transport:"http", start_command:"" });
      onAdded();
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  const fields = [
    { key:"name",          label:"Server name",             placeholder:"my-server" },
    { key:"description",   label:"Description",             placeholder:"What does this server do?" },
    { key:"url",           label:"Server URL",              placeholder:"http://localhost:8001" },
    { key:"tools",         label:"Tools (comma-separated)", placeholder:"tool_one, tool_two, tool_three" },
  ];

  return (
    <div style={{ padding:24, height:"calc(100vh - 101px)", overflowY:"auto" }}>
      <div style={{ maxWidth:560 }}>
        <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:4 }}>Custom MCP Server</div>
        <div style={{ fontSize:13, color:COLORS.textMuted, marginBottom:24 }}>Register any MCP server and optionally start it automatically.</div>

        <div className="card" style={{ padding:24 }}>
          <div style={{ display:"flex", flexDirection:"column", gap:14 }}>

            {fields.map(f => (
              <div key={f.key}>
                <div style={{ fontSize:11, color:COLORS.textMuted, marginBottom:5, textTransform:"uppercase", letterSpacing:"0.06em" }}>{f.label}</div>
                <input className="input" placeholder={f.placeholder} value={form[f.key]} onChange={e=>setForm(p=>({...p,[f.key]:e.target.value}))} />
              </div>
            ))}

            <div>
              <div style={{ fontSize:11, color:COLORS.textMuted, marginBottom:5, textTransform:"uppercase", letterSpacing:"0.06em" }}>Transport</div>
              <select className="input" value={form.transport} onChange={e=>setForm(p=>({...p,transport:e.target.value}))}>
                <option value="http">http</option>
                <option value="sse">sse</option>
              </select>
            </div>

            <div>
              <div style={{ fontSize:11, color:COLORS.textMuted, marginBottom:5, textTransform:"uppercase", letterSpacing:"0.06em" }}>
                Start command <span style={{color:COLORS.textDim, textTransform:"none", letterSpacing:0}}>(optional — auto-starts server)</span>
              </div>
              <input className="input" placeholder="python templates/qa/my_server.py"
                value={form.start_command}
                onChange={e=>setForm(p=>({...p,start_command:e.target.value}))} />
            </div>

            {serverStatus && (
              <div style={{ display:"flex", alignItems:"center", gap:8, padding:"8px 12px",
                background: serverStatus==="ok"?"rgba(34,197,94,0.06)":"rgba(245,158,11,0.06)",
                border:`1px solid ${serverStatus==="ok"?"rgba(34,197,94,0.2)":"rgba(245,158,11,0.2)"}`,
                borderRadius:6 }}>
                <div style={{ width:6, height:6, borderRadius:"50%", flexShrink:0,
                  background: serverStatus==="ok"?COLORS.success:COLORS.warning }}/>
                <span style={{ fontSize:11, color: serverStatus==="ok"?COLORS.success:COLORS.warning }}>
                  {serverStatus==="ok" ? "Server started" : "Added to registry — start it manually"}
                </span>
              </div>
            )}

            {error   && <div style={{ fontSize:12, color:COLORS.danger,  padding:"8px 12px", background:"rgba(239,68,68,0.08)",  borderRadius:6 }}>{error}</div>}
            {success && <div style={{ fontSize:12, color:COLORS.success, padding:"8px 12px", background:"rgba(34,197,94,0.08)",  borderRadius:6 }}>{success}</div>}

            <button className="btn btn-primary" onClick={submit} disabled={loading} style={{ width:"100%", justifyContent:"center", padding:"11px" }}>
              {loading ? <><div className="spinner"/> {form.start_command?"Starting...":"Adding..."}</> : form.start_command ? "Add & Start Server →" : "Add to Registry →"}
            </button>
          </div>
        </div>

        <div style={{ marginTop:16, padding:"14px 16px", background:COLORS.surface, borderRadius:8, border:`1px solid ${COLORS.border}` }}>
          <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:8 }}>How it works</div>
          <div style={{ fontSize:12, color:COLORS.textMuted, lineHeight:1.8, fontFamily:"JetBrains Mono, monospace" }}>
            Server URL: <span style={{color:"#a5b4fc"}}>POST /call</span> → <span style={{color:"#a5b4fc"}}>{"{ tool, arguments }"}</span><br/>
            Start command runs in background automatically.<br/>
            Leave blank if your server is already running.
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Servers Panel ──────────────────────────────────────────────────────────────
function ServersPanel({ servers, selected, onSelect, health = {} }) {
  const categories = {
    qa: servers.filter(s => ["jira","testrail","pytest-runner","xray","zephyr","allure-reporter","bdd-generator","selenium"].includes(s.name)),
    dev: servers.filter(s => ["github","git-local","azure-devops","code-runner"].includes(s.name)),
    general: servers.filter(s => !["jira","testrail","pytest-runner","xray","zephyr","github","git-local","azure-devops","code-runner","selenium","allure-reporter"].includes(s.name)),
  };
  return (
    <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
      {Object.entries(categories).map(([cat, list]) =>
        list.length > 0 && (
          <div key={cat}>
            <div style={{ fontSize:10, fontWeight:700, color:CAT_COLORS[cat], letterSpacing:"0.1em", textTransform:"uppercase", padding:"8px 0 6px", fontFamily:"JetBrains Mono, monospace" }}>{CAT_LABELS[cat]}</div>
            {list.map(s => (
              <div key={s.name} onClick={()=>onSelect(s)} className="card"
                style={{ padding:"10px 14px", marginBottom:4, cursor:"pointer", borderColor:selected?.name===s.name?COLORS.accent:COLORS.border, background:selected?.name===s.name?COLORS.accentGlow:COLORS.surface }}>
                <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
                  <div style={{display:"flex",alignItems:"center",gap:6}}>
                    <div style={{width:6,height:6,borderRadius:"50%",flexShrink:0,background:health[s.name]===true?COLORS.success:health[s.name]===false?COLORS.danger:COLORS.textDim}} title={health[s.name]===true?"Online":health[s.name]===false?"Offline":"Unknown"}/>
                    <span style={{fontSize:13,fontWeight:600}}>{s.name}</span>
                  </div>
                  <span style={{fontSize:10,color:COLORS.textMuted,fontFamily:"JetBrains Mono, monospace"}}>{s.tools.length} tools</span>
                </div>
                <div style={{fontSize:11,color:COLORS.textMuted,marginTop:2,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{s.description}</div>
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
  const [tool, setTool]       = useState(server.tools[0] || "");
  const [args, setArgs]       = useState("{}");
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  useEffect(() => { setTool(server.tools[0]||""); setArgs("{}"); setResult(null); setError(""); }, [server]);

  const run = async () => {
    let parsed;
    try { parsed = JSON.parse(args); } catch { setError("Invalid JSON in arguments"); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await fetch(`${API_BASE}/v1/call`, { method:"POST", headers:{"X-API-Key":apiKey,"Content-Type":"application/json"}, body:JSON.stringify({server:server.name,tool,arguments:parsed}) });
      const data = await r.json();
      setResult(data);
      onLog({ ts:new Date().toISOString(), server:server.name, tool, success:data.success, error:data.error });
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  return (
    <div className="card fade-in" style={{padding:24}}>
      <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:20}}>
        <div style={{fontSize:16,fontWeight:700}}>{server.name}</div>
        <span className="badge badge-blue">{server.transport}</span>
        <span style={{fontSize:11,color:COLORS.textMuted,fontFamily:"JetBrains Mono, monospace",marginLeft:"auto"}}>{server.url}</span>
      </div>
      <div style={{marginBottom:16}}>
        <div style={{fontSize:11,color:COLORS.textMuted,marginBottom:8,textTransform:"uppercase",letterSpacing:"0.06em"}}>Tool</div>
        <div style={{display:"flex",flexWrap:"wrap",gap:6}}>{server.tools.map(t=><span key={t} className={`tag ${tool===t?"active":""}`} onClick={()=>setTool(t)}>{t}</span>)}</div>
      </div>
      <div style={{marginBottom:16}}>
        <div style={{fontSize:11,color:COLORS.textMuted,marginBottom:6,textTransform:"uppercase",letterSpacing:"0.06em"}}>Arguments (JSON)</div>
        <textarea className="input" rows={4} value={args} onChange={e=>setArgs(e.target.value)} placeholder='{"key": "value"}' style={{resize:"vertical"}} />
      </div>
      {error && <div style={{fontSize:12,color:COLORS.danger,padding:"8px 12px",background:"rgba(239,68,68,0.08)",borderRadius:6,marginBottom:12,fontFamily:"JetBrains Mono, monospace"}}>{error}</div>}
      <button className="btn btn-primary" onClick={run} disabled={loading} style={{marginBottom:result?16:0}}>
        {loading ? <><div className="spinner"/> Running...</> : "▶ Run Tool"}
      </button>
      {result && (
        <div style={{marginTop:16}}>
          <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
            <span className={`badge ${result.success?"badge-green":"badge-red"}`}>{result.success?"SUCCESS":"ERROR"}</span>
            <span style={{fontSize:11,color:COLORS.textMuted,fontFamily:"JetBrains Mono, monospace"}}>{server.name} / {tool}</span>
          </div>
          <pre style={{background:COLORS.bg,border:`1px solid ${COLORS.border}`,borderRadius:8,padding:16,fontSize:11,fontFamily:"JetBrains Mono, monospace",color:result.success?COLORS.success:COLORS.danger,overflowX:"auto",maxHeight:300,whiteSpace:"pre-wrap",wordBreak:"break-all"}}>
            {JSON.stringify(result.success?result.result:result.error,null,2)}
          </pre>
        </div>
      )}
    </div>
  );
}

// ── Add Server Modal ───────────────────────────────────────────────────────────
function AddServerModal({ apiKey, onClose, onAdded }) {
  const [form, setForm]       = useState({ name:"", description:"", url:"http://localhost:8001", tools:"", transport:"http" });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const submit = async () => {
    if (!form.name||!form.url||!form.tools) { setError("Name, URL, and tools are required"); return; }
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { method:"POST", headers:{"X-API-Key":apiKey,"Content-Type":"application/json"}, body:JSON.stringify({...form,tools:form.tools.split(",").map(t=>t.trim()).filter(Boolean)}) });
      if (r.ok) { onAdded(); onClose(); }
      else { const d = await r.json(); setError(d.detail||"Failed"); }
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  return (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.7)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:100,padding:24}}>
      <div className="card fade-in" style={{width:"100%",maxWidth:480,padding:32}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:24}}>
          <div style={{fontSize:16,fontWeight:700}}>Add Server to Registry</div>
          <button className="btn btn-ghost" onClick={onClose} style={{padding:"4px 10px"}}>✕</button>
        </div>
        <div style={{display:"flex",flexDirection:"column",gap:12}}>
          {[{key:"name",label:"Server name",placeholder:"my-tool"},{key:"description",label:"Description",placeholder:"What does it do?"},{key:"url",label:"URL",placeholder:"http://localhost:8001"},{key:"tools",label:"Tools (comma separated)",placeholder:"tool1, tool2, tool3"}].map(f=>(
            <div key={f.key}>
              <div style={{fontSize:11,color:COLORS.textMuted,marginBottom:5,textTransform:"uppercase",letterSpacing:"0.06em"}}>{f.label}</div>
              <input className="input" placeholder={f.placeholder} value={form[f.key]} onChange={e=>setForm(p=>({...p,[f.key]:e.target.value}))} />
            </div>
          ))}
          {error && <div style={{fontSize:12,color:COLORS.danger,padding:"8px 12px",background:"rgba(239,68,68,0.08)",borderRadius:6}}>{error}</div>}
          <div style={{display:"flex",gap:8,marginTop:8}}>
            <button className="btn btn-ghost" onClick={onClose} style={{flex:1,justifyContent:"center"}}>Cancel</button>
            <button className="btn btn-primary" onClick={submit} disabled={loading} style={{flex:2,justifyContent:"center"}}>
              {loading ? <div className="spinner"/> : "Add to Registry"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Logs Panel (dashboard inline) ─────────────────────────────────────────────
function LogsPanel({ logs }) {
  const ref = useRef(null);
  useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [logs]);
  return (
    <div className="card" style={{padding:20,height:280}}>
      <div style={{fontSize:12,fontWeight:700,color:COLORS.textMuted,letterSpacing:"0.06em",textTransform:"uppercase",marginBottom:12}}>
        Audit Log <span style={{color:COLORS.textDim,fontWeight:400}}>— live</span>
      </div>
      <div ref={ref} style={{height:220,overflowY:"auto"}}>
        {logs.length===0 && <div style={{color:COLORS.textDim,fontSize:12,fontFamily:"JetBrains Mono, monospace",padding:"20px 0"}}>No calls yet — run a tool to see logs here.</div>}
        {logs.map((l,i)=>(
          <div key={i} className={`log-entry ${l.success?"log-ok":"log-err"}`}>
            <span style={{color:COLORS.textMuted}}>{new Date(l.ts).toLocaleTimeString()} </span>
            <span style={{color:l.success?COLORS.success:COLORS.danger}}>{l.success?"OK":"ERR"} </span>
            <span style={{color:COLORS.text}}>{l.server}</span>
            <span style={{color:COLORS.textMuted}}>/</span>
            <span style={{color:"#a5b4fc"}}>{l.tool}</span>
            {l.error && <span style={{color:COLORS.danger}}> — {l.error}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────────────────
export default function App() {
  const [apiKey, setApiKey]         = useState("");
  const [authed, setAuthed]         = useState(false);
  const [servers, setServers]       = useState([]);
  const [selected, setSelected]     = useState(null);
  const [status, setStatus]         = useState(null);
  const [logs, setLogs]             = useState([]);
  const [showAdd, setShowAdd]       = useState(false);
  const [stats, setStats]           = useState({ total: 0, ok: 0, err: 0, running: 0 });
  const [notifs, setNotifs]         = useState([]);
  const [serverHealth, setServerHealth] = useState({});

  const notify = (type, title, message, duration=4000) => {
    const id = Date.now() + Math.random();
    setNotifs(p => [...p.slice(-4), { id, type, title, message }]);
    setTimeout(() => setNotifs(p => p.filter(n => n.id !== id)), duration);
  };

  const checkServerHealth = async () => {
    try {
      const r = await fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": apiKey } });
      if (r.ok) {
        const srvs = await r.json();
        const health = {};
        await Promise.allSettled(srvs.map(async s => {
          try {
            const r2 = await fetch(s.url + "/health", { signal: AbortSignal.timeout(2000) });
            health[s.name] = r2.ok;
          } catch {
            health[s.name] = false;
          }
        }));
        setServerHealth(health);
      }
    } catch {}
  };

  const loadStats = async () => {
    try {
      const [logsRes, serversRes] = await Promise.all([
        fetch(`${API_BASE}/v1/logs?limit=1000`, { headers: { "X-API-Key": apiKey } }),
        fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": apiKey } }),
      ]);
      if (logsRes.ok) {
        const logs = await logsRes.json();
        const today = new Date().toDateString();
        const todayLogs = logs.filter(l => new Date(l.timestamp).toDateString() === today);
        setStats(s => ({
          ...s,
          total: todayLogs.length,
          ok: todayLogs.filter(l => l.success).length,
          err: todayLogs.filter(l => !l.success).length,
        }));
      }
      if (serversRes.ok) {
        const srvs = await serversRes.json();
        setStats(s => ({ ...s, running: srvs.length }));
      }
    } catch {}
  };
  const [activeTab, setActiveTab]   = useState("setup");
  const [lang, setLang]             = useState(() => localStorage.getItem("mcp_lang") || null);
  const [splashDone, setSplashDone] = useState(false);
  const [dark, setDark]             = useState(() => localStorage.getItem("mcp_theme") !== "light");

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    localStorage.setItem("mcp_theme", next ? "dark" : "light");
  };

  // Dynamic colors based on theme
  const C = dark ? {
    bg: "#0a0a0f", surface: "#13131a", border: "#1e1e2e", borderHover: "#2e2e4e",
    text: "#e2e8f0", textMuted: "#64748b", textDim: "#334155",
  } : {
    bg: "#f8fafc", surface: "#ffffff", border: "#e2e8f0", borderHover: "#cbd5e1",
    text: "#0f172a", textMuted: "#64748b", textDim: "#94a3b8",
  };

  const t = T[lang] || T.en;
  const isRtl = lang === "ar";

  const selectLang = (code) => { localStorage.setItem("mcp_lang", code); setLang(code); };

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

  useEffect(() => {
    if (authed) {
      loadServers();
      loadStatus();
      loadStats();
      const t = setInterval(loadStats, 10000);
      const t2 = setInterval(checkServerHealth, 15000);
      checkServerHealth();
      return () => { clearInterval(t); clearInterval(t2); };
    }
  }, [authed]);

  useEffect(() => {
    const tryConnect = async () => {
      // 1. try stored key
      const stored = localStorage.getItem("mcp_key");
      if (stored) {
        try {
          const r = await fetch(`${API_BASE}/v1/servers`, { headers: { "X-API-Key": stored } });
          if (r.ok) { setApiKey(stored); setAuthed(true); return; }
        } catch {}
      }
      // 2. try auto-key from gateway
      try {
        const r = await fetch(`${API_BASE}/v1/auto-key`);
        if (r.ok) {
          const d = await r.json();
          if (d.key) {
            localStorage.setItem("mcp_key", d.key);
            setApiKey(d.key);
            setAuthed(true);
            return;
          }
        }
      } catch {}
      // 3. fallback — show auth screen
      setAuthed(false);
    };
    tryConnect();
  }, []);

  if (!splashDone) return (<><style>{css}</style><SplashScreen onDone={() => setSplashDone(true)} /></>);
  if (!lang) return (<><style>{css}</style><LanguageScreen onSelect={selectLang} /></>);
  if (!authed) return (<><style>{css}</style><AuthScreen onAuth={auth} t={t} /></>);

  return (
    <>
      <style>{css}</style>
      <div className={dark?"theme-dark":"theme-light"} style={{ minHeight:"100vh", display:"flex", flexDirection:"column", direction: isRtl?"rtl":"ltr", background: dark?"#0a0a0f":"#f8fafc", color: dark?"#e2e8f0":"#0f172a" }}>
        <StatusBar apiKey={apiKey} status={status} dark={dark} onChangeLang={()=>{localStorage.removeItem("mcp_lang");setLang(null);}} />

        <div className="nav-tab-bar" style={{direction: isRtl?"rtl":"ltr"}}>
          <div className={`nav-tab ${activeTab==="setup"?"active":""}`}     onClick={()=>setActiveTab("setup")}>{t.quickSetup}</div>
          <div className={`nav-tab ${activeTab==="dashboard"?"active":""}`} onClick={()=>setActiveTab("dashboard")}>{t.dashboard}</div>
          <div className={`nav-tab ${activeTab==="logs"?"active":""}`}      onClick={()=>setActiveTab("logs")}>{t.logs}</div>
          <div className={`nav-tab ${activeTab==="custom"?"active":""}`}    onClick={()=>setActiveTab("custom")}>{t.customTab}</div>
          <div className={`nav-tab ${activeTab==="keys"?"active":""}`}      onClick={()=>setActiveTab("keys")}>🔑 Keys</div>
          <div className={`nav-tab ${activeTab==="settings"?"active":""}`}  onClick={()=>setActiveTab("settings")}>⚙️ Settings</div>
          <div className="nav-tab" onClick={()=>{localStorage.removeItem("mcp_lang");setLang(null);}} style={{marginLeft:"auto",fontSize:13}}>🌐</div>
          <div className="nav-tab" onClick={toggleTheme} style={{fontSize:13}} title="Toggle theme">{dark ? "☀️" : "🌙"}</div>
        </div>

        <div style={{display: activeTab==="setup"?"block":"none"}}><QuickSetup apiKey={apiKey} t={t} isRtl={isRtl} notify={notify} /></div>
        <div style={{display: activeTab==="logs"?"block":"none"}}><LogsTab apiKey={apiKey} t={t} /></div>
        <div style={{display: activeTab==="custom"?"block":"none"}}><CustomTab apiKey={apiKey} onAdded={loadServers} t={t} notify={notify} /></div>
        <div style={{display: activeTab==="keys"?"block":"none"}}><KeysTab apiKey={apiKey} notify={notify} /></div>
        <div style={{display: activeTab==="settings"?"block":"none"}}><SettingsTab apiKey={apiKey} notify={notify} /></div>

        {activeTab === "dashboard" && (
          <div style={{ display:"grid", gridTemplateColumns:"260px 1fr", flex:1 }}>
            <div style={{ borderRight:`1px solid ${COLORS.border}`, padding:16, overflowY:"auto", height:"calc(100vh - 101px)" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
                <div style={{ fontSize:11, fontWeight:700, color:COLORS.textMuted, textTransform:"uppercase", letterSpacing:"0.08em" }}>{t.servers} ({servers.length})</div>
                <button className="btn btn-ghost" onClick={()=>setShowAdd(true)} style={{padding:"3px 8px",fontSize:11}}>{t.addServer}</button>
              </div>
              <ServersPanel servers={servers} selected={selected} onSelect={setSelected} health={serverHealth} />
            </div>
            <div style={{ padding:24, overflowY:"auto", height:"calc(100vh - 101px)", display:"flex", flexDirection:"column", gap:20 }}>
              {status && (
                <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 }}>
                  {[{label:t.servers,value:stats.running||status.servers_registered,color:COLORS.accent},{label:t.healthy,value:status.servers_healthy,color:COLORS.success},{label:t.callsToday,value:stats.total,color:COLORS.warning}].map(s=>(
                    <div key={s.label} className="card" style={{padding:"16px 20px"}}>
                      <div style={{fontSize:28,fontWeight:800,color:s.color,letterSpacing:"-0.02em"}}>{s.value}</div>
                      <div style={{fontSize:12,color:COLORS.textMuted,marginTop:2}}>{s.label}</div>
                    </div>
                  ))}
                </div>
              )}
              {selected ? (
                <>
                  <ServerDetails server={selected} apiKey={apiKey} health={serverHealth} notify={notify} />
                  <ToolRunner server={selected} apiKey={apiKey} onLog={addLog} />
                </>
              ) : (
                <div className="card fade-in" style={{padding:40,textAlign:"center",color:COLORS.textMuted}}>
                  <div style={{fontSize:32,marginBottom:12}}>←</div>
                  <div style={{fontSize:14}}>{t.selectServer}</div>
                </div>
              )}
              <LogsPanel logs={logs} />
            </div>
          </div>
        )}
      </div>
      {showAdd && <AddServerModal apiKey={apiKey} onClose={()=>setShowAdd(false)} onAdded={loadServers} />}
      <NotificationContainer notifications={notifs} />
    </>
  );
}
