/**
 * Textora AI - Application Controller & Router
 * Manages view routing, theme switching, global state, and toast notifications.
 */

const AppState = {
  currentView: 'landing',
  currentAudit: null,
  activeDocument: null,
  sensitivity: 'balanced',
  theme: 'dark',
  apiProvider: 'heuristic',
  apiKey: ''
};

// Global Navigation
function navigateTo(viewId) {
  // Update state
  AppState.currentView = viewId;
  
  // Update view visibility
  document.querySelectorAll('.app-view').forEach(view => {
    view.classList.remove('active');
  });
  
  const targetView = document.getElementById(`view-${viewId}`);
  if (targetView) {
    targetView.classList.add('active');
  }
  
  // Update navbar links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.dataset.view === viewId) {
      link.classList.add('active');
    }
  });
  
  window.scrollTo({ top: 0, behavior: 'smooth' });
  
  if (window.location.hash.replace('#', '') !== viewId) {
    history.pushState(null, '', `#${viewId}`);
  }
  
  // Specific view hooks
  if (viewId === 'history' && window.HistoryManager) {
    window.HistoryManager.loadHistory();
  }
}

// Toast Notifications
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✓';
  if (type === 'error') icon = '⚠️';
  
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('textora_theme') || 'dark';
  setTheme(savedTheme);
  
  const themeBtn = document.getElementById('btn-toggle-theme');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const newTheme = AppState.theme === 'dark' ? 'light' : 'dark';
      setTheme(newTheme);
    });
  }
}

function setTheme(theme) {
  AppState.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('textora_theme', theme);
  
  const themeBtn = document.getElementById('btn-toggle-theme');
  if (themeBtn) {
    themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    themeBtn.title = theme === 'dark' ? 'Switch to Warm Ivory Light Mode' : 'Switch to Midnight Teal Dark Mode';
  }
}

// Interactive Sample Audit Preview for Landing Page
function initSamplePreview() {
  const samplePresets = {
    ai: {
      text: "In today's fast-paced digital world, artificial intelligence plays a crucial role in revolutionizing pedagogical frameworks across educational institutions. Moreover, it is essential to consider the multifaceted nature of automated adaptive learning systems. This technological evolution serves as a testament to the dynamic landscape of modern computational innovation. In conclusion, it is important to remember that ethical considerations remain paramount.",
      aiScore: 84,
      humanScore: 16,
      verdict: "Likely AI-Generated",
      cv: 0.22,
      markers: 5,
      grade: "Grade 13.2"
    },
    human: {
      text: "I still remember the scent of salt spray and diesel hanging over the pier that chilly October dawn. Dad fumbled with the rusted padlock on the tackle box, his knuckles red from the wind. He swore under his breath when the key jammed, but grinned the minute the brass clicked. We stood shoulder to shoulder for three hours without landing a bite.",
      aiScore: 18,
      humanScore: 82,
      verdict: "Likely Human-Written",
      cv: 0.58,
      markers: 0,
      grade: "Grade 7.4"
    },
    hybrid: {
      text: "The morning keynote at the renewable energy summit kicked off with unexpected humor when the presenter spilled his iced latte across the podium. However, in today's rapidly evolving energy landscape, sustainable infrastructure plays a pivotal role in curbing carbon emissions. The team later discussed distributed solar grids with genuine, fiery passion.",
      aiScore: 48,
      humanScore: 52,
      verdict: "Mixed / Collaborative Content",
      cv: 0.41,
      markers: 2,
      grade: "Grade 10.1"
    }
  };
  
  const pills = document.querySelectorAll('.sample-pill-btn');
  const textBox = document.getElementById('sample-preview-text');
  const aiScoreEl = document.getElementById('sample-ai-score');
  const humanScoreEl = document.getElementById('sample-human-score');
  const verdictEl = document.getElementById('sample-verdict');
  const cvEl = document.getElementById('sample-cv');
  const markersEl = document.getElementById('sample-markers');
  
  if (!pills.length || !textBox) return;
  
  function renderSample(key) {
    const data = samplePresets[key];
    if (!data) return;
    
    textBox.textContent = data.text;
    if (aiScoreEl) aiScoreEl.textContent = `${data.aiScore}%`;
    if (humanScoreEl) humanScoreEl.textContent = `${data.humanScore}%`;
    if (verdictEl) verdictEl.textContent = data.verdict;
    if (cvEl) cvEl.textContent = data.cv;
    if (markersEl) markersEl.textContent = `${data.markers} clichés`;
  }
  
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      renderSample(pill.dataset.sample);
    });
  });
  
  renderSample('ai');
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSamplePreview();
  
  // Navigation Event Listeners
  document.querySelectorAll('[data-view-target]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(el.dataset.viewTarget);
    });
  });
  
  // Listen for hashchange
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && ['landing', 'workspace', 'document-audit', 'results', 'history', 'settings'].includes(hash)) {
      navigateTo(hash);
    }
  });

  // Initial hash check
  const initHash = window.location.hash.replace('#', '');
  if (initHash && ['landing', 'workspace', 'document-audit', 'results', 'history', 'settings'].includes(initHash)) {
    navigateTo(initHash);
  }
  
  console.log('Textora AI v1.0.0 client initialized.');
});
