/* EduMIS Haftalik Dars Jadvali — Admin tahrirlash paneli */

const TTA = {
  ref: { classes: [], teachers: [], subjects: [], rooms: [] },
  currentClassId: null,
  currentData: null,
  draggedLessonId: null,
  draggedSubjectId: null,

  async init(){
    this.bindTheme();
    await this.loadReferenceData();
    this.bindToolbar();
    if (this.ref.classes.length){
      this.currentClassId = this.ref.classes[0].id;
      document.getElementById("tt-class-select").value = this.currentClassId;
    }
    await this.loadAndRender();
    this.connectStream();
  },

  bindTheme(){
    const saved = localStorage.getItem("tt-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
    const btn = document.getElementById("tt-theme-toggle");
    if (btn) btn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", cur);
      localStorage.setItem("tt-theme", cur);
    });
  },

  async loadReferenceData(){
    const [classes, teachers, subjects, rooms] = await Promise.all([
      fetch("/api/timetable/classes").then(r => r.json()),
      fetch("/api/timetable/teachers").then(r => r.json()),
      fetch("/api/timetable/subjects").then(r => r.json()),
      fetch("/api/timetable/rooms").then(r => r.json()),
    ]);
    this.ref = { classes, teachers, subjects, rooms };

    const classSel = document.getElementById("tt-class-select");
    classSel.innerHTML = classes.map(c => `<option value="${c.id}">${c.name}</option>`).join("");

    const poolEl = document.getElementById("tt-subject-pool");
    poolEl.innerHTML = subjects.map(s =>
      `<div class="tt-subject-chip" draggable="true" data-subject-id="${s.id}" style="background:${s.color}">${s.name}</div>`
    ).join("");
    poolEl.querySelectorAll(".tt-subject-chip").forEach(chip => {
      chip.addEventListener("dragstart", (e) => {
        this.draggedSubjectId = chip.dataset.subjectId;
        this.draggedLessonId = null;
        e.dataTransfer.effectAllowed = "copy";
      });
    });
  },

  bindToolbar(){
    document.getElementById("tt-class-select").addEventListener("change", (e) => {
      this.currentClassId = e.target.value;
      this.loadAndRender();
    });

    document.getElementById("tt-copy-day-btn")?.addEventListener("click", () => this.copyDay());
    document.getElementById("tt-copy-class-btn")?.addEventListener("click", () => this.copyClass());
    document.getElementById("tt-history-btn")?.addEventListener("click", () => this.showHistory());
    document.getElementById("tt-import-btn")?.addEventListener("click", () => {
      document.getElementById("tt-import-file").click();
    });
    document.getElementById("tt-import-file")?.addEventListener("change", (e) => this.importExcel(e));
    document.getElementById("tt-export-excel")?.addEventListener("click", () => {
      window.location.href = `/api/timetable/export/excel/${this.currentClassId}`;
    });
    document.getElementById("tt-export-pdf")?.addEventListener("click", () => {
      window.location.href = `/api/timetable/export/pdf/${this.currentClassId}`;
    });
    document.getElementById("tt-print-btn")?.addEventListener("click", () => window.print());
  },

  showConflict(message){
    const banner = document.getElementById("tt-conflict-banner");
    banner.textContent = "⚠ " + message;
    banner.classList.add("tt-show");
    clearTimeout(this._conflictTimer);
    this._conflictTimer = setTimeout(() => banner.classList.remove("tt-show"), 5000);
  },

  async loadAndRender(){
    if (!this.currentClassId) return;
    const data = await fetch(`/api/timetable/class/${this.currentClassId}`).then(r => r.json());
    this.currentData = data;
    this.render(data);
  },

  todayDow(){
    const d = new Date().getDay();
    return d === 0 ? null : d;
  },

  render(data){
    const container = document.getElementById("tt-grid");
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
        const cellKey = `${slot.slot_order}:${day.num}`;
        if (lesson){
          html += `
            <div class="tt-lesson-cell tt-filled ${isToday ? "tt-today-col" : ""}"
                 style="--cell-color:${lesson.subject_color || "#2563eb"}"
                 draggable="true"
                 data-lesson-id="${lesson.id}"
                 data-slot="${slot.slot_order}" data-day="${day.num}">
              <span class="tt-subject">${lesson.subject_name}</span>
              <span class="tt-teacher">${lesson.teacher_name}</span>
              <span class="tt-room">${lesson.room_name}</span>
            </div>`;
        } else {
          html += `
            <div class="tt-lesson-cell tt-empty"
                 data-slot="${slot.slot_order}" data-day="${day.num}">+</div>`;
        }
      }
    }
    container.innerHTML = html;
    this.attachDnD(container);
  },

  attachDnD(container){
    const cells = container.querySelectorAll(".tt-lesson-cell");
    cells.forEach(cell => {
      // mavjud darsni sudrab ko'chirish
      if (cell.dataset.lessonId){
        cell.addEventListener("dragstart", () => {
          this.draggedLessonId = cell.dataset.lessonId;
          this.draggedSubjectId = null;
          cell.classList.add("tt-dragging");
        });
        cell.addEventListener("dragend", () => cell.classList.remove("tt-dragging"));
        // bosilganda o'chirish tanlovi
        cell.addEventListener("dblclick", () => this.deleteLesson(cell.dataset.lessonId));
      }

      cell.addEventListener("dragover", (e) => {
        e.preventDefault();
        cell.classList.add("tt-drag-over");
      });
      cell.addEventListener("dragleave", () => cell.classList.remove("tt-drag-over"));

      cell.addEventListener("drop", async (e) => {
        e.preventDefault();
        cell.classList.remove("tt-drag-over");
        const slotOrder = parseInt(cell.dataset.slot);
        const day = parseInt(cell.dataset.day);

        if (this.draggedLessonId){
          await this.moveLesson(this.draggedLessonId, slotOrder, day);
        } else if (this.draggedSubjectId){
          await this.promptNewLesson(this.draggedSubjectId, slotOrder, day);
        }
        this.draggedLessonId = null;
        this.draggedSubjectId = null;
      });
    });
  },

  async promptNewLesson(subjectId, slotOrder, day){
    // Yengil inline tanlov: o'qituvchi va xonani tanlash uchun oddiy modal
    const teacher = await this.pickFromList("O'qituvchini tanlang", this.ref.teachers, "full_name");
    if (!teacher) return;
    const room = await this.pickFromList("Xonani tanlang", this.ref.rooms, "name");
    if (!room) return;

    const res = await fetch("/api/timetable/lesson", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        class_id: this.currentClassId,
        day_of_week: day,
        slot_order: slotOrder,
        subject_id: subjectId,
        teacher_id: teacher.id,
        room_id: room.id,
      }),
    });
    const body = await res.json();
    if (!res.ok){
      this.showConflict(body.conflicts?.map(c => c.message).join(" | ") || body.error);
      return;
    }
    this.loadAndRender();
  },

  async moveLesson(lessonId, slotOrder, day){
    const res = await fetch(`/api/timetable/lesson/${lessonId}/move`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ slot_order: slotOrder, day_of_week: day }),
    });
    const body = await res.json();
    if (!res.ok){
      this.showConflict(body.conflicts?.map(c => c.message).join(" | ") || body.error);
      return;
    }
    this.loadAndRender();
  },

  async deleteLesson(lessonId){
    if (!confirm("Bu darsni o'chirishni tasdiqlaysizmi?")) return;
    await fetch(`/api/timetable/lesson/${lessonId}`, { method: "DELETE" });
    this.loadAndRender();
  },

  pickFromList(title, list, labelField){
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:999;";
      overlay.innerHTML = `
        <div style="background:var(--tt-surface);color:var(--tt-text);border-radius:14px;padding:20px;max-width:320px;width:90%;">
          <h4 style="margin-bottom:12px;font-size:0.95rem;">${title}</h4>
          <select id="tt-pick-select" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--tt-border);margin-bottom:14px;">
            ${list.map(i => `<option value="${i.id}">${i[labelField]}</option>`).join("")}
          </select>
          <div style="display:flex;gap:8px;">
            <button id="tt-pick-cancel" class="tt-btn tt-btn-ghost" style="flex:1;">Bekor qilish</button>
            <button id="tt-pick-ok" class="tt-btn" style="flex:1;">Tanlash</button>
          </div>
        </div>`;
      document.body.appendChild(overlay);
      overlay.querySelector("#tt-pick-cancel").onclick = () => { overlay.remove(); resolve(null); };
      overlay.querySelector("#tt-pick-ok").onclick = () => {
        const id = parseInt(overlay.querySelector("#tt-pick-select").value);
        const item = list.find(i => i.id === id);
        overlay.remove();
        resolve(item);
      };
    });
  },

  async copyDay(){
    const fromDay = prompt("Qaysi kundan nusxa olinsin? (1=Dush ... 6=Shan)");
    const toDay = prompt("Qaysi kunga nusxalansin? (1=Dush ... 6=Shan)");
    if (!fromDay || !toDay) return;
    const res = await fetch("/api/timetable/copy-day", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ class_id: this.currentClassId, from_day: parseInt(fromDay), to_day: parseInt(toDay) }),
    });
    const body = await res.json();
    if (!res.ok){
      this.showConflict("Nusxalashda to'qnashuv topildi — avval mos kunni bo'shating");
      return;
    }
    this.loadAndRender();
  },

  async copyClass(){
    const sourceName = prompt("Qaysi sinfdan nusxa olinsin? (sinf nomini yozing)");
    const source = this.ref.classes.find(c => c.name === sourceName);
    if (!source){ alert("Sinf topilmadi"); return; }
    const res = await fetch("/api/timetable/copy-class", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ source_class_id: source.id, target_class_id: this.currentClassId }),
    });
    const body = await res.json();
    if (!res.ok){
      this.showConflict("Nusxalashda to'qnashuv topildi");
      return;
    }
    this.loadAndRender();
  },

  async showHistory(){
    const rows = await fetch(`/api/timetable/history/${this.currentClassId}`).then(r => r.json());
    const panel = document.getElementById("tt-history-panel");
    panel.innerHTML = `<h4 style="margin-bottom:10px;">Jadval tarixi</h4>` + rows.map(r => `
      <div class="tt-history-item">
        <span>${r.note} — ${r.created_by} (${r.created_at})</span>
        <button class="tt-btn tt-btn-ghost" onclick="TTA.restore(${r.id})">Qaytarish</button>
      </div>`).join("") || "<p>Tarix mavjud emas</p>";
    panel.style.display = "block";
  },

  async restore(historyId){
    if (!confirm("Ushbu holatga qaytarishni tasdiqlaysizmi? Joriy holat ham tarixga saqlanadi.")) return;
    await fetch(`/api/timetable/restore/${historyId}`, { method: "POST" });
    this.loadAndRender();
    this.showHistory();
  },

  async importExcel(e){
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`/api/timetable/import/excel/${this.currentClassId}`, {
      method: "POST",
      body: formData,
    });
    const body = await res.json();
    if (body.errors && body.errors.length){
      this.showConflict(`Import: ${body.imported} ta yozildi, ${body.errors.length} ta xato`);
    }
    this.loadAndRender();
    e.target.value = "";
  },

  connectStream(){
    try {
      const es = new EventSource("/api/timetable/stream");
      es.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "lesson_changed" && String(msg.payload.class_id) === String(this.currentClassId)){
            this.loadAndRender();
          }
        } catch(e){ /* ping */ }
      };
    } catch(e){
      console.warn("Real-time ulanish qo'llab-quvvatlanmaydi:", e);
    }
  },
};

document.addEventListener("DOMContentLoaded", () => TTA.init());
