"""
The site's interface copy in UZ/RU/EN — one place to edit every label.

Projects and the owner's name live in the database (admin panel), not here.
Uzbek copy uses the updated Latin alphabet (Ş, Ç, Ö, Ğ — see uz_alphabet.py);
project and brand names keep their own spelling (Oqqushlar, oqqushlar.uz).
"""

SUPPORTED_LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"

STRINGS = {
    "uz": {
        "skip_link": "Asosiy kontentga ötiş",
        "lang_group_label": "Til",
        "hero_role": "Django backend muhandisi",
        "hero_headline_pre": "Bizneslar har kuni tayanadigan ",
        "hero_headline_em": "tizimlarni",
        "hero_headline_post": " quraman.",
        "hero_tagline": "ERP, SaaS va biznes platformalar — arxitekturadan serverga qöyişgaça, boşidan oxirigaça özim.",
        "hero_cta_projects": "Loyihalar",
        "socials_label": "Ijtimoiy tarmoqlar",
        "projects_title": "Loyihalar",
        "opens_new_tab": "yangi oynada oçiladi",
        "status_live": "Işlamoqda",
        "status_launch": "Işga tuşiş arafasida",
        "status_dev": "Işlab çiqilmoqda",
        "status_tool": "Içki vosita",
        "founder_label": "Asosçi",
        "contact_title": "Loyihangiz bormi?",
        "contact_desc": "Qisqaça yozing — qanday quriş mumkinligini va muddatini aytaman.",
        "contact_telegram_btn": "Telegram'da yozing",
    },
    "ru": {
        "skip_link": "Перейти к содержимому",
        "lang_group_label": "Язык",
        "hero_role": "Django backend-инженер",
        "hero_headline_pre": "Строю ",
        "hero_headline_em": "системы",
        "hero_headline_post": ", на которых бизнес работает каждый день.",
        "hero_tagline": "ERP, SaaS и бизнес-платформы — от архитектуры до запуска на сервере, от начала до конца сам.",
        "hero_cta_projects": "Проекты",
        "socials_label": "Соцсети",
        "projects_title": "Проекты",
        "opens_new_tab": "откроется в новой вкладке",
        "status_live": "В продакшене",
        "status_launch": "Скоро запуск",
        "status_dev": "В разработке",
        "status_tool": "Внутренний инструмент",
        "founder_label": "Основатель",
        "contact_title": "Есть проект?",
        "contact_desc": "Опишите в двух словах — расскажу, как это построить и сколько времени займёт.",
        "contact_telegram_btn": "Написать в Telegram",
    },
    "en": {
        "skip_link": "Skip to content",
        "lang_group_label": "Language",
        "hero_role": "Django Backend Engineer",
        "hero_headline_pre": "I build the ",
        "hero_headline_em": "systems",
        "hero_headline_post": " businesses run on every day.",
        "hero_tagline": "ERP systems, SaaS and business platforms — from architecture to the live server, built end to end by me.",
        "hero_cta_projects": "Projects",
        "socials_label": "Social profiles",
        "projects_title": "Projects",
        "opens_new_tab": "opens in a new tab",
        "status_live": "Live",
        "status_launch": "Launching soon",
        "status_dev": "In development",
        "status_tool": "Internal tool",
        "founder_label": "Founder",
        "contact_title": "Have a project?",
        "contact_desc": "Tell me about it in a few lines and I'll say how I'd build it and how long it would take.",
        "contact_telegram_btn": "Message me on Telegram",
    },
}

# One line under the headline — the tools the projects above are built with.
STACK = ["Python", "Django", "PostgreSQL", "nginx", "Linux", "Cloudflare"]

LANGUAGE_NAMES = {"uz": "Özbekça", "ru": "Русский", "en": "English"}
OG_LOCALES = {"uz": "uz_UZ", "ru": "ru_RU", "en": "en_US"}
