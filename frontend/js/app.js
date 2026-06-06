// Uses same origin when served from /ui/ on the API server; fallback for local file preview.
const API_BASE = window.location.protocol.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:8002";

const routes = {
  home: { title: "Dashboard", eyebrow: "Overview", auth: false },
  login: { title: "Sign In", eyebrow: "Authentication", auth: false },
  register: { title: "Create Account", eyebrow: "Authentication", auth: false },
  generate: { title: "Resume Generator", eyebrow: "AI Tools", auth: false },
  match: { title: "Job Match", eyebrow: "AI Tools", auth: false },
};

const navItems = [
  { id: "home", label: "Dashboard", icon: "⌂" },
  { id: "login", label: "Login", icon: "→" },
  { id: "register", label: "Register", icon: "+" },
  { id: "generate", label: "Resume Generator", icon: "✦" },
  { id: "match", label: "Job Match", icon: "%" },
];

const state = {
  token: localStorage.getItem("access_token"),
  email: localStorage.getItem("user_email"),
};

const contentEl = document.getElementById("app-content");
const navEl = document.getElementById("nav");
const alertEl = document.getElementById("global-alert");
const pageTitleEl = document.getElementById("page-title");
const pageEyebrowEl = document.getElementById("page-eyebrow");
const userEmailEl = document.getElementById("user-email");
const userChipEl = document.getElementById("user-chip");
const logoutBtn = document.getElementById("logout-btn");

function showAlert(message, type = "error") {
  alertEl.hidden = false;
  alertEl.className = `alert alert-${type}`;
  alertEl.textContent = message;
}

function clearAlert() {
  alertEl.hidden = true;
  alertEl.textContent = "";
}

function setAuth(auth) {
  state.token = auth.access_token;
  state.email = auth.user_email;
  localStorage.setItem("access_token", auth.access_token);
  localStorage.setItem("user_email", auth.user_email);
  updateChrome();
}

function clearAuth() {
  state.token = null;
  state.email = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_email");
  updateChrome();
}

function updateChrome() {
  userEmailEl.textContent = state.email || "Guest";
  userChipEl.classList.toggle("authenticated", Boolean(state.email));
  logoutBtn.hidden = !state.email;
}

async function apiRequest(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message = typeof detail === "string" ? detail : JSON.stringify(detail) || "Request failed";
    throw new Error(message);
  }

  return data;
}

function navigate(routeId) {
  window.location.hash = routeId;
}

function getRouteId() {
  const hash = window.location.hash.replace("#", "").trim();
  return routes[hash] ? hash : "home";
}

function renderNav() {
  const current = getRouteId();
  navEl.innerHTML = navItems
    .map(
      (item) => `
        <a href="#${item.id}" class="nav-link ${current === item.id ? "active" : ""}">
          <span>${item.icon}</span>
          <span>${item.label}</span>
        </a>
      `
    )
    .join("");
}

function renderHome() {
  contentEl.innerHTML = `
    <div class="hero-grid">
      <div class="feature-card">
        <h4>Authentication</h4>
        <p>Register and login to receive a JWT from the FastAPI backend.</p>
      </div>
      <div class="feature-card">
        <h4>Resume Generator</h4>
        <p>Turn free-form career notes into a structured resume with Groq AI.</p>
      </div>
      <div class="feature-card">
        <h4>Job Match</h4>
        <p>Compare a resume against a job description and get a similarity score.</p>
      </div>
    </div>
    <div class="card">
      <h3>Demo Flow</h3>
      <p>Start with Register, then try Resume Generator and Job Match. API docs are available from the top-right link.</p>
      <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
        <button class="btn btn-primary" data-go="register">Create account</button>
        <button class="btn btn-ghost" data-go="generate">Generate resume</button>
        <button class="btn btn-ghost" data-go="match">Match a job</button>
      </div>
    </div>
  `;

  contentEl.querySelectorAll("[data-go]").forEach((btn) => {
    btn.addEventListener("click", () => navigate(btn.dataset.go));
  });
}

function renderLogin() {
  contentEl.innerHTML = `
    <div class="card" style="max-width:520px;">
      <h3>Welcome back</h3>
      <p>Sign in with your registered email and password.</p>
      <form id="login-form">
        <div class="form-group">
          <label for="login-email">Email</label>
          <input id="login-email" type="email" required placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label for="login-password">Password</label>
          <input id="login-password" type="password" required minlength="6" placeholder="••••••••" />
        </div>
        <button class="btn btn-primary" type="submit">Sign in</button>
      </form>
    </div>
  `;

  document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlert();
    const button = event.target.querySelector("button");
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span>Signing in...';

    try {
      const payload = {
        email: document.getElementById("login-email").value.trim(),
        password: document.getElementById("login-password").value,
      };
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setAuth(data);
      showAlert(`Signed in as ${data.user_email}`, "success");
      navigate("home");
    } catch (error) {
      showAlert(error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Sign in";
    }
  });
}

function renderRegister() {
  contentEl.innerHTML = `
    <div class="card" style="max-width:520px;">
      <h3>Create your account</h3>
      <p>Register to get a JWT access token from the backend.</p>
      <form id="register-form">
        <div class="form-group">
          <label for="register-name">Full name</label>
          <input id="register-name" type="text" required minlength="2" maxlength="100" placeholder="Jane Doe" />
        </div>
        <div class="form-group">
          <label for="register-email">Email</label>
          <input id="register-email" type="email" required placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label for="register-password">Password</label>
          <input id="register-password" type="password" required minlength="6" maxlength="128" placeholder="At least 6 characters" />
        </div>
        <button class="btn btn-primary" type="submit">Create account</button>
      </form>
    </div>
  `;

  document.getElementById("register-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlert();
    const button = event.target.querySelector("button");
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span>Creating account...';

    try {
      const payload = {
        full_name: document.getElementById("register-name").value.trim(),
        email: document.getElementById("register-email").value.trim(),
        password: document.getElementById("register-password").value,
      };
      const data = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setAuth(data);
      showAlert(`Registration successful. Welcome, ${payload.full_name}!`, "success");
      navigate("generate");
    } catch (error) {
      showAlert(error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Create account";
    }
  });
}

function renderGenerate() {
  contentEl.innerHTML = `
    <div class="grid-2">
      <div class="card">
        <h3>Your background</h3>
        <p>Paste career notes, skills, and experience (minimum 20 characters).</p>
        <form id="generate-form">
          <div class="form-group">
            <label for="free-text">Free text</label>
            <textarea id="free-text" required minlength="20" placeholder="Example: Software engineer with 4 years of Python, FastAPI, MongoDB..."></textarea>
          </div>
          <button class="btn btn-primary" type="submit">Generate resume</button>
        </form>
      </div>
      <div class="card">
        <h3>Generated resume</h3>
        <p>AI output from POST /ai/generate-resume</p>
        <div class="result-box" id="generated-resume">Results will appear here.</div>
      </div>
    </div>
  `;

  document.getElementById("generate-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlert();
    const button = event.target.querySelector("button");
    const output = document.getElementById("generated-resume");
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span>Generating...';
    output.textContent = "Generating resume...";

    try {
      const data = await apiRequest("/ai/generate-resume", {
        method: "POST",
        body: JSON.stringify({ free_text: document.getElementById("free-text").value.trim() }),
      });
      output.textContent = data.generated_resume || "No resume returned.";
      localStorage.setItem("last_resume", data.generated_resume || "");
    } catch (error) {
      output.textContent = "Generation failed.";
      showAlert(error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Generate resume";
    }
  });
}

function renderMatch() {
  const savedResume = localStorage.getItem("last_resume") || "";

  contentEl.innerHTML = `
    <div class="card">
      <h3>Compare resume to job description</h3>
      <p>Uses POST /ai/match-job to return a similarity score and explanation.</p>
      <form id="match-form">
        <div class="grid-2">
          <div class="form-group">
            <label for="resume-text">Resume text</label>
            <textarea id="resume-text" required minlength="20"></textarea>
          </div>
          <div class="form-group">
            <label for="job-description">Job description</label>
            <textarea id="job-description" required minlength="20" placeholder="Paste the target job description here..."></textarea>
          </div>
        </div>
        <button class="btn btn-primary" type="submit">Analyze match</button>
      </form>
    </div>
    <div class="card" id="match-results" hidden>
      <div class="score-badge" id="match-score"></div>
      <h3>Explanation</h3>
      <div class="result-box" id="match-explanation"></div>
      <h3 style="margin-top:1rem;">Tailored resume</h3>
      <div class="result-box" id="tailored-resume"></div>
    </div>
  `;

  document.getElementById("resume-text").value = savedResume;

  document.getElementById("match-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlert();
    const button = event.target.querySelector("button");
    const results = document.getElementById("match-results");
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span>Analyzing...';

    try {
      const data = await apiRequest("/ai/match-job", {
        method: "POST",
        body: JSON.stringify({
          resume_text: document.getElementById("resume-text").value.trim(),
          job_description: document.getElementById("job-description").value.trim(),
        }),
      });

      results.hidden = false;
      document.getElementById("match-score").textContent = `Similarity score: ${data.similarity_score}%`;
      document.getElementById("match-explanation").textContent = data.explanation || "No explanation returned.";
      document.getElementById("tailored-resume").textContent = data.tailored_resume || "No tailored resume returned.";
    } catch (error) {
      showAlert(error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Analyze match";
    }
  });
}

function render() {
  const routeId = getRouteId();
  const route = routes[routeId];

  pageTitleEl.textContent = route.title;
  pageEyebrowEl.textContent = route.eyebrow;
  renderNav();
  clearAlert();

  switch (routeId) {
    case "login":
      renderLogin();
      break;
    case "register":
      renderRegister();
      break;
    case "generate":
      renderGenerate();
      break;
    case "match":
      renderMatch();
      break;
    default:
      renderHome();
      break;
  }
}

logoutBtn.addEventListener("click", () => {
  clearAuth();
  showAlert("Signed out.", "success");
  navigate("login");
});

window.addEventListener("hashchange", render);
updateChrome();
render();
