"""
Seed the Project table with the projects that used to be hardcoded in
portfolio/content.py. The data is copied here as a literal on purpose:
a migration must keep working even after content.py changes.
"""

from django.db import migrations

PROJECTS = [{'slug': 'buildops',
  'tier': 'featured',
  'order': 0,
  'status': 'live',
  'link': 'https://sofibrat.uz',
  'github': '',
  'tags': 'Django, PostgreSQL, Nginx + Gunicorn, PWA, Claude API',
  'title_uz': 'BuildOps — Qurilish ERP tizimi',
  'title_ru': 'BuildOps — ERP-система для стройкомпании',
  'title_en': 'BuildOps — Construction ERP System',
  'desc_uz': "Qurilish kompaniyasi uchun to'liq boshqaruv tizimi: direktor, prorab, geodezist, buxgalter va "
             'ishchi uchun alohida panellar, real vaqtdagi moliyaviy hisobotlar, yuk tashish logistikasi '
             "moduli va Claude AI asosidagi ichki yordamchi. Hetzner VPS'da nginx + gunicorn orqali "
             'production rejimida ishlaydi.',
  'desc_ru': 'Полноценная система управления для строительной компании: отдельные панели для директора, '
             'прораба, геодезиста, бухгалтера и рабочих, финансовая отчётность в реальном времени, модуль '
             'логистики грузоперевозок и встроенный ИИ-помощник на базе Claude API. Работает в продакшене на '
             'Hetzner VPS (nginx + gunicorn).',
  'desc_en': 'A full management system for a construction company: separate role-based dashboards for the '
             'director, site manager, surveyor, accountant and field workers, real-time financial reporting, '
             'a hauling/logistics module, and a built-in AI assistant powered by the Claude API. Running in '
             'production on a Hetzner VPS behind nginx + gunicorn.',
  'highlights_uz': "6 ta rol uchun alohida panel (direktor, prorab, PTO, geodezist, buxgalter, ta'minotchi) "
                   '+ ishchilar uchun mobil PWA\n'
                   'Ishchilar davomati: geofence va kamera orqali tasdiqlangan kelish/ketish\n'
                   "Claude API asosidagi AI-yordamchi: davomat, maosh, texnika va yoqilg'i bo'yicha "
                   'savollarga javob beradi\n'
                   "Asfalt tashish logistikasi: haydovchi PWA, TTN rasmi, tarif × masofa × tonna bo'yicha "
                   'avtomatik narxlash\n'
                   'Ikki production muhit: Hetzner VPS (PostgreSQL, nginx + gunicorn) va PythonAnywhere',
  'highlights_ru': 'Отдельные панели для 6 ролей (директор, прораб, ПТО, геодезист, бухгалтер, снабженец) + '
                   'мобильное PWA для рабочих\n'
                   'Учёт посещаемости: приход/уход с геозоной и подтверждением камерой\n'
                   'ИИ-помощник на Claude API: отвечает на вопросы о посещаемости, зарплате, технике и '
                   'топливе\n'
                   'Логистика перевозки асфальта: PWA для водителей, фото ТТН, автоматический расчёт по '
                   'тарифу × расстоянию × тоннажу\n'
                   'Две production-среды: Hetzner VPS (PostgreSQL, nginx + gunicorn) и PythonAnywhere',
  'highlights_en': 'Dedicated dashboards for 6 roles (director, site manager, planning, surveyor, '
                   'accountant, supplier) + a mobile PWA for field workers\n'
                   'Attendance with geofenced, camera-verified check-in and check-out\n'
                   'AI assistant on the Claude API that answers questions about attendance, payroll, '
                   'equipment and fuel\n'
                   'Asphalt-hauling logistics: driver PWA, waybill photos, automatic pricing by tariff × '
                   'distance × tonnage\n'
                   'Two production environments: Hetzner VPS (PostgreSQL, nginx + gunicorn) and '
                   'PythonAnywhere'},
 {'slug': 'eltaom',
  'tier': 'main',
  'order': 10,
  'status': 'dev',
  'link': '',
  'github': '',
  'tags': 'Django, django-tenants, PostgreSQL, Flutter',
  'title_uz': 'Eltaom — restoranlar uchun SaaS platforma',
  'title_ru': 'Eltaom — SaaS-платформа для ресторанов',
  'title_en': 'Eltaom — Restaurant SaaS Platform',
  'desc_uz': "Bir nechta restoran uchun mo'ljallangan multi-tenant SaaS tizimi (django-tenants asosida) — "
             "har bir mijoz o'z alohida ma'lumotlar bazasiga ega. Mijoz va kuryer uchun Flutter ilovalari, "
             'boshqaruv/ofitsiant/oshxona uchun veb-panellar rejalashtirilmoqda.',
  'desc_ru': 'Multi-tenant SaaS-система для сети ресторанов на базе django-tenants — у каждого клиента '
             'отдельная база данных. Планируются приложения на Flutter для клиентов и курьеров, а также '
             'веб-панели для менеджмента, официантов и кухни.',
  'desc_en': 'A multi-tenant SaaS system for restaurants built on django-tenants, giving each client an '
             'isolated database. Flutter apps for customers and couriers are planned, alongside web '
             'dashboards for management, waitstaff and the kitchen.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'lingvoapp',
  'tier': 'main',
  'order': 20,
  'status': 'dev',
  'link': '',
  'github': '',
  'tags': 'Django, Telegram Mini App, SM-2, PostgreSQL',
  'title_uz': "LingvoApp — ingliz tili o'rganish platformasi",
  'title_ru': 'LingvoApp — платформа для изучения английского',
  'title_en': 'LingvoApp — English Learning Platform',
  'desc_uz': "O'zbek foydalanuvchilari uchun Telegram Mini App ko'rinishidagi ingliz tili o'rganish "
             "platformasi. So'z boyligini mustahkamlash uchun SM-2 space-repetition algoritmi asosida "
             'qurilgan. Hozircha 8 bosqichdan 6-tasi tayyor.',
  'desc_ru': 'Платформа для изучения английского языка в формате Telegram Mini App для узбекоязычных '
             'пользователей. В основе — алгоритм интервального повторения SM-2 для запоминания слов. Готово '
             '6 из 8 этапов.',
  'desc_en': 'An English-learning platform built as a Telegram Mini App for Uzbek-speaking learners, using '
             'the SM-2 spaced-repetition algorithm for vocabulary retention. Currently 6 of 8 planned stages '
             'are complete.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'roma-food',
  'tier': 'main',
  'order': 30,
  'status': 'live',
  'link': 'https://romafood.pythonanywhere.com',
  'github': 'https://github.com/ShohzoDev0108/roma-food',
  'tags': 'Django, JavaScript, PythonAnywhere',
  'title_uz': 'Roma Food — QR-menyu tizimi',
  'title_ru': 'Roma Food — система QR-меню',
  'title_en': 'Roma Food — QR Menu System',
  'desc_uz': "Toshkentdagi fastfood restorani uchun QR-kod orqali ochiladigan raqamli menyu. O'zbek va rus "
             "tillarida, mijozning o'z savatchasi va ochilish splash-ekrani bilan. PythonAnywhere'da "
             "production'da ishlaydi.",
  'desc_ru': 'Цифровое меню по QR-коду для фастфуд-ресторана в Ташкенте. Двуязычное (узбекский/русский), с '
             'собственной корзиной на JS и заставкой при открытии. Работает в продакшене на PythonAnywhere.',
  'desc_en': 'A QR-code digital menu for a fast-food restaurant in Tashkent. Bilingual (Uzbek/Russian), with '
             'a custom JS shopping cart and a branded splash screen. Live in production on PythonAnywhere.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'geodezistman',
  'tier': 'main',
  'order': 40,
  'status': 'live',
  'link': 'https://geodezistman.uz',
  'github': '',
  'tags': 'Django, PostgreSQL, Render',
  'title_uz': "Geodezistman.uz — geodezistlar uchun onlayn ta'lim",
  'title_ru': 'Geodezistman.uz — онлайн-обучение для геодезистов',
  'title_en': 'Geodezistman.uz — E-Learning for Surveyors',
  'desc_uz': "O'zbek geodezistlari uchun onlayn kurslar platformasi. Render'da bepul PostgreSQL bazasi bilan "
             "joylashtirilgan, o'ziga xos 'chizma' uslubidagi dizayn va shaxsiy domen bilan.",
  'desc_ru': 'Платформа онлайн-курсов для узбекских геодезистов. Развёрнута на Render с бесплатной базой '
             'PostgreSQL, фирменный дизайн в стиле чертежа и собственный домен.',
  'desc_en': 'An online-course platform for Uzbek land surveyors. Deployed on Render with a free PostgreSQL '
             'database, a custom blueprint-style visual theme, and its own domain.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'geo-portfolio',
  'tier': 'main',
  'order': 50,
  'status': 'live',
  'link': 'https://geoollomurod.pythonanywhere.com',
  'github': '',
  'tags': 'Django, WhiteNoise, PythonAnywhere',
  'title_uz': 'Geodezist portfolio sayti',
  'title_ru': 'Портфолио-сайт геодезиста',
  'title_en': 'Surveyor Portfolio Site',
  'desc_uz': "Mustaqil geodezist uchun shaxsiy portfolio sayti — oltita model asosida qurilgan, 'chizma' "
             'uslubidagi dizayn va WhiteNoise orqali statik fayllarni uzatish bilan.',
  'desc_ru': 'Персональный сайт-портфолио для независимого геодезиста — построен на шести моделях, оформлен '
             'в стиле чертежа, статика раздаётся через WhiteNoise.',
  'desc_en': 'A personal portfolio site for an independent land surveyor — built around six Django models, '
             'styled with a blueprint theme, static files served via WhiteNoise.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'english-bot',
  'tier': 'other',
  'order': 60,
  'status': 'tool',
  'link': '',
  'github': '',
  'tags': 'Python, aiogram 3.x, SQLAlchemy 2.x, PostgreSQL',
  'title_uz': "English Bot — Telegram ta'lim boti",
  'title_ru': 'English Bot — обучающий Telegram-бот',
  'title_en': 'English Bot — Telegram Learning Bot',
  'desc_uz': "Ingliz tili o'rganish uchun Telegram bot skeleti — aiogram 3.x, SQLAlchemy 2.x va PostgreSQL "
             'asosida qurilgan.',
  'desc_ru': 'Каркас Telegram-бота для изучения английского языка на базе aiogram 3.x, SQLAlchemy 2.x и '
             'PostgreSQL.',
  'desc_en': 'A Telegram bot scaffold for English learning, built with aiogram 3.x, SQLAlchemy 2.x and '
             'PostgreSQL.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''},
 {'slug': 'n8n-workflows',
  'tier': 'other',
  'order': 70,
  'status': 'tool',
  'link': '',
  'github': '',
  'tags': 'n8n, Automation, AI',
  'title_uz': "n8n avtomatlashtirish workflow'lari",
  'title_ru': 'Автоматизация на n8n',
  'title_en': 'n8n Automation Workflows',
  'desc_uz': "Telegram uchun yangiliklar agregatori (Jaccard o'xshashlik algoritmi bilan takrorlanishni "
             'aniqlash) va AI-node asosida rasmlardagi watermark koordinatalarini avtomatik aniqlovchi '
             'workflow.',
  'desc_ru': 'Агрегатор новостей для Telegram с определением дублей по алгоритму сходства Жаккара, а также '
             'workflow для автоматического определения координат водяного знака на изображениях через '
             'AI-node.',
  'desc_en': 'A Telegram news aggregator with duplicate detection using Jaccard similarity, plus a workflow '
             'that uses an AI node to auto-detect watermark coordinates on images.',
  'highlights_uz': '',
  'highlights_ru': '',
  'highlights_en': ''}]


def seed(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    for row in PROJECTS:
        Project.objects.update_or_create(slug=row["slug"], defaults=row)


def unseed(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    Project.objects.filter(slug__in=[r["slug"] for r in PROJECTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0003_project_contactmessage"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
