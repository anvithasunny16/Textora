/**
 * Textora AI - Audit History Manager
 * Manages database persistence, live searching, format filtering,
 * viewing historical reports, and record deletion.
 */

window.HistoryManager = {
  audits: [],
  searchQuery: '',
  selectedType: 'all',
  
  init() {
    this.bindEvents();
  },
  
  bindEvents() {
    const searchInput = document.getElementById('history-search-input');
    const typeFilter = document.getElementById('history-type-filter');
    const refreshBtn = document.getElementById('btn-history-refresh');
    const clearBtn = document.getElementById('btn-history-clear');
    
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.trim().toLowerCase();
        this.renderTable();
      });
    }
    
    if (typeFilter) {
      typeFilter.addEventListener('change', (e) => {
        this.selectedType = e.target.value;
        this.renderTable();
      });
    }
    
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadHistory();
        showToast('History refreshed.', 'info');
      });
    }
    
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearAll());
    }
  },
  
  async loadHistory() {
    const listBody = document.getElementById('history-table-body');
    if (listBody) {
      listBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">Loading audit records...</td></tr>`;
    }
    
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      
      this.audits = data.audits || [];
      this.renderTable();
    } catch (err) {
      console.error(err);
      if (listBody) {
        listBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--risk-coral); padding: 30px;">Failed to load audit history.</td></tr>`;
      }
    }
  },
  
  renderTable() {
    const listBody = document.getElementById('history-table-body');
    const countEl = document.getElementById('history-record-count');
    if (!listBody) return;
    
    let filtered = this.audits;
    if (this.searchQuery) {
      filtered = filtered.filter(a => 
        (a.document_name && a.document_name.toLowerCase().includes(this.searchQuery)) ||
        (a.summary_notes && a.summary_notes.toLowerCase().includes(this.searchQuery)) ||
        (a.classification && a.classification.toLowerCase().includes(this.searchQuery))
      );
    }
    
    if (this.selectedType && this.selectedType !== 'all') {
      filtered = filtered.filter(a => a.file_type === this.selectedType);
    }
    
    if (countEl) countEl.textContent = `${filtered.length} record(s)`;
    
    if (filtered.length === 0) {
      listBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 48px 20px; color: var(--text-secondary);">
            <div style="font-size: 32px; margin-bottom: 10px;">📋</div>
            <div style="font-size: 15px; font-weight: 700; margin-bottom: 4px;">No Audit Records Found</div>
            <div style="font-size: 13px; color: var(--text-muted);">Perform a text analysis or document upload to save your first audit.</div>
          </td>
        </tr>
      `;
      return;
    }
    
    listBody.innerHTML = filtered.map(item => {
      const dateStr = item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent';
      const aiScore = Math.round(item.ai_score || 0);
      const humanScore = Math.round(item.human_score || 0);
      const cls = item.classification || 'Inconclusive';
      
      let badgeCls = 'badge-mixed';
      if (cls.includes('AI')) badgeCls = 'badge-ai';
      if (cls.includes('Human')) badgeCls = 'badge-human';
      
      let fileIcon = '📄';
      if (item.file_type === 'pdf') fileIcon = '📕';
      if (item.file_type === 'docx') fileIcon = '📘';
      if (item.file_type === 'pptx') fileIcon = '📙';
      
      return `
        <tr>
          <td>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span>${fileIcon}</span>
              <div>
                <strong style="color: var(--text-primary);">${item.document_name}</strong>
                <div style="font-size: 11px; color: var(--text-muted);">${item.file_type.toUpperCase()}</div>
              </div>
            </div>
          </td>
          <td style="color: var(--text-secondary);">${dateStr}</td>
          <td><span class="count-badge">${item.word_count.toLocaleString()}</span></td>
          <td>
            <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 700;">
              <span style="color: var(--risk-coral);">${aiScore}% AI</span>
              <span style="color: var(--text-muted);">/</span>
              <span style="color: var(--human-green);">${humanScore}% Human</span>
            </div>
          </td>
          <td><span class="badge ${badgeCls}">${cls}</span></td>
          <td>
            <div style="display: flex; gap: 6px;">
              <button class="btn btn-secondary btn-sm" onclick="window.HistoryManager.viewAudit('${item.id}')" title="View Report">Open</button>
              <button class="btn btn-outline btn-sm" onclick="window.HistoryManager.downloadPdf('${item.id}', '${item.document_name}')" title="Download PDF">PDF</button>
              <button class="btn btn-outline btn-sm" style="color: var(--risk-coral);" onclick="window.HistoryManager.deleteAudit('${item.id}')" title="Delete Record">✕</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },
  
  async viewAudit(auditId) {
    showToast('Loading full report...', 'info');
    try {
      const res = await fetch(`/api/history/${auditId}`);
      if (!res.ok) {
        showToast('Could not retrieve audit.', 'error');
        return;
      }
      const data = await res.json();
      const reportData = data.results;
      reportData.document = {
        filename: data.document_name,
        file_type: data.file_type
      };
      
      AppState.currentAudit = reportData;
      window.AnalysisDashboard.renderResults(reportData);
      navigateTo('results');
    } catch (err) {
      console.error(err);
      showToast('Network error loading audit.', 'error');
    }
  },
  
  async downloadPdf(auditId, docName) {
    showToast('Preparing PDF download...', 'info');
    try {
      const res = await fetch(`/api/history/${auditId}`);
      if (!res.ok) {
        showToast('Failed to retrieve audit data.', 'error');
        return;
      }
      const data = await res.json();
      
      const pdfRes = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          results: data.results,
          document_name: docName || 'Textora_Audit'
        })
      });
      
      if (pdfRes.ok) {
        const blob = await pdfRes.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${docName.replace(/\s+/g, '_')}_Audit.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('PDF downloaded successfully!', 'success');
      } else {
        showToast('Error generating PDF.', 'error');
      }
    } catch (err) {
      showToast('Network error generating PDF.', 'error');
    }
  },
  
  async deleteAudit(auditId) {
    if (!confirm('Are you sure you want to permanently delete this audit record?')) return;
    
    try {
      const res = await fetch(`/api/history/${auditId}`, { method: 'DELETE' });
      if (res.ok) {
        this.audits = this.audits.filter(a => a.id !== auditId);
        this.renderTable();
        showToast('Audit record deleted.', 'success');
      } else {
        showToast('Could not delete record.', 'error');
      }
    } catch (err) {
      showToast('Network error during deletion.', 'error');
    }
  },
  
  async clearAll() {
    if (!confirm('Warning: This will delete ALL saved audit history records in the local SQLite database. Proceed?')) return;
    
    try {
      const res = await fetch('/api/history', { method: 'DELETE' });
      if (res.ok) {
        this.audits = [];
        this.renderTable();
        showToast('All audit history cleared.', 'success');
      } else {
        showToast('Failed to clear history.', 'error');
      }
    } catch (err) {
      showToast('Network error.', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.HistoryManager.init();
});
