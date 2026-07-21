# -*- coding: utf-8 -*-
"""EduMIS uchun tarjima lug'ati (uz / ru / en)."""

TRANSLATIONS = {
    # ---------- Umumiy / tugmalar ----------
    "app_name": {"uz": "EduMIS", "ru": "EduMIS", "en": "EduMIS"},
    "save": {"uz": "Saqlash", "ru": "Сохранить", "en": "Save"},
    "cancel": {"uz": "Bekor qilish", "ru": "Отмена", "en": "Cancel"},
    "delete": {"uz": "O'chirish", "ru": "Удалить", "en": "Delete"},
    "download": {"uz": "Yuklab olish", "ru": "Скачать", "en": "Download"},
    "search": {"uz": "Qidirish", "ru": "Поиск", "en": "Search"},
    "back": {"uz": "Orqaga", "ru": "Назад", "en": "Back"},
    "today": {"uz": "Bugun", "ru": "Сегодня", "en": "Today"},
    "none_found": {"uz": "Hech narsa topilmadi.", "ru": "Ничего не найдено.", "en": "Nothing found."},
    "count_ta": {"uz": "ta", "ru": "", "en": ""},

    # ---------- Navigatsiya (base.html) ----------
    "nav_panel": {"uz": "Panel", "ru": "Панель", "en": "Panel"},
    "nav_home": {"uz": "Bosh sahifa", "ru": "Главная", "en": "Home"},
    "nav_students": {"uz": "O'quvchilar", "ru": "Ученики", "en": "Students"},
    "nav_attendance": {"uz": "Davomat", "ru": "Посещаемость", "en": "Attendance"},
    "nav_schedule": {"uz": "Jadval", "ru": "Расписание", "en": "Schedule"},
    "nav_teachers": {"uz": "O'qituvchilar", "ru": "Учителя", "en": "Teachers"},
    "nav_classrooms": {"uz": "Sinfxonalar", "ru": "Кабинеты", "en": "Classrooms"},
    "nav_grades": {"uz": "Baholar", "ru": "Оценки", "en": "Grades"},
    "nav_backup": {"uz": "Zaxira", "ru": "Резервная копия", "en": "Backup"},
    "nav_ai_report": {"uz": "SI Hisobot", "ru": "ИИ-отчёт", "en": "AI Report"},
    "nav_my_profile": {"uz": "Mening kabinetim", "ru": "Мой кабинет", "en": "My Profile"},
    "nav_notifications": {"uz": "Bildirishnoma", "ru": "Уведомления", "en": "Notifications"},
    "nav_settings": {"uz": "Sozlamalar", "ru": "Настройки", "en": "Settings"},
    "nav_cabinet": {"uz": "Kabinetim", "ru": "Мой кабинет", "en": "Cabinet"},

    # ---------- Login ----------
    "login_title": {"uz": "Tizimga kirish", "ru": "Вход в систему", "en": "Sign In"},
    "login_subtitle": {"uz": "Davom etish uchun login va parolni kiriting", "ru": "Введите логин и пароль для продолжения", "en": "Enter your username and password to continue"},
    "login_username": {"uz": "Login", "ru": "Логин", "en": "Username"},
    "login_password": {"uz": "Parol", "ru": "Пароль", "en": "Password"},
    "login_button": {"uz": "Kirish", "ru": "Войти", "en": "Sign In"},

    # ---------- Dashboard ----------
    "dash_welcome": {"uz": "Xush kelibsiz", "ru": "Добро пожаловать", "en": "Welcome"},
    "dash_subtitle": {"uz": "Tizim umumiy ko'rsatkichlari", "ru": "Общие показатели системы", "en": "Overall system stats"},
    "dash_students": {"uz": "O'quvchilar", "ru": "Ученики", "en": "Students"},
    "dash_teachers": {"uz": "O'qituvchilar", "ru": "Учителя", "en": "Teachers"},
    "dash_classes": {"uz": "Sinflar", "ru": "Классы", "en": "Classes"},
    "dash_attendance_rate": {"uz": "Davomat foizi", "ru": "Процент посещаемости", "en": "Attendance rate"},
    "dash_trend_title": {"uz": "Davomat trendi (oxirgi 14 kun)", "ru": "Тренд посещаемости (последние 14 дней)", "en": "Attendance trend (last 14 days)"},
    "dash_trend_empty": {"uz": "Hozircha davomat ma'lumotlari yo'q.", "ru": "Пока нет данных о посещаемости.", "en": "No attendance data yet."},
    "dash_class_chart_title": {"uz": "Sinflar bo'yicha o'quvchilar soni", "ru": "Число учеников по классам", "en": "Students per class"},
    "dash_class_chart_empty": {"uz": "Hozircha sinflarga o'quvchi biriktirilmagan.", "ru": "Пока ни один ученик не привязан к классу.", "en": "No students assigned to a class yet."},
    "dash_link_students": {"uz": "O'quvchilar ro'yxati", "ru": "Список учеников", "en": "Student list"},
    "dash_link_attendance": {"uz": "Davomatni belgilash", "ru": "Отметить посещаемость", "en": "Mark attendance"},
    "dash_link_grades": {"uz": "Baholarni ko'rish", "ru": "Просмотр оценок", "en": "View grades"},

    # ---------- Students ----------
    "students_title": {"uz": "O'quvchilar tarkibi", "ru": "Список учеников", "en": "Student List"},
    "students_total": {"uz": "Jami", "ru": "Всего", "en": "Total"},
    "students_search_placeholder": {"uz": "F.I.Sh yoki JSHSHIR bo'yicha qidirish...", "ru": "Поиск по ФИО или ИНН...", "en": "Search by name or ID..."},
    "students_all_classes": {"uz": "Barcha sinflar", "ru": "Все классы", "en": "All classes"},
    "students_no_results": {"uz": "Qidiruv bo'yicha hech narsa topilmadi.", "ru": "По запросу ничего не найдено.", "en": "No results found."},
    "students_empty": {"uz": "Hozircha o'quvchilar kiritilmagan.", "ru": "Ученики пока не добавлены.", "en": "No students added yet."},
    "students_add_title": {"uz": "O'quvchi qo'shish", "ru": "Добавить ученика", "en": "Add Student"},
    "students_full_name_placeholder": {"uz": "F.I.Sh (Masalan: Aliyev Vali)", "ru": "ФИО (напр.: Алиев Вали)", "en": "Full name (e.g. Aliyev Vali)"},
    "students_jshshir_placeholder": {"uz": "JSHSHIR (14 xonali)", "ru": "ИНН (14 цифр)", "en": "ID number (14 digits)"},
    "students_class_placeholder": {"uz": "Sinf (Masalan: 9-A)", "ru": "Класс (напр.: 9-А)", "en": "Class (e.g. 9-A)"},
    "students_birth_date": {"uz": "Tug'ilgan sana", "ru": "Дата рождения", "en": "Birth date"},
    "students_gender_male": {"uz": "Erkak", "ru": "Мужской", "en": "Male"},
    "students_gender_female": {"uz": "Ayol", "ru": "Женский", "en": "Female"},
    "students_add_button": {"uz": "Qo'shish", "ru": "Добавить", "en": "Add"},
    "students_view_profile": {"uz": "Profilni ko'rish", "ru": "Просмотр профиля", "en": "View profile"},
    "students_confirm_delete": {"uz": "Bu o'quvchini o'chirishga ishonchingiz komilmi?", "ru": "Вы уверены, что хотите удалить этого ученика?", "en": "Are you sure you want to delete this student?"},

    # ---------- Attendance ----------
    "attendance_title": {"uz": "Kunlik Davomat", "ru": "Ежедневная посещаемость", "en": "Daily Attendance"},
    "attendance_date_label": {"uz": "Sana", "ru": "Дата", "en": "Date"},
    "attendance_present": {"uz": "Keldi", "ru": "Присутствовал", "en": "Present"},
    "attendance_absent": {"uz": "Kelmadi", "ru": "Отсутствовал", "en": "Absent"},
    "attendance_empty_class": {"uz": "Bu sinfda o'quvchi topilmadi.", "ru": "В этом классе нет учеников.", "en": "No students in this class."},
    "attendance_empty_all": {"uz": "Davomat olish uchun avval o'quvchilar ro'yxatidan o'quvchi qo'shing.", "ru": "Сначала добавьте учеников в список, чтобы отмечать посещаемость.", "en": "Add students to the list first to take attendance."},
    "attendance_save_button": {"uz": "Davomatni saqlash", "ru": "Сохранить посещаемость", "en": "Save attendance"},

    # ---------- Teachers ----------
    "teachers_title": {"uz": "O'qituvchilar tarkibi", "ru": "Список учителей", "en": "Teacher List"},
    "teachers_subject_label": {"uz": "Fani", "ru": "Предмет", "en": "Subject"},
    "teachers_empty": {"uz": "Hozircha o'qituvchilar kiritilmagan.", "ru": "Учителя пока не добавлены.", "en": "No teachers added yet."},

    # ---------- Classrooms ----------
    "classrooms_title": {"uz": "Sinf xonalari tarkibi", "ru": "Список кабинетов", "en": "Classroom List"},
    "classrooms_type_label": {"uz": "Turi", "ru": "Тип", "en": "Type"},
    "classrooms_capacity_label": {"uz": "Sig'imi", "ru": "Вместимость", "en": "Capacity"},
    "classrooms_seats": {"uz": "o'rin", "ru": "мест", "en": "seats"},
    "classrooms_room_no": {"uz": "Xona №", "ru": "Кабинет №", "en": "Room #"},
    "classrooms_empty": {"uz": "Hozircha sinf xonalari kiritilmagan.", "ru": "Кабинеты пока не добавлены.", "en": "No classrooms added yet."},

    # ---------- Grades ----------
    "grades_title": {"uz": "Chorak va Yakuniy Baholar", "ru": "Четвертные и итоговые оценки", "en": "Quarterly & Final Grades"},
    "grades_search_placeholder": {"uz": "O'quvchi yoki fan bo'yicha qidirish...", "ru": "Поиск по ученику или предмету...", "en": "Search by student or subject..."},
    "grades_q1": {"uz": "1-Ch", "ru": "1-я четв.", "en": "Q1"},
    "grades_q2": {"uz": "2-Ch", "ru": "2-я четв.", "en": "Q2"},
    "grades_q3": {"uz": "3-Ch", "ru": "3-я четв.", "en": "Q3"},
    "grades_q4": {"uz": "4-Ch", "ru": "4-я четв.", "en": "Q4"},
    "grades_final": {"uz": "Yakun", "ru": "Итог", "en": "Final"},
    "grades_empty": {"uz": "Hozircha baholar kiritilmagan.", "ru": "Оценки пока не добавлены.", "en": "No grades added yet."},

    # ---------- Student profile (admin ko'rinishi) ----------
    "profile_class": {"uz": "Sinf", "ru": "Класс", "en": "Class"},
    "profile_birth_date": {"uz": "Tug'ilgan sana", "ru": "Дата рождения", "en": "Birth date"},
    "profile_gender": {"uz": "Jinsi", "ru": "Пол", "en": "Gender"},
    "profile_id": {"uz": "JSHSHIR", "ru": "ИНН", "en": "ID number"},
    "profile_grades_title": {"uz": "Baholar", "ru": "Оценки", "en": "Grades"},
    "profile_back_to_list": {"uz": "Ro'yxatga qaytish", "ru": "Вернуться к списку", "en": "Back to list"},
    "profile_subject_name": {"uz": "Fan nomi", "ru": "Название предмета", "en": "Subject"},
    "profile_quarterly_final_grades": {"uz": "Choraklik va Yakuniy Baholar", "ru": "Четвертные и итоговые оценки", "en": "Quarterly & Final Grades"},

    # ---------- Timetable ----------
    "timetable_title": {"uz": "Dars Jadvali", "ru": "Расписание уроков", "en": "Class Timetable"},
    "timetable_empty": {"uz": "Hozircha dars jadvali kiritilmagan.", "ru": "Расписание пока не добавлено.", "en": "No timetable added yet."},

    # ---------- Notifications ----------
    "notifications_title": {"uz": "Bildirishnomalar", "ru": "Уведомления", "en": "Notifications"},
    "notifications_empty": {"uz": "Hozircha bildirishnomalar yo'q.", "ru": "Пока нет уведомлений.", "en": "No notifications yet."},

    # ---------- My profile (o'quvchi kabineti) ----------
    "my_profile_class_label": {"uz": "Sinf", "ru": "Класс", "en": "Class"},
    "my_profile_id_label": {"uz": "JSHSHIR", "ru": "ИНН", "en": "ID number"},
    "my_profile_unassigned": {"uz": "belgilanmagan", "ru": "не указан", "en": "not set"},
    "my_profile_attendance_rate": {"uz": "Davomat foizi", "ru": "Процент посещаемости", "en": "Attendance rate"},
    "my_profile_subject_count": {"uz": "Fanlar soni", "ru": "Количество предметов", "en": "Number of subjects"},
    "my_profile_grades_title": {"uz": "Mening baholarim", "ru": "Мои оценки", "en": "My Grades"},
    "my_profile_grades_empty": {"uz": "Hozircha baholaringiz kiritilmagan.", "ru": "Ваши оценки пока не добавлены.", "en": "No grades entered yet."},
    "my_profile_schedule_title": {"uz": "Dars jadvalim", "ru": "Моё расписание", "en": "My Schedule"},
    "my_profile_schedule_empty": {"uz": "Sizning sinfingiz uchun dars jadvali hali kiritilmagan.", "ru": "Расписание для вашего класса пока не добавлено.", "en": "No schedule added for your class yet."},
    "my_profile_attendance_title": {"uz": "Davomat tarixi", "ru": "История посещаемости", "en": "Attendance History"},
    "my_profile_attendance_empty": {"uz": "Hozircha davomat yozuvlari yo'q.", "ru": "Записей о посещаемости пока нет.", "en": "No attendance records yet."},

    # ---------- Backup ----------
    "backup_title": {"uz": "Zaxira nusxalash", "ru": "Резервное копирование", "en": "Backup"},
    "backup_count": {"uz": "ta zaxira", "ru": "копий", "en": "backups"},
    "backup_current_size": {"uz": "Joriy baza hajmi", "ru": "Текущий размер базы", "en": "Current database size"},
    "backup_auto_note": {"uz": "Har {h} soatda avtomatik zaxira olinadi, oxirgi {n} tasi saqlanadi.", "ru": "Автоматическая копия создаётся каждые {h} ч., хранятся последние {n}.", "en": "Automatic backup every {h}h, last {n} kept."},
    "backup_create_now": {"uz": "Hozir zaxira olish", "ru": "Создать копию сейчас", "en": "Back up now"},
    "backup_existing_title": {"uz": "Mavjud zaxiralar", "ru": "Существующие копии", "en": "Existing Backups"},
    "backup_restore": {"uz": "Tiklash", "ru": "Восстановить", "en": "Restore"},
    "backup_confirm_restore": {"uz": "DIQQAT: Joriy baza shu zaxira bilan almashtiriladi. Bu amalni ortga qaytarib bo'lmaydi. Davom etasizmi?", "ru": "ВНИМАНИЕ: текущая база будет заменена этой копией. Действие необратимо. Продолжить?", "en": "WARNING: the current database will be replaced by this backup. This cannot be undone. Continue?"},
    "backup_confirm_delete": {"uz": "Ushbu zaxira nusxa o'chirilsinmi?", "ru": "Удалить эту резервную копию?", "en": "Delete this backup?"},
    "backup_empty": {"uz": "Hozircha zaxira nusxalar yo'q. Yuqoridagi tugma orqali birinchisini yarating.", "ru": "Резервных копий пока нет. Создайте первую с помощью кнопки выше.", "en": "No backups yet. Create your first one using the button above."},

    # ---------- AI report ----------
    "ai_report_title": {"uz": "SI Hisobot", "ru": "ИИ-отчёт", "en": "AI Report"},
    "ai_report_connected": {"uz": "API ulangan", "ru": "API подключён", "en": "API connected"},
    "ai_report_not_connected": {"uz": "API sozlanmagan", "ru": "API не настроен", "en": "API not configured"},
    "ai_report_key_needed_title": {"uz": "Anthropic API kaliti kerak", "ru": "Требуется ключ API Anthropic", "en": "Anthropic API key required"},
    "ai_report_key_needed_desc": {"uz": "SI hisobot yaratish uchun Anthropic API kaliti kerak. Uni console.anthropic.com saytidan olishingiz mumkin.", "ru": "Для создания ИИ-отчёта нужен ключ API Anthropic. Получить его можно на console.anthropic.com.", "en": "An Anthropic API key is needed to generate AI reports. Get one at console.anthropic.com."},
    "ai_report_save_key": {"uz": "Saqlash", "ru": "Сохранить", "en": "Save"},
    "ai_report_current_key": {"uz": "Joriy kalit", "ru": "Текущий ключ", "en": "Current key"},
    "ai_report_generate": {"uz": "Yangi hisobot yaratish", "ru": "Создать новый отчёт", "en": "Generate new report"},
    "ai_report_change_key": {"uz": "API kalitni almashtirish", "ru": "Изменить API ключ", "en": "Change API key"},
    "ai_report_update": {"uz": "Yangilash", "ru": "Обновить", "en": "Update"},
    "ai_report_history_title": {"uz": "Hisobotlar tarixi", "ru": "История отчётов", "en": "Report History"},
    "ai_report_confirm_delete": {"uz": "Ushbu hisobot o'chirilsinmi?", "ru": "Удалить этот отчёт?", "en": "Delete this report?"},
    "ai_report_empty": {"uz": "Hozircha hisobot yaratilmagan. Yuqoridagi tugma orqali birinchisini generatsiya qiling.", "ru": "Отчётов пока нет. Создайте первый с помощью кнопки выше.", "en": "No reports yet. Generate your first one using the button above."},

    # ---------- Settings hub ----------
    "settings_title": {"uz": "Sozlamalar", "ru": "Настройки", "en": "Settings"},
    "settings_profile": {"uz": "Profil", "ru": "Профиль", "en": "Profile"},
    "settings_language_appearance": {"uz": "Til va ko'rinish", "ru": "Язык и оформление", "en": "Language & Appearance"},
    "settings_security": {"uz": "Xavfsizlik", "ru": "Безопасность", "en": "Security"},
    "settings_notifications": {"uz": "Bildirishnomalar", "ru": "Уведомления", "en": "Notifications"},
    "settings_school": {"uz": "Maktab sozlamalari", "ru": "Настройки школы", "en": "School Settings"},
    "settings_data": {"uz": "Ma'lumotlar", "ru": "Данные", "en": "Data"},
    "settings_about": {"uz": "Dastur haqida", "ru": "О приложении", "en": "About"},
    "settings_logout": {"uz": "Chiqish", "ru": "Выйти", "en": "Log out"},

    # ---------- Settings: Profile ----------
    "sp_title": {"uz": "Profil", "ru": "Профиль", "en": "Profile"},
    "sp_full_name": {"uz": "Ism va familiya", "ru": "Имя и фамилия", "en": "Full name"},
    "sp_phone": {"uz": "Telefon raqam", "ru": "Номер телефона", "en": "Phone number"},
    "sp_email": {"uz": "Email", "ru": "Эл. почта", "en": "Email"},
    "sp_position": {"uz": "Lavozim", "ru": "Должность", "en": "Position"},
    "sp_position_placeholder": {"uz": "Masalan: Direktor, Zavuch, O'qituvchi", "ru": "Напр.: Директор, Завуч, Учитель", "en": "e.g. Principal, Vice-Principal, Teacher"},
    "sp_login_label": {"uz": "Login (o'zgartirib bo'lmaydi)", "ru": "Логин (нельзя изменить)", "en": "Username (cannot be changed)"},
    "sp_avatar_note": {"uz": "Profil rasmi (avatar) yuklash imkoniyati keyingi yangilanishda qo'shiladi.", "ru": "Загрузка фото профиля будет добавлена в следующем обновлении.", "en": "Profile picture upload will be added in a future update."},

    # ---------- Settings: Appearance ----------
    "sa_title": {"uz": "Til va ko'rinish", "ru": "Язык и оформление", "en": "Language & Appearance"},
    "sa_language_label": {"uz": "Til", "ru": "Язык", "en": "Language"},
    "sa_uz": {"uz": "O'zbek", "ru": "Узбекский", "en": "Uzbek"},
    "sa_ru": {"uz": "Rus", "ru": "Русский", "en": "Russian"},
    "sa_en": {"uz": "Ingliz", "ru": "Английский", "en": "English"},
    "sa_appearance_label": {"uz": "Ko'rinish", "ru": "Оформление", "en": "Appearance"},
    "sa_light": {"uz": "Kunduzgi", "ru": "Светлая", "en": "Light"},
    "sa_dark": {"uz": "Tungi rejim", "ru": "Тёмная тема", "en": "Dark mode"},
    "sa_note": {"uz": "Eslatma: sahifa ichidagi ba'zi elementlar hali ham fon rangini to'liq o'zgartirmasligi mumkin - bu keyingi bosqichda takomillashtiriladi.", "ru": "Примечание: некоторые элементы страницы могут пока не менять фон полностью - это будет улучшено позже.", "en": "Note: some page elements may not fully change background yet - this will be improved later."},

    # ---------- Settings: Security ----------
    "ss_title": {"uz": "Xavfsizlik", "ru": "Безопасность", "en": "Security"},
    "ss_change_password": {"uz": "Parolni o'zgartirish", "ru": "Изменить пароль", "en": "Change password"},
    "ss_new_password_placeholder": {"uz": "Yangi parol (kamida 6 belgi)", "ru": "Новый пароль (мин. 6 символов)", "en": "New password (min 6 characters)"},
    "ss_update_password": {"uz": "Parolni yangilash", "ru": "Обновить пароль", "en": "Update password"},
    "ss_2fa_note": {"uz": "Ikki bosqichli himoya (2FA) hozircha mavjud emas - bu keyingi bosqichda qo'shiladigan xavfsizlik funksiyasi.", "ru": "Двухфакторная защита (2FA) пока недоступна - будет добавлена позже.", "en": "Two-factor authentication (2FA) isn't available yet - it will be added in a future update."},
    "ss_history_title": {"uz": "So'nggi kirishlar", "ru": "Последние входы", "en": "Recent Logins"},
    "ss_unknown_ip": {"uz": "noma'lum", "ru": "неизвестно", "en": "unknown"},
    "ss_history_empty": {"uz": "Kirish tarixi hali yo'q.", "ru": "Истории входов пока нет.", "en": "No login history yet."},

    # ---------- Settings: Notifications ----------
    "sn_title": {"uz": "Bildirishnomalar", "ru": "Уведомления", "en": "Notifications"},
    "sn_grades": {"uz": "Yangi baholar haqida xabar", "ru": "Уведомление о новых оценках", "en": "New grade notifications"},
    "sn_attendance": {"uz": "Davomat haqida xabar", "ru": "Уведомление о посещаемости", "en": "Attendance notifications"},
    "sn_homework": {"uz": "Vazifalar eslatmasi", "ru": "Напоминание о заданиях", "en": "Homework reminders"},
    "sn_note": {"uz": "Bu sahifada tanlovingiz saqlanadi, lekin xabarlarni haqiqatan Telegram bot yoki SMS orqali yuborish alohida sozlash talab qiladi.", "ru": "Ваш выбор сохраняется, но фактическая отправка через Telegram-бот или SMS требует отдельной настройки.", "en": "Your choice is saved, but actually sending via Telegram bot or SMS requires separate setup."},

    # ---------- Settings: School ----------
    "sc_title": {"uz": "Maktab sozlamalari", "ru": "Настройки школы", "en": "School Settings"},
    "sc_name": {"uz": "Maktab nomi", "ru": "Название школы", "en": "School name"},
    "sc_name_placeholder": {"uz": "Masalan: 21-umumiy o'rta ta'lim maktabi", "ru": "Напр.: Школа №21", "en": "e.g. School No. 21"},
    "sc_address": {"uz": "Manzil", "ru": "Адрес", "en": "Address"},
    "sc_address_placeholder": {"uz": "Viloyat, tuman, ko'cha", "ru": "Область, район, улица", "en": "Region, district, street"},
    "sc_academic_year": {"uz": "O'quv yili", "ru": "Учебный год", "en": "Academic year"},
    "sc_grading_system": {"uz": "Baholash tizimi", "ru": "Система оценивания", "en": "Grading system"},
    "sc_grading_5": {"uz": "5 ballik tizim", "ru": "5-балльная система", "en": "5-point system"},
    "sc_grading_100": {"uz": "100 ballik tizim", "ru": "100-балльная система", "en": "100-point system"},
    "sc_grading_note": {"uz": "Eslatma: bu sozlama hozircha faqat saqlanadi - baho kiritish formalarini shu tizimga moslashtirish keyingi bosqichda amalga oshiriladi.", "ru": "Примечание: настройка пока только сохраняется - адаптация форм оценок будет позже.", "en": "Note: this setting is only saved for now - adapting grade entry forms will happen later."},
    "sc_other_note": {"uz": "Sinflar/fanlarni boshqarish va rollar/ruxsatlar tahriri hozircha mavjud emas - bular alohida bo'lim sifatida keyingi bosqichda qo'shiladi.", "ru": "Управление классами/предметами и ролями пока недоступно - будет добавлено позже.", "en": "Managing classes/subjects and roles isn't available yet - it will be added later."},

    # ---------- Settings: Data ----------
    "sd_title": {"uz": "Ma'lumotlar", "ru": "Данные", "en": "Data"},
    "sd_export_title": {"uz": "Excel'ga eksport qilish", "ru": "Экспорт в Excel", "en": "Export to Excel"},
    "sd_export_students": {"uz": "O'quvchilar ro'yxati", "ru": "Список учеников", "en": "Student list"},
    "sd_export_grades": {"uz": "Baholar", "ru": "Оценки", "en": "Grades"},
    "sd_export_attendance": {"uz": "Davomat", "ru": "Посещаемость", "en": "Attendance"},
    "sd_export_note": {"uz": "CSV formatida yuklanadi - Excel, Google Sheets orqali ochish mumkin. PDF eksport keyingi bosqichda qo'shiladi.", "ru": "Загружается в формате CSV - можно открыть в Excel, Google Таблицах. Экспорт в PDF будет добавлен позже.", "en": "Downloads as CSV - open with Excel or Google Sheets. PDF export coming later."},
    "sd_backup_title": {"uz": "Zaxira nusxa", "ru": "Резервная копия", "en": "Backup"},
    "sd_backup_link": {"uz": "Zaxira nusxalash bo'limiga o'tish", "ru": "Перейти к резервному копированию", "en": "Go to backup section"},

    # ---------- Settings: About ----------
    "sab_title": {"uz": "Dastur haqida", "ru": "О приложении", "en": "About"},
    "sab_version": {"uz": "Versiya", "ru": "Версия", "en": "Version"},
    "sab_updates": {"uz": "Yangilanishlar", "ru": "Обновления", "en": "Updates"},
    "sab_updates_desc": {"uz": "Qidiruv/filtr, Dashboard grafiklar, Zaxira tizimi, SI hisobot, Kengaytirilgan sozlamalar qo'shildi.", "ru": "Добавлены поиск/фильтры, графики на панели, система резервного копирования, ИИ-отчёты, расширенные настройки.", "en": "Added search/filters, dashboard charts, backup system, AI reports, expanded settings."},
    "sab_terms": {"uz": "Foydalanish shartlari", "ru": "Условия использования", "en": "Terms of Use"},
    "sab_terms_desc": {"uz": "Ushbu tizim maktab ichki foydalanishi uchun mo'ljallangan. Ma'lumotlar mahalliy serverda saqlanadi.", "ru": "Данная система предназначена для внутреннего использования школы. Данные хранятся на локальном сервере.", "en": "This system is intended for internal school use. Data is stored on a local server."},
    "sab_help": {"uz": "Yordam markazi", "ru": "Центр поддержки", "en": "Help Center"},
    "sab_help_desc": {"uz": "Muammo yuzaga kelsa, tizim administratoriga murojaat qiling.", "ru": "При возникновении проблем обратитесь к администратору системы.", "en": "If you run into an issue, please contact your system administrator."},
}


def translate(key, lang='uz'):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get('uz') or key
