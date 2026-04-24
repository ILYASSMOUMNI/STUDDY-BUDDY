/* StudyBuddy v2 — Alpine.js application */

if (typeof marked !== 'undefined') {
  marked.setOptions({ breaks: true, gfm: true });
}

function app() {
  return {
    // ── Core state ──────────────────────────────────────────────────────────
    initialized: false,
    user: null,
    view: 'dashboard',
    lang: 'fr',
    sidebarOpen: true,
    toasts: [],
    modal: null,   // null | 'upload'

    // ── Forms ───────────────────────────────────────────────────────────────
    login: { name: '', email: '', loading: false, error: '' },
    upload: { file: null, title: '', filiere: 'IA Distribuée', loading: false },

    // ── Data ────────────────────────────────────────────────────────────────
    courses: [],
    dash: { stats: null, progress: [], activity: [], recommendations: [], weaknesses: [] },
    progress: null,

    // ── Chat state ──────────────────────────────────────────────────────────
    chat: {
      courseId: null,
      messages: [],
      input: '',
      sending: false,
      mode: 'default',
    },

    // ── Quiz state ──────────────────────────────────────────────────────────
    quiz: {
      phase: 'config',   // config | taking | result
      courseId: null,
      topic: '',
      numQ: 5,
      diff: 'medium',
      data: null,
      qi: 0,             // question index
      selected: null,
      answered: false,
      answers: [],
      result: null,
      loading: false,
    },

    // ── Static config ────────────────────────────────────────────────────────
    navItems: [
      { view: 'dashboard', icon: 'fas fa-home',           label: 'Tableau de bord' },
      { view: 'chat',      icon: 'fas fa-comments',       label: 'Tuteur IA'       },
      { view: 'quiz',      icon: 'fas fa-clipboard-check',label: 'Quiz'             },
      { view: 'courses',   icon: 'fas fa-book',           label: 'Cours'            },
      { view: 'progress',  icon: 'fas fa-chart-line',     label: 'Progression'      },
    ],

    chatModes: [
      { v: 'default',      label: 'Par défaut',      icon: 'fas fa-comment'       },
      { v: 'explain',      label: 'Expliquer',       icon: 'fas fa-lightbulb'     },
      { v: 'step_by_step', label: 'Étape par étape', icon: 'fas fa-list-ol'       },
      { v: 'example',      label: 'Avec exemples',   icon: 'fas fa-code'          },
      { v: 'summary',      label: 'Résumé',          icon: 'fas fa-compress-alt'  },
    ],

    suggestions: [
      'Explique le principe de MapReduce',
      'Qu\'est-ce que HDFS ?',
      'Donne un exemple de pipeline RAG',
      'Résume les concepts clés du cours',
    ],

    // ── Init ─────────────────────────────────────────────────────────────────
    async init() {
      const saved = localStorage.getItem('sb_user');
      if (saved) {
        try {
          this.user = JSON.parse(saved);
          await Promise.all([this.fetchDash(), this.fetchCourses()]);
        } catch {
          localStorage.removeItem('sb_user');
          this.user = null;
        }
      }
      this.initialized = true;
    },

    // ── Auth ─────────────────────────────────────────────────────────────────
    async loginUser() {
      if (!this.login.name.trim() || !this.login.email.trim()) {
        this.login.error = 'Veuillez remplir tous les champs.';
        return;
      }
      this.login.loading = true;
      this.login.error = '';
      try {
        const d = await this.api('POST', '/api/auth/login', {
          name: this.login.name.trim(),
          email: this.login.email.trim(),
        });
        this.user = d.student;
        localStorage.setItem('sb_user', JSON.stringify(d.student));
        await Promise.all([this.fetchDash(), this.fetchCourses()]);
      } catch (e) {
        this.login.error = 'Impossible de contacter le serveur. Vérifiez que le serveur est lancé.';
      } finally {
        this.login.loading = false;
      }
    },

    logout() {
      localStorage.removeItem('sb_user');
      this.user = null;
      this.dash = { stats: null, progress: [], activity: [], recommendations: [], weaknesses: [] };
      this.courses = [];
      this.progress = null;
    },

    // ── Navigation ────────────────────────────────────────────────────────────
    async navigate(v) {
      this.view = v;
      if (v === 'dashboard') await this.fetchDash();
      else if (v === 'courses')  await this.fetchCourses();
      else if (v === 'progress') await this.fetchProgress();
      else if (v === 'chat' && this.chat.messages.length === 0) await this.loadHistory();
    },

    pageTitle() {
      return { dashboard: 'Tableau de bord', chat: 'Tuteur IA', quiz: 'Quiz',
               courses: 'Bibliothèque', progress: 'Progression' }[this.view] || '';
    },

    // ── Data fetching ─────────────────────────────────────────────────────────
    async fetchDash() {
      if (!this.user) return;
      try {
        const [dash, courses] = await Promise.all([
          this.api('GET', `/api/dashboard/${this.user.id}`),
          this.api('GET', '/api/courses'),
        ]);
        this.dash = dash;
        this.courses = courses;
      } catch (e) { console.error('fetchDash', e); }
    },

    async fetchCourses() {
      try { this.courses = await this.api('GET', '/api/courses'); }
      catch (e) { console.error('fetchCourses', e); }
    },

    async fetchProgress() {
      if (!this.user) return;
      try { this.progress = await this.api('GET', `/api/progress/${this.user.id}`); }
      catch (e) { console.error('fetchProgress', e); }
    },

    // ── Course CRUD ───────────────────────────────────────────────────────────
    async doUpload() {
      if (!this.upload.file || !this.upload.title.trim()) return;
      this.upload.loading = true;
      try {
        const fd = new FormData();
        fd.append('file', this.upload.file);
        fd.append('title', this.upload.title.trim());
        fd.append('filiere', this.upload.filiere);
        const r = await fetch('/api/courses', { method: 'POST', body: fd });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Upload failed');
        this.toast(`Cours indexé — ${d.chunks} passages`, 'success');
        this.modal = null;
        this.upload = { file: null, title: '', filiere: 'IA Distribuée', loading: false };
        await this.fetchCourses();
      } catch (e) {
        this.toast('Erreur : ' + e.message, 'error');
      } finally {
        this.upload.loading = false;
      }
    },

    async deleteCourse(id) {
      if (!confirm('Supprimer ce cours et son index vectoriel ?')) return;
      await this.api('DELETE', `/api/courses/${id}`);
      this.courses = this.courses.filter(c => c.id !== id);
      this.toast('Cours supprimé', 'success');
    },

    pickFile(e) {
      this.upload.file = e.target.files[0] || null;
      if (this.upload.file && !this.upload.title)
        this.upload.title = this.upload.file.name.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ');
    },

    dropFile(e) {
      this.upload.file = e.dataTransfer.files[0] || null;
      if (this.upload.file && !this.upload.title)
        this.upload.title = this.upload.file.name.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ');
    },

    // ── Chat ──────────────────────────────────────────────────────────────────
    async selectCourse(id) {
      this.chat.courseId = id;
      this.chat.messages = [];
      await this.loadHistory();
    },

    async loadHistory() {
      if (!this.user) return;
      try {
        const url = `/api/chat/history/${this.user.id}` +
          (this.chat.courseId ? `?course_id=${this.chat.courseId}` : '');
        const d = await this.api('GET', url);
        this.chat.messages = d.messages || [];
        this.$nextTick(() => this.scrollChat());
      } catch { this.chat.messages = []; }
    },

    async sendMsg() {
      if (!this.chat.input.trim() || this.chat.sending) return;
      const msg = this.chat.input.trim();
      this.chat.input = '';
      this.chat.sending = true;

      this.chat.messages.push({ role: 'user', content: msg });
      this.chat.messages.push({ role: 'assistant', content: '', thinking: true });
      this.$nextTick(() => this.scrollChat());

      try {
        const history = this.chat.messages
          .filter(m => !m.thinking)
          .slice(0, -1)
          .map(m => ({ role: m.role, content: m.content }));

        const d = await this.api('POST', '/api/chat', {
          student_id: this.user.id,
          course_id: this.chat.courseId,
          message: msg,
          messages: history,
          mode: this.chat.mode,
          lang: this.lang,
        });
        this.chat.messages.pop();
        this.chat.messages.push({ role: 'assistant', content: d.reply });
      } catch (e) {
        this.chat.messages.pop();
        this.chat.messages.push({ role: 'assistant', content: '⚠️ Erreur de connexion au serveur.' });
      } finally {
        this.chat.sending = false;
        this.$nextTick(() => this.scrollChat());
      }
    },

    scrollChat() {
      const el = document.getElementById('chat-msgs');
      if (el) el.scrollTop = el.scrollHeight;
    },

    toChat(courseId) {
      this.chat.courseId = courseId;
      this.chat.messages = [];
      this.view = 'chat';
      this.$nextTick(() => this.loadHistory());
    },

    // ── Quiz ──────────────────────────────────────────────────────────────────
    toQuiz(courseId) {
      this.quiz.courseId = String(courseId);
      this.quiz.phase = 'config';
      this.view = 'quiz';
    },

    toQuizConcept(w) {
      this.quiz.courseId = String(w.course_id);
      this.quiz.topic = w.concept;
      this.quiz.phase = 'config';
      this.view = 'quiz';
    },

    async startQuiz() {
      if (!this.quiz.courseId || !this.quiz.topic.trim()) {
        this.toast('Sélectionnez un cours et entrez un sujet', 'warning');
        return;
      }
      this.quiz.loading = true;
      try {
        const d = await this.api('POST', '/api/quiz/generate', {
          student_id: this.user.id,
          course_id: parseInt(this.quiz.courseId),
          topic: this.quiz.topic.trim(),
          num_questions: this.quiz.numQ,
          difficulty: this.quiz.diff,
          lang: this.lang,
        });
        if (d.questions && d.questions.length > 0) {
          this.quiz.data = d;
          this.quiz.phase = 'taking';
          this.quiz.qi = 0;
          this.quiz.selected = null;
          this.quiz.answered = false;
          this.quiz.answers = [];
          this.quiz.result = null;
        } else {
          this.toast('Impossible de générer le quiz — essayez un autre sujet', 'error');
        }
      } catch (e) {
        this.toast('Erreur lors de la génération : ' + e.message, 'error');
      } finally {
        this.quiz.loading = false;
      }
    },

    pickAnswer(opt) {
      if (this.quiz.answered) return;
      this.quiz.selected = opt;
      this.quiz.answered = true;
    },

    async nextQ() {
      const q = this.quiz.data.questions[this.quiz.qi];
      this.quiz.answers.push({
        concept: q.concept || this.quiz.topic,
        question: q.question,
        student_answer: this.quiz.selected,
        correct_answer: q.correct_answer,
        is_correct: this.quiz.selected === q.correct_answer,
      });

      if (this.quiz.qi < this.quiz.data.questions.length - 1) {
        this.quiz.qi++;
        this.quiz.selected = null;
        this.quiz.answered = false;
      } else {
        await this.submitQuiz();
      }
    },

    async submitQuiz() {
      try {
        const d = await this.api('POST', '/api/quiz/submit', {
          student_id: this.user.id,
          course_id: parseInt(this.quiz.courseId),
          answers: this.quiz.answers,
          lang: this.lang,
        });
        this.quiz.result = d;
        this.quiz.phase = 'result';
        await this.fetchDash();
      } catch (e) {
        this.toast('Erreur lors de la soumission', 'error');
      }
    },

    resetQuiz() {
      Object.assign(this.quiz, {
        phase: 'config', data: null, qi: 0,
        selected: null, answered: false, answers: [], result: null,
        topic: '', loading: false,
      });
    },

    chatAboutResult() {
      const concept = this.quiz.result?.analysis?.priorite || this.quiz.topic;
      this.chat.courseId = parseInt(this.quiz.courseId) || null;
      this.chat.messages = [];
      this.chat.input = `Explique-moi le concept : "${concept}"`;
      this.view = 'chat';
      this.$nextTick(() => this.loadHistory());
    },

    // Quiz option styling helpers
    optClass(opt) {
      if (!this.quiz.answered) {
        return this.quiz.selected === opt
          ? 'border-indigo-500 bg-indigo-50 opt-selected'
          : 'border-slate-200 bg-white';
      }
      const correct = this.quiz.data?.questions?.[this.quiz.qi]?.correct_answer;
      if (opt === correct) return 'border-green-500 bg-green-50 opt-correct';
      if (opt === this.quiz.selected) return 'border-red-500 bg-red-50 opt-wrong';
      return 'border-slate-200 bg-white opacity-50 opt-dim';
    },

    optLabelClass(opt, i) {
      if (!this.quiz.answered)
        return this.quiz.selected === opt ? 'bg-indigo-500 text-white' : 'bg-slate-100 text-slate-600';
      const correct = this.quiz.data?.questions?.[this.quiz.qi]?.correct_answer;
      if (opt === correct) return 'bg-green-500 text-white';
      if (opt === this.quiz.selected) return 'bg-red-500 text-white';
      return 'bg-slate-100 text-slate-400';
    },

    // ── Dashboard helpers ─────────────────────────────────────────────────────
    handleRec(r) {
      if (r.type === 'resume_chat')                     this.toChat(r.course_id);
      else if (r.type === 'targeted_quiz' || r.type === 'review_concept')
        this.toQuizConcept({ course_id: r.course_id, concept: r.concept });
      else if (r.type === 'start_quiz')                 this.toQuiz(r.course_id);
    },

    recTitle(r) {
      return { resume_chat: 'Reprendre le chat', targeted_quiz: 'Quiz ciblé',
               review_concept: 'Revoir le concept', start_quiz: 'Démarrer le quiz' }[r.type] || r.type;
    },

    recDesc(r) {
      if (r.concept) return `Concept : "${r.concept}" (${r.fail_count} erreur${r.fail_count>1?'s':''})`;
      if (r.course_title) return `Cours : ${r.course_title}`;
      return '';
    },

    // ── Utility ───────────────────────────────────────────────────────────────
    initials() {
      if (!this.user?.name) return '?';
      return this.user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    },

    getCourse(id) {
      return this.courses.find(c => c.id === id) || null;
    },

    scoreColor(pct) {
      if (pct >= 80) return 'text-green-500';
      if (pct >= 60) return 'text-amber-500';
      return 'text-red-500';
    },

    renderMd(text) {
      if (!text) return '';
      try { return marked.parse(String(text)); }
      catch { return String(text); }
    },

    fmtDate(d) {
      if (!d) return '';
      try {
        return new Date(d).toLocaleDateString('fr-FR',
          { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
      } catch { return d; }
    },

    fmtSize(bytes) {
      if (bytes < 1024)    return bytes + ' B';
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / 1048576).toFixed(1) + ' MB';
    },

    toast(msg, type = 'info') {
      const id = Date.now();
      this.toasts.push({ id, msg, type, show: true });
      setTimeout(() => {
        const i = this.toasts.findIndex(t => t.id === id);
        if (i >= 0) this.toasts.splice(i, 1);
      }, 3800);
    },

    // Generic fetch wrapper
    async api(method, url, body = null) {
      const opts = { method, headers: {} };
      if (body) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
      }
      const r = await fetch(url, opts);
      if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: r.statusText }));
        throw new Error(err.detail || r.statusText);
      }
      return r.json();
    },
  };
}
