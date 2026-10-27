/**
 * Textora AI - Dedicated Document Audit Workflow
 * Handles structured file inspection, slide/page browser,
 * scanned document alerts, and section-by-section audit execution.
 */

window.DocumentAuditManager = {
  currentDocument: null,
  selectedSectionIndex: 0,
  
  init() {
    this.bindEvents();
  },
  
  bindEvents() {
    const fileInput = document.getElementById('doc-audit-file-input');
    const dropzone = document.getElementById('doc-audit-dropzone');
    
    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());
      
      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-active');
      });
      dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-active'));
      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-active');
        if (e.dataTransfer.files.length) {
          this.uploadAndInspect(e.dataTransfer.files[0]);
        }
      });
      
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
          this.uploadAndInspect(e.target.files[0]);
          fileInput.value = '';
        }
      });
    }
    
    // Audit whole document button
    const btnAuditAll = document.getElementById('btn-audit-entire-doc');
    if (btnAuditAll) {
      btnAuditAll.addEventListener('click', () => this.auditEntireDocument());
    }
    
    // Audit selected section button
    const btnAuditSec = document.getElementById('btn-audit-selected-section');
    if (btnAuditSec) {
      btnAuditSec.addEventListener('click', () => this.auditSelectedSection());
    }
  },
  
  loadExtractedDocument(fileId) {
    const fileObj = window.WorkspaceManager?.activeFiles?.find(f => f.id === fileId);
    if (!fileObj || !fileObj.extractedData) {
      showToast('Document extraction data not found.', 'error');
      return;
    }
    this.currentDocument = fileObj.extractedData;
    this.renderDocumentView();
    navigateTo('document-audit');
  },
  
  async uploadAndInspect(file) {
    const allowed = ['.txt', '.pdf', '.docx', '.pptx'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowed.includes(ext)) {
      showToast(`Unsupported format '${ext}'. Allowed: TXT, PDF, DOCX, PPTX`, 'error');
      return;
    }
    
    if (file.size > 25 * 1024 * 1024) {
      showToast(`File exceeds 25MB limit.`, 'error');
      return;
    }
    
    showToast(`Extracting ${file.name}...`, 'info');
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch('/api/extract', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      
      if (res.ok && data.success) {
        this.currentDocument = data;
        this.renderDocumentView();
        showToast(`Extracted ${data.sections?.length || 1} sections successfully.`, 'success');
      } else {
        showToast(data.detail || 'Extraction failed', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error during extraction.', 'error');
    }
  },
  
  renderDocumentView() {
    const doc = this.currentDocument;
    if (!doc) return;
    
    const metaCard = document.getElementById('doc-audit-meta-card');
    const emptyState = document.getElementById('doc-audit-empty-state');
    const layout = document.getElementById('doc-audit-layout');
    
    if (emptyState) emptyState.style.display = 'none';
    if (layout) layout.style.display = 'grid';
    
    // Scanned document warning
    const noticeEl = document.getElementById('doc-audit-scanned-notice');
    if (noticeEl) {
      if (doc.is_scanned) {
        noticeEl.style.display = 'block';
        noticeEl.innerHTML = `⚠️ <strong>OCR Required Notice:</strong> ${doc.notice}`;
      } else {
        noticeEl.style.display = 'none';
      }
    }
    
    // Meta Header
    const nameEl = document.getElementById('doc-audit-filename');
    const typeBadge = document.getElementById('doc-audit-type-badge');
    const statsEl = document.getElementById('doc-audit-stats');
    
    if (nameEl) nameEl.textContent = doc.filename;
    if (typeBadge) {
      typeBadge.textContent = doc.file_type.toUpperCase();
      typeBadge.className = 'badge badge-lime';
    }
    if (statsEl) {
      const parts = [`${doc.total_words?.toLocaleString() || 0} words`];
      if (doc.page_count) parts.push(`${doc.page_count} pages`);
      if (doc.slide_count) parts.push(`${doc.slide_count} slides`);
      if (doc.section_count) parts.push(`${doc.section_count} sections`);
      statsEl.textContent = parts.join(' • ');
    }
    
    // Section Navigation List
    const navList = document.getElementById('doc-audit-section-list');
    if (!navList) return;
    
    const sections = doc.sections || [];
    navList.innerHTML = sections.map((sec, idx) => `
      <div class="section-nav-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}">
        <span>${sec.title}</span>
        <span class="count-badge">${sec.word_count} w</span>
      </div>
    `).join('');
    
    navList.querySelectorAll('.section-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        navList.querySelectorAll('.section-nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        this.selectSection(parseInt(item.dataset.idx, 10));
      });
    });
    
    this.selectSection(0);
  },
  
  selectSection(idx) {
    this.selectedSectionIndex = idx;
    const sec = this.currentDocument?.sections?.[idx];
    if (!sec) return;
    
    const titleEl = document.getElementById('doc-preview-section-title');
    const textEl = document.getElementById('doc-preview-text');
    const wordsEl = document.getElementById('doc-preview-words');
    
    if (titleEl) titleEl.textContent = sec.title;
    if (textEl) textEl.textContent = sec.text || '(No text extracted for this section)';
    if (wordsEl) wordsEl.textContent = `${sec.word_count} words • ${sec.char_count} chars`;
  },
  
  async auditEntireDocument() {
    if (!this.currentDocument || !this.currentDocument.full_text) {
      showToast('No document content to audit.', 'error');
      return;
    }
    
    showToast('Auditing entire document...', 'info');
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: this.currentDocument.full_text,
          document_name: this.currentDocument.filename,
          sensitivity: AppState.sensitivity,
          save_history: true
        })
      });
      
      const data = await res.json();
      if (res.ok && data.success) {
        data.document = {
          filename: this.currentDocument.filename,
          file_type: this.currentDocument.file_type
        };
        AppState.currentAudit = data;
        window.AnalysisDashboard.renderResults(data);
        navigateTo('results');
        showToast('Document audit complete!', 'success');
      } else {
        showToast(data.detail || 'Audit failed', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error during audit.', 'error');
    }
  },
  
  async auditSelectedSection() {
    const sec = this.currentDocument?.sections?.[this.selectedSectionIndex];
    if (!sec || !sec.text) {
      showToast('Selected section has no readable text.', 'error');
      return;
    }
    
    showToast(`Auditing "${sec.title}"...`, 'info');
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: sec.text,
          document_name: `${this.currentDocument.filename} (${sec.title})`,
          sensitivity: AppState.sensitivity,
          save_history: true
        })
      });
      
      const data = await res.json();
      if (res.ok && data.success) {
        data.document = {
          filename: `${this.currentDocument.filename} (${sec.title})`,
          file_type: this.currentDocument.file_type
        };
        AppState.currentAudit = data;
        window.AnalysisDashboard.renderResults(data);
        navigateTo('results');
        showToast(`Audit for ${sec.title} complete!`, 'success');
      } else {
        showToast(data.detail || 'Section audit failed', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error during section audit.', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.DocumentAuditManager.init();
});
