/**
 * Textora AI - Results Dashboard Controller
 * Renders audit statistics, animated dual gauges, interactive sentence highlighter,
 * sentence inspector drawer, diagnostic metric cards, recommendations, and report exports.
 */

window.AnalysisDashboard = {
  currentData: null,
  activeFilter: 'all',
  selectedSentenceIndex: null,
  
  init() {
    this.bindExportEvents();
    this.bindFilterEvents();
  },
  
  bindExportEvents() {
    const btnPdf = document.getElementById('btn-export-pdf');
    const btnJson = document.getElementById('btn-export-json');
    const btnPrint = document.getElementById('btn-export-print');
    
    if (btnPdf) {
      btnPdf.addEventListener('click', () => this.exportPdf());
    }
    if (btnJson) {
      btnJson.addEventListener('click', () => this.exportJson());
    }
    if (btnPrint) {
      btnPrint.addEventListener('click', () => this.exportPrint());
    }
  },
  
  bindFilterEvents() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.activeFilter = btn.dataset.filter;
        this.applySentenceFilter();
      });
    });
  },
  
  renderResults(data) {
    this.currentData = data;
    const scores = data.scores || {};
    const stats = data.statistics || {};
    const metrics = data.metrics || {};
    const doc = data.document || {};
    
    // Header
    const titleEl = document.getElementById('res-doc-title');
    const dateEl = document.getElementById('res-doc-date');
    const methodEl = document.getElementById('res-method-badge');
    
    if (titleEl) titleEl.textContent = doc.filename || 'Audited Content';
    if (dateEl) dateEl.textContent = new Date().toLocaleString();
    if (methodEl) methodEl.textContent = data.method || 'Built-in Linguistic Heuristics';
    
    // Gauges
    const aiVal = Math.round(scores.ai_score || 0);
    const humanVal = Math.round(scores.human_score || 0);
    
    const aiBar = document.getElementById('gauge-ai-bar');
    const humanBar = document.getElementById('gauge-human-bar');
    const aiText = document.getElementById('gauge-ai-val');
    const humanText = document.getElementById('gauge-human-val');
    
    if (aiBar) aiBar.style.width = `${aiVal}%`;
    if (humanBar) humanBar.style.width = `${humanVal}%`;
    if (aiText) aiText.textContent = `${aiVal}%`;
    if (humanText) humanText.textContent = `${humanVal}%`;
    
    // Verdict
    const verdictBadge = document.getElementById('res-verdict-badge');
    const verdictText = document.getElementById('res-verdict-text');
    const confBadge = document.getElementById('res-conf-badge');
    const confExpl = document.getElementById('res-conf-explanation');
    
    const cls = data.classification || 'Inconclusive';
    if (verdictBadge) {
      verdictBadge.textContent = cls;
      verdictBadge.className = 'badge ' + (
        cls.includes('AI') ? 'badge-ai' : (cls.includes('Human') ? 'badge-human' : 'badge-mixed')
      );
    }
    
    if (verdictText) verdictText.textContent = data.summary || '';
    if (confBadge) confBadge.textContent = `Confidence: ${data.confidence || 'Moderate'}`;
    if (confExpl) confExpl.textContent = data.confidence_explanation || '';
    
    // Sentence Breakdown
    this.renderSentenceStream(data.sentence_breakdown?.sentences || []);
    
    // Deep-Dive Metric 1: Burstiness
    const burst = metrics.burstiness || {};
    const cvVal = document.getElementById('metric-burst-cv');
    const burstLabel = document.getElementById('metric-burst-label');
    const meanLen = document.getElementById('metric-burst-mean');
    
    if (cvVal) cvVal.textContent = burst.coefficient_of_variation ?? '0.0';
    if (burstLabel) burstLabel.textContent = burst.burstiness_label || 'Pacing Analysis';
    if (meanLen) meanLen.textContent = `${burst.mean_length || 0} words/sentence (±${burst.std_deviation || 0})`;
    
    // Distribution Bars
    const dist = burst.distribution || {};
    const totalSent = Math.max(1, stats.sentence_count || 1);
    this.setMiniBar('dist-short', (dist.short_1_to_10 || 0) / totalSent * 100);
    this.setMiniBar('dist-med', (dist.medium_11_to_20 || 0) / totalSent * 100);
    this.setMiniBar('dist-long', (dist.long_21_to_30 || 0) / totalSent * 100);
    this.setMiniBar('dist-ext', (dist.extended_31_plus || 0) / totalSent * 100);
    
    // Deep-Dive Metric 2: Lexical Richness
    const lex = metrics.lexical_diversity || {};
    const ttrVal = document.getElementById('metric-lex-ttr');
    const lexLabel = document.getElementById('metric-lex-label');
    const hapaxVal = document.getElementById('metric-lex-hapax');
    
    if (ttrVal) ttrVal.textContent = lex.ttr ?? '0.0';
    if (lexLabel) lexLabel.textContent = lex.diversity_label || 'Vocabulary Variety';
    if (hapaxVal) hapaxVal.textContent = `${lex.unique_words || 0} unique words (${lex.hapax_count || 0} used once)`;
    
    // Deep-Dive Metric 3: Formulaic Markers
    const form = metrics.formulaic_patterns || {};
    const formVal = document.getElementById('metric-form-count');
    const formDensity = document.getElementById('metric-form-density');
    const formTags = document.getElementById('metric-form-tags');
    
    if (formVal) formVal.textContent = `${form.total_markers || 0}`;
    if (formDensity) formDensity.textContent = `Density: ${form.density_per_100_words || 0} per 100 words`;
    
    if (formTags) {
      const phrases = form.matched_phrases || [];
      if (phrases.length === 0) {
        formTags.innerHTML = `<span style="font-size: 12px; color: var(--human-green);">✓ No obvious algorithmic transition clichés detected.</span>`;
      } else {
        formTags.innerHTML = phrases.map(p => `<span class="marker-tag">${p}</span>`).join('');
      }
    }
    
    // Deep-Dive Metric 4: Readability
    const read = metrics.readability || {};
    const gradeVal = document.getElementById('metric-read-grade');
    const freVal = document.getElementById('metric-read-fre');
    const fogVal = document.getElementById('metric-read-fog');
    
    if (gradeVal) gradeVal.textContent = `Grade ${read.flesch_kincaid_grade || '8.0'}`;
    if (freVal) freVal.textContent = `Reading Ease: ${read.flesch_reading_ease || 60} (${read.flesch_reading_ease_label || 'Standard'})`;
    if (fogVal) fogVal.textContent = `Gunning Fog: ${read.gunning_fog_index || '9.0'} | Coleman-Liau: ${read.coleman_liau_index || '9.0'}`;
    
    // Recommendations
    this.renderRecommendations(data.recommendations || []);
  },
  
  setMiniBar(id, pct) {
    const bar = document.getElementById(id);
    if (bar) bar.style.width = `${Math.min(100, Math.round(pct))}%`;
  },
  
  renderSentenceStream(sentences) {
    const stream = document.getElementById('sentence-stream-container');
    if (!stream) return;
    
    if (sentences.length === 0) {
      stream.innerHTML = '<p style="color: var(--text-muted);">No sentences to display.</p>';
      return;
    }
    
    stream.innerHTML = sentences.map((s, idx) => {
      return `<span class="sentence-span ${s.signal}" data-index="${idx}" title="Score: ${s.score}% AI signal - Click to inspect">${s.text} </span>`;
    }).join('');
    
    // Attach click events
    stream.querySelectorAll('.sentence-span').forEach(span => {
      span.addEventListener('click', () => {
        const idx = parseInt(span.dataset.index, 10);
        this.selectSentence(idx);
      });
    });
    
    // Select first sentence by default if available
    if (sentences.length > 0) {
      this.selectSentence(0);
    }
  },
  
  selectSentence(idx) {
    this.selectedSentenceIndex = idx;
    const sentences = this.currentData?.sentence_breakdown?.sentences || [];
    const s = sentences[idx];
    if (!s) return;
    
    // Highlight active span
    document.querySelectorAll('.sentence-span').forEach(sp => {
      sp.classList.toggle('selected', parseInt(sp.dataset.index, 10) === idx);
    });
    
    // Render Inspector
    const inspector = document.getElementById('sentence-inspector');
    const inspIndex = document.getElementById('insp-sentence-index');
    const inspSignalBadge = document.getElementById('insp-signal-badge');
    const inspScore = document.getElementById('insp-score');
    const inspText = document.getElementById('insp-text');
    const inspReasons = document.getElementById('insp-reasons-list');
    const inspMeta = document.getElementById('insp-meta-counts');
    
    if (!inspector) return;
    inspector.style.display = 'block';
    
    if (inspIndex) inspIndex.textContent = `Sentence #${idx + 1}`;
    if (inspSignalBadge) {
      inspSignalBadge.textContent = s.signal.toUpperCase();
      inspSignalBadge.className = 'badge ' + (
        s.signal === 'ai' ? 'badge-ai' : (s.signal === 'human' ? 'badge-human' : 'badge-mixed')
      );
    }
    if (inspScore) inspScore.textContent = `${s.score}% AI Signal`;
    if (inspText) inspText.textContent = `"${s.text}"`;
    if (inspMeta) inspMeta.textContent = `${s.word_count} words • ${s.syllables} syllables (${s.avg_syllable_per_word} syl/word)`;
    
    if (inspReasons) {
      inspReasons.innerHTML = s.reasons.map(r => `
        <div class="reason-tag">
          <span style="color: var(--accent-lime);">▪</span>
          <span>${r}</span>
        </div>
      `).join('');
    }
  },
  
  applySentenceFilter() {
    const spans = document.querySelectorAll('.sentence-span');
    spans.forEach(span => {
      if (this.activeFilter === 'all') {
        span.style.display = 'inline';
      } else {
        span.style.display = span.classList.contains(this.activeFilter) ? 'inline' : 'none';
      }
    });
  },
  
  renderRecommendations(recs) {
    const container = document.getElementById('recs-container');
    if (!container) return;
    
    if (recs.length === 0) {
      container.innerHTML = '<p style="color: var(--text-muted);">No recommendations at this time.</p>';
      return;
    }
    
    container.innerHTML = recs.map(r => `
      <div class="rec-item">
        <div class="rec-category">${r.category}</div>
        <div class="rec-title">${r.title}</div>
        <div class="rec-desc">${r.description}</div>
      </div>
    `).join('');
  },
  
  async exportPdf() {
    if (!this.currentData) return;
    showToast('Generating official PDF report...', 'info');
    
    try {
      const response = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          results: this.currentData,
          document_name: this.currentData.document?.filename || 'Textora_Audit_Report'
        })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Textora_Audit_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('PDF report downloaded!', 'success');
      } else {
        showToast('Failed to generate PDF.', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error generating PDF.', 'error');
    }
  },
  
  async exportJson() {
    if (!this.currentData) return;
    const jsonStr = JSON.stringify(this.currentData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Textora_Audit_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast('JSON report downloaded!', 'success');
  },
  
  async exportPrint() {
    if (!this.currentData) return;
    try {
      const res = await fetch('/api/export/html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          results: this.currentData,
          document_name: this.currentData.document?.filename || 'Textora_Audit'
        })
      });
      
      const html = await res.text();
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(html);
        printWindow.document.close();
      }
    } catch (err) {
      showToast('Error opening print report.', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.AnalysisDashboard.init();
});
