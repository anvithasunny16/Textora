/**
 * Textora AI - Auditor Workspace Controller
 * Controls text editor interactions, live metrics, multi-file uploads,
 * sample presets, and initiates content analysis.
 */

window.WorkspaceManager = {
  editor: null,
  activeFiles: [],
  undoStack: [],
  
  init() {
    this.editor = document.getElementById('editor-textarea');
    this.bindEvents();
    this.updateCounts();
  },
  
  bindEvents() {
    if (!this.editor) return;
    
    // Live count updating
    this.editor.addEventListener('input', () => {
      this.saveUndoState();
      this.updateCounts();
    });
    
    // Paste button
    const pasteBtn = document.getElementById('btn-editor-paste');
    if (pasteBtn) {
      pasteBtn.addEventListener('click', async () => {
        try {
          const clipText = await navigator.clipboard.readText();
          const textarea = this.editor || document.getElementById('editor-textarea');
          if (clipText && textarea) {
            textarea.value = clipText;
            this.updateCounts();
            showToast('Text pasted from clipboard.', 'success');
          }
        } catch (err) {
          showToast('Clipboard access denied. Please paste using Ctrl+V.', 'info');
        }
      });
    }
    
    // Clear button
    const clearBtn = document.getElementById('btn-editor-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        const textarea = this.editor || document.getElementById('editor-textarea');
        if (textarea && textarea.value.trim().length > 0) {
          this.saveUndoState();
          textarea.value = '';
          this.updateCounts();
          showToast('Editor cleared.', 'info');
        }
      });
    }
    
    // Undo button
    const undoBtn = document.getElementById('btn-editor-undo');
    if (undoBtn) {
      undoBtn.addEventListener('click', () => {
        const textarea = this.editor || document.getElementById('editor-textarea');
        if (this.undoStack.length > 0 && textarea) {
          textarea.value = this.undoStack.pop();
          this.updateCounts();
          showToast('Undo applied.', 'info');
        } else {
          showToast('No earlier actions to undo.', 'info');
        }
      });
    }
    
    // Preset Sample Select
    const sampleSelect = document.getElementById('select-sample-preset');
    if (sampleSelect) {
      sampleSelect.addEventListener('change', (e) => {
        this.loadPreset(e.target.value);
        e.target.value = '';
      });
    }
    
    // Drag & Drop
    const dropzone = document.getElementById('workspace-dropzone');
    const fileInput = document.getElementById('workspace-file-input');
    
    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());
      
      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-active');
      });
      
      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-active');
      });
      
      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-active');
        if (e.dataTransfer.files.length) {
          this.handleFiles(Array.from(e.dataTransfer.files));
        }
      });
      
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
          this.handleFiles(Array.from(e.target.files));
          fileInput.value = '';
        }
      });
    }
    
    // Primary Analyze Button
    const analyzeBtn = document.getElementById('btn-analyze-content');
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => this.analyzeContent());
    }
  },
  
  saveUndoState() {
    if (this.editor.value) {
      if (this.undoStack.length > 20) this.undoStack.shift();
      this.undoStack.push(this.editor.value);
    }
  },
  
  updateCounts() {
    if (!this.editor) return;
    const text = this.editor.value.trim();
    
    const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
    const chars = text.length;
    const sentences = text ? (text.match(/[^.!?]+[.!?]+(\s|$)/g) || [text]).length : 0;
    const readingTimeSec = Math.round((words / 225) * 60);
    
    const wordEl = document.getElementById('count-words');
    const charEl = document.getElementById('count-chars');
    const sentenceEl = document.getElementById('count-sentences');
    const readingEl = document.getElementById('count-reading-time');
    const analyzeBtn = document.getElementById('btn-analyze-content');
    
    if (wordEl) wordEl.textContent = words.toLocaleString();
    if (charEl) charEl.textContent = chars.toLocaleString();
    if (sentenceEl) sentenceEl.textContent = sentences.toLocaleString();
    if (readingEl) readingEl.textContent = `${readingTimeSec}s`;
  },
  
  loadPreset(presetType) {
    const presets = {
      human: "I still remember the scent of salt spray and diesel hanging over the pier that chilly October dawn. Dad fumbled with the rusted padlock on the tackle box, his knuckles red from the wind. He swore under his breath when the key jammed, but grinned the minute the brass tumblers clicked into place. 'First cast belongs to the early riser,' he said, handing me the weathered fiberglass rod. We stood shoulder to shoulder for nearly three hours without landing a single bite. It didn't matter in the slightest. The rhythm of the tide against the wooden pilings felt like a steady, unspoken conversation.",
      ai: "In today's fast-paced digital world, artificial intelligence plays a crucial role in revolutionizing modern industries. Moreover, it is essential to consider the multifaceted nature of automated machine learning systems across society. This technological paradigm serves as a testament to the dynamic landscape of modern computational innovation. Furthermore, machine learning algorithms delve into vast datasets to unlock unprecedented analytical potential. At its core, this rich tapestry of interconnected technologies fosters a sense of progress across diverse sectors. In conclusion, it is important to remember that ethical considerations remain paramount as we navigate this transformative journey.",
      hybrid: "The morning keynote at the renewable energy summit kicked off with unexpected humor when the presenter spilled his iced latte across the podium. However, in today's rapidly evolving energy landscape, sustainable infrastructure plays a pivotal role in curbing carbon emissions. The engineering team later discussed distributed solar microgrids with genuine, fiery passion. Still, questions around scalable battery storage remain a crucial challenge for municipal planners.",
      academic: "The proliferation of digital communication platforms has profoundly reshaped linguistic exchange. While historical grammarians prioritized strict syntactical orthodoxy, contemporary sociolinguists celebrate morphological fluidity. Consequently, modern textual analysis must balance algorithmic precision with nuanced hermeneutic sensitivity."
    };
    
    if (presets[presetType]) {
      const textarea = this.editor || document.getElementById('editor-textarea');
      this.saveUndoState();
      if (textarea) textarea.value = presets[presetType];
      this.updateCounts();
      showToast(`Loaded ${presetType.toUpperCase()} sample text.`, 'info');
    }
  },
  
  handleFiles(files) {
    const allowed = ['.txt', '.pdf', '.docx', '.pptx'];
    
    files.forEach(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      if (!allowed.includes(ext)) {
        showToast(`Unsupported format '${ext}'. Allowed: TXT, PDF, DOCX, PPTX`, 'error');
        return;
      }
      
      if (file.size > 25 * 1024 * 1024) {
        showToast(`File '${file.name}' exceeds 25MB limit.`, 'error');
        return;
      }
      
      const fileObj = {
        id: 'file_' + Math.random().toString(36).substring(2, 9),
        file: file,
        name: file.name,
        size: this.formatBytes(file.size),
        type: ext.replace('.', ''),
        status: 'Ready'
      };
      
      this.activeFiles.push(fileObj);
      this.extractFileText(fileObj);
    });
    
    this.renderFileQueue();
    this.updateCounts();
  },
  
  async extractFileText(fileObj) {
    fileObj.status = 'Extracting...';
    this.renderFileQueue();
    
    const formData = new FormData();
    formData.append('file', fileObj.file);
    
    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (response.ok && data.success) {
        fileObj.status = 'Extracted';
        fileObj.extractedData = data;
        
        // Populate editor if empty
        if (!this.editor.value.trim() && data.full_text) {
          this.editor.value = data.full_text;
          this.updateCounts();
          showToast(`Extracted ${data.total_words} words from ${fileObj.name}`, 'success');
        }
      } else {
        fileObj.status = 'Failed';
        showToast(data.detail || 'Extraction failed', 'error');
      }
    } catch (err) {
      fileObj.status = 'Error';
      showToast(`Network error extracting ${fileObj.name}`, 'error');
    }
    
    this.renderFileQueue();
  },
  
  removeFile(id) {
    this.activeFiles = this.activeFiles.filter(f => f.id !== id);
    this.renderFileQueue();
    this.updateCounts();
  },
  
  renderFileQueue() {
    const queueEl = document.getElementById('workspace-file-queue');
    if (!queueEl) return;
    
    if (this.activeFiles.length === 0) {
      queueEl.innerHTML = '';
      return;
    }
    
    queueEl.innerHTML = this.activeFiles.map(f => {
      let icon = '📄';
      if (f.type === 'pdf') icon = '📕';
      if (f.type === 'docx') icon = '📘';
      if (f.type === 'pptx') icon = '📙';
      
      return `
        <div class="file-item">
          <div class="file-info">
            <span style="font-size: 20px;">${icon}</span>
            <div>
              <div class="file-name" title="${f.name}">${f.name}</div>
              <div class="file-meta">${f.size} &bull; ${f.type.toUpperCase()} &bull; <span style="color: var(--accent-lime);">${f.status}</span></div>
            </div>
          </div>
          <div style="display: flex; gap: 6px;">
            ${f.extractedData ? `<button class="btn btn-outline btn-sm" onclick="window.DocumentAuditManager.loadExtractedDocument('${f.id}')">Inspect</button>` : ''}
            <button class="btn btn-outline btn-sm" style="color: var(--risk-coral);" onclick="window.WorkspaceManager.removeFile('${f.id}')">✕</button>
          </div>
        </div>
      `;
    }).join('');
  },
  
  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  },
  
  async analyzeContent() {
    const textarea = this.editor || document.getElementById('editor-textarea');
    const text = textarea ? textarea.value.trim() : '';
    if (text.length < 15 && this.activeFiles.length === 0) {
      showToast('Please enter text or click a sample preset above!', 'info');
      return;
    }
    
    const analyzeBtn = document.getElementById('btn-analyze-content');
    const originalText = analyzeBtn.innerHTML;
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span>⏳</span> Auditing Content...`;
    
    try {
      let result;
      const sensitivity = AppState.sensitivity || 'balanced';
      
      // If we have an uploaded file with no text edits
      if (this.activeFiles.length > 0 && (!text || text === this.activeFiles[0].extractedData?.full_text)) {
        const formData = new FormData();
        formData.append('file', this.activeFiles[0].file);
        formData.append('sensitivity', sensitivity);
        formData.append('provider', AppState.apiProvider);
        formData.append('save_history', 'true');
        
        const res = await fetch('/api/analyze-file', {
          method: 'POST',
          body: formData
        });
        result = await res.json();
      } else {
        const payload = {
          text: text,
          sensitivity: sensitivity,
          provider: AppState.apiProvider,
          document_name: this.activeFiles[0]?.name || 'Pasted Content',
          save_history: true
        };
        
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        result = await res.json();
      }
      
      if (result.success) {
        AppState.currentAudit = result;
        showToast('Text audit complete!', 'success');
        window.AnalysisDashboard.renderResults(result);
        navigateTo('results');
      } else {
        showToast(result.detail || 'Analysis could not be completed.', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error while analyzing content.', 'error');
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = originalText;
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.WorkspaceManager.init();
});
