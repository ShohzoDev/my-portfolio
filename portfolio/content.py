"""
The site's copy in UZ/RU/EN — one place to edit every label and text.

In the About paragraphs, *stars* mark a key phrase (shown highlighted) and a
project name such as Zebest becomes a link to its site automatically — see
the `highlight` filter in templatetags/portfolio_extras.py.

Projects and the owner's name live in the database (admin panel), not here.
Uzbek copy uses the updated Latin alphabet (Ş, Ç, Ö, Ğ — see uz_alphabet.py);
project and brand names keep their own spelling (Oqqushlar, oqqushlar.uz).
"""

SUPPORTED_LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"

STRINGS = {
    "uz": {
        "skip_link": "Asosiy kontentga ötiş",
        "menu_label": "Menyu",
        "lang_group_label": "Til",
        "nav_about": "Men haqimda",
        "nav_services": "Xizmatlar",
        "nav_projects": "Loyihalar",
        "nav_contact": "Aloqa",
        "hero_role": "Django backend muhandisi",
        "side_lead": "Bizneslar har kuni tayanadigan tizimlarni quraman — arxitekturadan serverga qöyişgaça.",
        "hero_tagline": "ERP, SaaS va biznes platformalar — arxitekturadan serverga qöyişgaça, boşidan oxirigaça özim.",
        "hero_status": "Yangi loyihalarga oçiqman",
        "socials_label": "Ijtimoiy tarmoqlar",
        "about_p1": "Men Shohzod — Özbekistonda işlaydigan *Django backend muhandisiman*. Biznes jarayonini tuşunişdan tortib arxitektura, kod, server va xavfsizlikkaça — loyihani *boşidan production'gaça* özim olib boraman.",
        "about_p2": "Hozir restoranlar uçun Zebest platformasining *asosçisiman* va quriliş kompaniyalari uçun BuildBest tizimini rivojlantiryapman. Işga tuşgandan keyin ham tizimni *kuzatib, qöllab-quvvatlab* boraman.",
        "s1_t": "Biznes tizimlari",
        "s1_d": "ERP va CRM: hisob, xodimlar, ombor va moliya — bitta tizimda.",
        "s2_t": "SaaS platformalar",
        "s2_d": "Köp mijozli onlayn xizmatlar: obuna, har mijozga alohida subdomen va admin panel.",
        "s3_t": "Telegram botlar",
        "s3_d": "Bot va Mini App'lar, takroriy işlarni avtomatlaştiriş.",
        "s4_t": "Server va qöllab-quvvatlaş",
        "s4_d": "Linux serverga joylaş, HTTPS, zaxira, monitoring va keyingi qöllab-quvvatlaş.",
        "opens_new_tab": "yangi oynada oçiladi",
        "status_live": "Işlamoqda",
        "status_launch": "Işga tuşiş arafasida",
        "status_dev": "Işlab çiqilmoqda",
        "status_tool": "Içki vosita",
        "founder_label": "Asosçi",
        "contact_title": "Loyihangiz bormi?",
        "contact_desc": "Qisqaça yozing — qanday quriş mumkinligini va muddatini aytaman.",
        "contact_telegram_btn": "Telegram'da yozing",
        "contact_or": "yoki email:",
        "footer_note": "Django va qölda yozilgan CSS'da qurilgan. Şrift — IBM Plex.",
    },
    "ru": {
        "skip_link": "Перейти к содержимому",
        "menu_label": "Меню",
        "lang_group_label": "Язык",
        "nav_about": "Обо мне",
        "nav_services": "Услуги",
        "nav_projects": "Проекты",
        "nav_contact": "Контакты",
        "hero_role": "Django backend-инженер",
        "side_lead": "Строю системы, на которые бизнес опирается каждый день, — от архитектуры до сервера.",
        "hero_tagline": "ERP, SaaS и бизнес-платформы — от архитектуры до запуска на сервере, от начала до конца сам.",
        "hero_status": "Открыт для новых проектов",
        "socials_label": "Соцсети",
        "about_p1": "Я Шохзод — *Django backend-инженер* из Узбекистана. От понимания бизнес-процесса до архитектуры, кода, серверов и безопасности — веду проект сам, *от начала до продакшена*.",
        "about_p2": "Сейчас я *основатель* Zebest — платформы для ресторанов — и развиваю BuildBest, систему для строительных компаний. После запуска продолжаю *следить за системой и поддерживать её*.",
        "s1_t": "Бизнес-системы",
        "s1_d": "ERP и CRM: учёт, сотрудники, склад и финансы — в одной системе.",
        "s2_t": "SaaS-платформы",
        "s2_d": "Мультиклиентские онлайн-сервисы: подписка, свой поддомен для каждого клиента и админ-панель.",
        "s3_t": "Telegram-боты",
        "s3_d": "Боты и Mini App, автоматизация рутинных задач.",
        "s4_t": "Сервер и поддержка",
        "s4_d": "Развёртывание на Linux, HTTPS, резервные копии, мониторинг и дальнейшая поддержка.",
        "opens_new_tab": "откроется в новой вкладке",
        "status_live": "В продакшене",
        "status_launch": "Скоро запуск",
        "status_dev": "В разработке",
        "status_tool": "Внутренний инструмент",
        "founder_label": "Основатель",
        "contact_title": "Есть проект?",
        "contact_desc": "Опишите в двух словах — расскажу, как это построить и сколько времени займёт.",
        "contact_telegram_btn": "Написать в Telegram",
        "contact_or": "или email:",
        "footer_note": "Сделано на Django и написанном вручную CSS. Шрифт — IBM Plex.",
    },
    "en": {
        "skip_link": "Skip to content",
        "menu_label": "Menu",
        "lang_group_label": "Language",
        "nav_about": "About",
        "nav_services": "Services",
        "nav_projects": "Projects",
        "nav_contact": "Contact",
        "hero_role": "Django Backend Engineer",
        "side_lead": "I build the systems businesses rely on every day — from architecture to the server.",
        "hero_tagline": "ERP systems, SaaS and business platforms — from architecture to the live server, built end to end by me.",
        "hero_status": "Open to new projects",
        "socials_label": "Social profiles",
        "about_p1": "I'm Shohzod, a *Django backend engineer* based in Uzbekistan. From understanding the business process to architecture, code, servers and security, I take a project *from scratch to production* myself.",
        "about_p2": "I'm the *founder* of Zebest, a platform for restaurants, and I'm building BuildBest, a system for construction companies. After launch I keep *monitoring and supporting* the system.",
        "s1_t": "Business systems",
        "s1_d": "ERP and CRM: accounting, staff, stock and finance in one system.",
        "s2_t": "SaaS platforms",
        "s2_d": "Multi-tenant online services: subscriptions, a subdomain per client and an admin panel.",
        "s3_t": "Telegram bots",
        "s3_d": "Bots and Mini Apps that automate repetitive work.",
        "s4_t": "Servers and support",
        "s4_d": "Linux deployment, HTTPS, backups, monitoring and ongoing support.",
        "opens_new_tab": "opens in a new tab",
        "status_live": "Live",
        "status_launch": "Launching soon",
        "status_dev": "In development",
        "status_tool": "Internal tool",
        "founder_label": "Founder",
        "contact_title": "Have a project?",
        "contact_desc": "Tell me about it in a few lines and I'll say how I'd build it and how long it would take.",
        "contact_telegram_btn": "Message me on Telegram",
        "contact_or": "or email:",
        "footer_note": "Built with Django and hand-written CSS. Set in IBM Plex.",
    },
}

# The tools the projects are built with (hero line and the About facts).
STACK = ["Python", "Django", "PostgreSQL", "nginx", "Linux", "Cloudflare"]

LANGUAGE_NAMES = {"uz": "Özbekça", "ru": "Русский", "en": "English"}
OG_LOCALES = {"uz": "uz_UZ", "ru": "ru_RU", "en": "en_US"}
