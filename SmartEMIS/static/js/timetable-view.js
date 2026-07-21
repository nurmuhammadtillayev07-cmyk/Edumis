/* EduMIS Haftalik Dars Jadvali — o'quvchi/o'qituvchi ko'rinishi (read-only) */

const TT = {
  state: {
    classId: null,
    teacherId: null,
    mode: "class", // "class" | "teacher"
    data: null,
  },

  todayDow(){
    // JS getDay(): 0=Yakshanba..6=Shanba. Bizda 1=Dushanba..6=Shanba.
    const d = new Date().getDay();
    return d === 0 ? null : d;
  },

  async init(){
    this.bindTheme();
    this.bindControls();
    await this.loadReferenceData();
    await this.loadAndRender();
    this.connectStream();
  },

  bindTheme(){
    const saved = localStorage.getItem("tt-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
    const btn = document.getElementById("tt-theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", cur);
      localStorage.setItem("tt-theme", cur);
    });
  },

  async loadReferenceData(){
    const [classes, teachers] = await Promise.all([
      fetch("/api/timetable/classes").then(r => r.json()),
      fetch("/api/timetable/teachers").then(r => r.json()),
    ]);

    const classSel = document.getElementById("tt-class-select");
    if (classSel){
      classSel.innerHTML = classes.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
      classSel.addEventListener("change", () => {
        this.state.mode = "class";
        this.state.classId = classSel.value;
        this.loadAndRender();
      });
      if (classes.length) this.state.classId = classes[0].id;
    }

    const teacherSel = document.getElementById("tt-teacher-select");
    if (teacherSel){
      teacherSel.innerHTML =
        `<option value="">— O'qituvchi bo'yicha ko'rish —</option>` +
        teachers.map(t => `<option value="${t.id}">${t.full_name}</option>`).join("");
      teacherSel.addEventListener("change", () => {
        if (teacherSel.value){
          this.state.mode = "teacher";
          this.state.teacherId = teacherSel.value;
        } else {
          this.state.mode = "class";
        }
        this.loadAndRender();
      });
    }
  },

  bindControls(){
    const searchInput = document.getElementById("tt-search");
    if (searchInput){
      let timer;
      searchInput.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(() => this.doSearch(searchInput.value), 300);
      });
    }
    const printBtn = document.getElementById("tt-print-btn");
    if (printBtn) printBtn.addEventListener("click", () => window.print());

    const excelBtn = document.getElementById("tt-export-excel");
    if (excelBtn) excelBtn.addEventListener("click", () => {
      if (this.state.classId) window.location.href = `/api/timetable/export/excel/${this.state.classId}`;
    });
    const pdfBtn = document.getElementById("tt-export-pdf");
    if (pdfBtn) pdfBtn.addEventListener("click", () => {
      if (this.state.classId) window.location.href = `/api/timetable/export/pdf/${this.state.classId}`;
    });
  },

  async doSearch(q){
    const resultsBox = document.getElementById("tt-search-results");
    if (!resultsBox) return;
    if (!q.trim()){ resultsBox.innerHTML = ""; return; }
    const results = await fetch(`/api/timetable/search?q=${encodeURIComponent(q)}`).then(r => r.json());
    resultsBox.innerHTML = results.map(r =>
      `<div class="tt-history-item"><span>${r.subject_name} — ${r.teacher_name}</span><span>${r.class_name}, ${r.room_name}</span></div>`
    ).join("") || `<div class="tt-history-item">Hech narsa topilmadi</div>`;
  },

  async loadAndRender(){
    let data;
    if (this.state.mode === "teacher" && this.state.teacherId){
      data = await fetch(`/api/timetable/teacher/${this.state.teacherId}`).then(r => r.json());
    } else if (this.state.classId){
      data = await fetch(`/api/timetable/class/${this.state.classId}`).then(r => r.json());
    } else {
      return;
    }
    this.state.data = data;
    this.render(data);
  },

  render(data){
    const container = document.getElementById("tt-grid");
    if (!container) return;
    const today = this.todayDow();

    let html = `<div class="tt-head-cell"></div>`;
    for (const day of data.days){
      html += `<div class="tt-head-cell ${day.num === today ? "tt-today" : ""}">${day.name}</div>`;
    }

    for (const slot of data.slots){
      html += `<div class="tt-time-cell">${slot.start_time}<br>${slot.end_time}</div>`;
      for (const day of data.days){
        const lesson = data.grid[slot.slot_order][String(day.num)];
        const isToday = day.num === today;
        if (lesson){
          html += `
            <div class="tt-lesson-cell tt-filled ${isToday ? "tt-today-col" : ""}" style="--cell-color:${lesson.subject_color || "#2563eb"}">
              <span class="tt-subject">${lesson.subject_name}</span>
              <span class="tt-teacher">${lesson.teacher_name}</span>
              <span class="tt-room">${lesson.room_name}${lesson.class_name ? " · " + lesson.class_name : ""}</span>
            </div>`;
        } else {
          html += `<div class="tt-lesson-cell tt-empty ${isToday ? "tt-today-col" : ""}">—</div>`;
        }
      }
    }
    container.innerHTML = html;
  },

  connectStream(){
    try {
      const es = new EventSource("/api/timetable/stream");
      es.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "lesson_changed" || msg.type === "slots_changed"){
            this.loadAndRender();
          }
        } catch(e){ /* ping xabarlarini e'tiborsiz qoldiramiz */ }
      };
    } catch(e){
      console.warn("Real-time ulanish qo'llab-quvvatlanmaydi:", e);
    }
  },
};

document.addEventListener("DOMContentLoaded", () => TT.init());
