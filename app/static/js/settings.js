/**
 * Textora AI - Settings & Help Controller
 * Manages configuration, sensitivity adjustment, API key handling,
 * and FAQ accordion interactivity.
 */

window.SettingsManager = {
  init() {
    this.bindEvents();
    this.loadSettings();
  },
  
  bindEvents() {
    // Sensitivity selector
    const sensSelect = document.getElementById('setting-sensitivity');
    if (sensSelect) {
      sensSelect.addEventListener('change', (e) => {
        AppState.sensitivity = e.target.value;
        localStorage.setItem('textora_sensitivity', e.target.value);
        showToast(`Detection sensitivity set to ${e.target.value.toUpperCase()}.`, 'info');
      });
    }
    
    // API Provider selector
    const provSelect = document.getElementById('setting-provider');
    const apiKeyGroup = document.getElementById('setting-api-key-group');
    if (provSelect && apiKeyGroup) {
      provSelect.addEventListener('change', (e) => {
        AppState.apiProvider = e.target.value;
        apiKeyGroup.style.display = e.target.value === 'heuristic' ? 'none' : 'block';
        showToast(`Analysis engine set to ${e.target.options[e.target.selectedIndex].text}`, 'info');
      });
    }
    
    // API Key input
    const keyInput = document.getElementById('setting-api-key');
    if (keyInput) {
      keyInput.addEventListener('change', (e) => {
        AppState.apiKey = e.target.value.trim();
        showToast('API credential stored in active session.', 'success');
      });
    }
    
    // FAQ Accordion
    document.querySelectorAll('.faq-question').forEach(q => {
      q.addEventListener('click', () => {
        const item = q.closest('.faq-item');
        if (item) {
          item.classList.toggle('open');
        }
      });
    });
  },
  
  loadSettings() {
    const savedSens = localStorage.getItem('textora_sensitivity') || 'balanced';
    AppState.sensitivity = savedSens;
    
    const sensSelect = document.getElementById('setting-sensitivity');
    if (sensSelect) sensSelect.value = savedSens;
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.SettingsManager.init();
});
