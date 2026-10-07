"""
Content for the compact portfolio:

- three featured projects with case-study pages (BuildOps, Oqqushlar, Zebest —
  Zebest is the current name of the restaurant SaaS previously listed as
  "Eltaom"),
- every other project becomes a one-line entry in "Boshqa ishlar",
- the surveyor's portfolio site is hidden (not deleted),
- the BuildOps public link is removed so the client's name is not published
  without consent — add it back in the admin if the client agrees,
- the About text moves into SiteProfile so it can be edited in the admin.

Everything stays editable in the admin panel afterwards.
"""

from django.db import migrations

ABOUT = {
    "uz": (
        "Men Shohzod — O'zbekistonda ishlaydigan Django backend muhandisiman. Biznes jarayonini "
        "tushunishdan tortib arxitektura, kod, server va xavfsizlikkacha — tizimni boshidan "
        "production'gacha o'zim olib boraman va ishga tushgandan keyin ham qo'llab-quvvatlayman. "
        "Hozir qurilish ERP'si, to'y taklifnomalari SaaS'i va restoranlar platformasi ustida ishlayapman."
    ),
    "ru": (
        "Я Шохзод — Django backend-инженер из Узбекистана. От понимания бизнес-процесса до архитектуры, "
        "кода, серверов и безопасности — сам веду систему от идеи до продакшена и поддерживаю её после "
        "запуска. Сейчас работаю над ERP для строительства, SaaS для свадебных приглашений и платформой "
        "для ресторанов."
    ),
    "en": (
        "I'm Shohzod, a Django backend engineer based in Uzbekistan. From understanding the business "
        "process to architecture, code, servers and security, I take systems from idea to production "
        "myself and keep supporting them after launch. Right now I'm working on a construction ERP, a "
        "wedding-invitation SaaS and a restaurant platform."
    ),
}

FEATURED = {
    "buildops": {
        "order": 1,
        "status": "live",
        "link": "",
        "tags": "Django, PostgreSQL, Kafka, PWA, Claude API, nginx, gunicorn",
        "title": {"uz": "BuildOps", "ru": "BuildOps", "en": "BuildOps"},
        "desc": {
            "uz": "Qurilish kompaniyasi uchun ERP: obyektlar, davomat, texnika, logistika va moliya — bitta tizimda.",
            "ru": "ERP для строительной компании: объекты, табель, техника, логистика и финансы — в одной системе.",
            "en": "An ERP for a construction company: sites, attendance, machinery, hauling and finance in one system.",
        },
        "facts": {
            "uz": "231 test\n6 rol paneli\n1C · GPS · AI",
            "ru": "231 тест\n6 ролевых панелей\n1C · GPS · AI",
            "en": "231 tests\n6 role dashboards\n1C · GPS · AI",
        },
        "problem": {
            "uz": (
                "Qurilish kompaniyasi obyektlar, ishchilar davomati, texnika, asfalt tashish va moliyani "
                "bitta joyda ko'rishi kerak edi. Har bir rol — direktordan ishchigacha — faqat o'ziga "
                "kerakli ekranni ko'rishi, tizim esa kompaniya allaqachon ishlatayotgan 1C buxgalteriya va "
                "GPS-monitoring bilan ma'lumot almashishi lozim edi."
            ),
            "ru": (
                "Строительной компании нужно было видеть объекты, табель рабочих, технику, перевозку асфальта "
                "и финансы в одном месте. Каждая роль — от директора до рабочего — должна видеть только свой "
                "экран, а система — обмениваться данными с уже используемыми 1C:Бухгалтерией и GPS-мониторингом."
            ),
            "en": (
                "A construction company needed its sites, worker attendance, machinery, asphalt hauling and "
                "finances in one place. Every role, from director to worker, should see only its own screen, "
                "and the system had to exchange data with the 1C accounting and GPS tracking the company "
                "already used."
            ),
        },
        "solution": {
            "uz": (
                "Django va PostgreSQL asosidagi monolit: 6 ta rol uchun alohida panel va ishchilar uchun PWA. "
                "Davomat geofence ichida kamera bilan tasdiqlanadi.\n\n"
                "1C yopiq tarmoqda turgani uchun integratsiya teskari yo'nalishda qurildi: 1C ma'lumotni "
                "token-API orqali o'zi yuboradi, avval dry-run rejimida tekshiriladi. GPS ma'lumotlari Kafka "
                "consumer orqali real vaqtda keladi; Kafka vaqtni UTC'da, REST esa mahalliy vaqtda bergani "
                "uchun har biriga alohida parser yozildi.\n\n"
                "Smetani Excel'dan import qilishda AI faqat ustunlar mosligini taklif qiladi — raqamlarning "
                "o'zini emas. Har bir qator «norma × hajm × narx = jami» tekshiruvidan o'tadi, foydalanuvchi "
                "esa natijani tasdiqlash ekranida ko'rib chiqadi."
            ),
            "ru": (
                "Монолит на Django и PostgreSQL: отдельные панели для 6 ролей и PWA для рабочих. Приход на "
                "объект подтверждается камерой внутри геозоны.\n\n"
                "1C стоит в закрытой сети, поэтому интеграция построена в обратную сторону: 1C сам отправляет "
                "данные через токен-API, сначала в режиме dry-run. GPS-данные приходят в реальном времени "
                "через Kafka-консьюмер; Kafka отдаёт время в UTC, а REST — в местном, поэтому для каждого "
                "написан свой парсер.\n\n"
                "При импорте смет из Excel AI предлагает только сопоставление колонок — не сами числа. Каждая "
                "строка проходит проверку «норма × объём × цена = итого», а пользователь подтверждает "
                "результат на отдельном экране."
            ),
            "en": (
                "A Django and PostgreSQL monolith with separate dashboards for 6 roles and a PWA for workers. "
                "Check-ins are confirmed by camera inside a geofence.\n\n"
                "1C lives on a closed network, so the integration runs the other way: 1C pushes data through "
                "a token API, dry-run first. GPS data streams in through a Kafka consumer; Kafka reports UTC "
                "while the REST channel reports local time, so each gets its own parser.\n\n"
                "When estimates are imported from Excel, AI only proposes the column mapping, never the "
                "numbers. Every row must pass norm × volume × price = total, and the user confirms the result "
                "on a review screen."
            ),
        },
        "result": {
            "uz": (
                "Tizim production'da sinov bosqichida ishlayapti. 231 ta avtomatik test, har kecha shifrlangan "
                "zaxira nusxa (tiklash sinab ko'rilgan) va 34 ta tekshiruvli production health-check bor. "
                "Bitta optimizatsiyada xodimlar sahifasidagi so'rovlar soni 128 tadan 4 taga tushdi."
            ),
            "ru": (
                "Система работает в продакшене в режиме пилота. 231 автотест, ночные зашифрованные бэкапы "
                "(восстановление проверено) и production health-check из 34 проверок. Одна оптимизация "
                "сократила число запросов на странице сотрудников со 128 до 4."
            ),
            "en": (
                "The system runs in production as a pilot, with 231 automated tests, nightly encrypted backups "
                "(restore tested) and a 34-check production health check. One optimisation cut the staff page "
                "from 128 queries to 4."
            ),
        },
        "highlights": {
            "uz": (
                "6 ta rol paneli (direktor, PTO, prorab, geodezist, buxgalter, ta'minot) va ishchilar uchun PWA\n"
                "Davomat: geofence ichida kamera bilan tasdiqlangan kelish/ketish\n"
                "1C integratsiyasi: yopiq tarmoqdagi 1C token-API orqali o'zi yuboradi, dry-run rejimi bilan\n"
                "GPS: Kafka consumer (systemd, exponential backoff) va REST kanal, har biriga alohida vaqt parseri\n"
                "AI smeta importi: model faqat ustunlar mosligini taklif qiladi, raqamlar arifmetik tekshiruvdan o'tadi\n"
                "N+1 optimizatsiya: 42 xodimli sahifada 128 → 4 so'rov"
            ),
            "ru": (
                "6 ролевых панелей (директор, ПТО, прораб, геодезист, бухгалтер, снабжение) и PWA для рабочих\n"
                "Табель: приход/уход с подтверждением камерой внутри геозоны\n"
                "Интеграция с 1C: 1C из закрытой сети сам отправляет данные через токен-API, с режимом dry-run\n"
                "GPS: Kafka-консьюмер (systemd, экспоненциальный backoff) и REST-канал, у каждого свой парсер времени\n"
                "AI-импорт смет: модель предлагает только сопоставление колонок, числа проходят арифметическую проверку\n"
                "Оптимизация N+1: 128 → 4 запроса на странице с 42 сотрудниками"
            ),
            "en": (
                "6 role dashboards (director, estimating, site foreman, surveyor, accountant, supply) plus a worker PWA\n"
                "Attendance: check-in/out confirmed by camera inside a geofence\n"
                "1C integration: 1C on a closed network pushes data through a token API, with a dry-run mode\n"
                "GPS: a Kafka consumer (systemd, exponential backoff) plus a REST channel, each with its own time parser\n"
                "AI estimate import: the model only proposes the column mapping; numbers pass an arithmetic check\n"
                "N+1 fix: 128 → 4 queries on a 42-person page"
            ),
        },
    },
    "oqqushlar": {
        "order": 2,
        "status": "live",
        "link": "https://oqqushlar.uz",
        "tags": "Django, PostgreSQL, Cloudflare R2, nginx, gunicorn",
        "title": {"uz": "Oqqushlar", "ru": "Oqqushlar", "en": "Oqqushlar"},
        "desc": {
            "uz": "To'y va marosimlar uchun onlayn taklifnoma SaaS: 19 dizayn, 8 til, RSVP va mehmonlar statistikasi.",
            "ru": "SaaS для онлайн-приглашений на свадьбы и торжества: 19 дизайнов, 8 языков, RSVP и статистика гостей.",
            "en": "A SaaS for online wedding and ceremony invitations: 19 designs, 8 languages, RSVP and guest stats.",
        },
        "facts": {
            "uz": "258 test\n8 til\n19 dizayn",
            "ru": "258 тестов\n8 языков\n19 дизайнов",
            "en": "258 tests\n8 languages\n19 designs",
        },
        "problem": {
            "uz": (
                "To'y yoki marosim egasi bir necha daqiqada o'z taklifnomasini yaratishi, uni mehmonlarga "
                "havola sifatida yuborishi va kim kelishini (RSVP) kuzatishi kerak edi. Platforma Markaziy "
                "Osiyoning bir nechta tilida va 9 xil marosim turi uchun ishlashi lozim edi."
            ),
            "ru": (
                "Организатор свадьбы или торжества должен за несколько минут создать приглашение, разослать "
                "его гостям ссылкой и видеть, кто придёт (RSVP). Платформа должна работать на нескольких "
                "языках Центральной Азии и для 9 типов торжеств."
            ),
            "en": (
                "Hosts of a wedding or ceremony needed to build an invitation in minutes, send it to guests as "
                "a link and track who is coming (RSVP). The platform had to work in several Central Asian "
                "languages and for 9 ceremony types."
            ),
        },
        "solution": {
            "uz": (
                "Ko'p-mijozli Django 5.2 LTS ilova, PostgreSQL 16, media fayllar Cloudflare R2'da. 19 ta "
                "dizayn umumiy CSS va mask-qatlamlar ustiga qurilgan: bu 28 ta qo'shimcha shablonning oldini "
                "oldi va 1 655 qator takroriy CSS'ni olib tashladi.\n\n"
                "Yuklangan rasmlar WebP'ga o'tkaziladi va GPS/EXIF ma'lumotlaridan tozalanadi — 7,3 MB rasm "
                "taxminan 0,9 MB bo'ladi. Rate-limit ma'lumotlar bazasidagi kesh orqali ishlaydi, shuning uchun "
                "barcha gunicorn worker'larda bir xil; poyga holatlari PostgreSQL advisory-lock bilan yopilgan. "
                "Kirill yozuvidagi ismlar o'qiladigan URL'larga transliteratsiya qilinadi."
            ),
            "ru": (
                "Мультитенантное приложение на Django 5.2 LTS, PostgreSQL 16, медиафайлы в Cloudflare R2. "
                "19 дизайнов построены на общем CSS и слоях-масках: это избавило от 28 дополнительных "
                "шаблонов и убрало 1 655 строк дублирующегося CSS.\n\n"
                "Загруженные фото конвертируются в WebP и очищаются от GPS/EXIF — снимок на 7,3 МБ становится "
                "около 0,9 МБ. Rate-limit работает через кеш в базе данных, поэтому одинаков во всех "
                "gunicorn-воркерах; гонки закрыты advisory-lock в PostgreSQL. Кириллические имена "
                "транслитерируются в читаемые URL."
            ),
            "en": (
                "A multi-tenant Django 5.2 LTS app on PostgreSQL 16, with media on Cloudflare R2. The 19 "
                "designs share one CSS base plus mask layers, which avoided 28 extra templates and removed "
                "1,655 lines of duplicated CSS.\n\n"
                "Uploaded photos are converted to WebP and stripped of GPS/EXIF data, so a 7.3 MB photo ends "
                "up around 0.9 MB. Rate limiting runs on a database-backed cache, so it holds across every "
                "gunicorn worker, and race conditions are closed with a PostgreSQL advisory lock. Cyrillic "
                "names are transliterated into readable URLs."
            ),
        },
        "result": {
            "uz": (
                "Platforma oqqushlar.uz manzilida ishlaydi. 258 ta avtomatik test, har kecha shifrlangan "
                "zaxira (14 kunlik va 8 haftalik nusxa, tiklash tekshiruvi bilan) va Telegram orqali xatolar "
                "monitoringi bor."
            ),
            "ru": (
                "Платформа работает на oqqushlar.uz. 258 автотестов, ночные зашифрованные бэкапы (14 ежедневных "
                "и 8 еженедельных копий с проверкой восстановления) и мониторинг ошибок через Telegram."
            ),
            "en": (
                "The platform is live at oqqushlar.uz, with 258 automated tests, nightly encrypted backups "
                "(14 daily and 8 weekly copies, with restore checks) and error monitoring via Telegram."
            ),
        },
        "highlights": {
            "uz": (
                "8 til: o'zbek, rus, ingliz, qozoq, qirg'iz, tojik, turkman, qoraqalpoq\n"
                "9 marosim turi va 7 millat bo'yicha filtr\n"
                "RSVP va mehmonlar statistikasi\n"
                "Rasmlar: WebP + EXIF/GPS tozalash, taxminan 8 baravar kichik\n"
                "Shifrlangan tungi zaxira: pg_dump | gpg, alohida bucket, tiklash tekshiruvi"
            ),
            "ru": (
                "8 языков: узбекский, русский, английский, казахский, киргизский, таджикский, туркменский, каракалпакский\n"
                "9 типов торжеств и фильтр по 7 национальностям\n"
                "RSVP и статистика гостей\n"
                "Фото: WebP + очистка EXIF/GPS, примерно в 8 раз меньше\n"
                "Зашифрованные ночные бэкапы: pg_dump | gpg, отдельный bucket, проверка восстановления"
            ),
            "en": (
                "8 languages: Uzbek, Russian, English, Kazakh, Kyrgyz, Tajik, Turkmen, Karakalpak\n"
                "9 ceremony types and a filter by 7 nationalities\n"
                "RSVP and guest statistics\n"
                "Photos: WebP + EXIF/GPS stripping, about 8× smaller\n"
                "Encrypted nightly backups: pg_dump | gpg, separate bucket, restore checks"
            ),
        },
    },
    "zebest": {
        "order": 3,
        "status": "launch",
        "link": "",
        "tags": "Django, django-tenants, PostgreSQL, PWA, nginx, gunicorn",
        "title": {"uz": "Zebest", "ru": "Zebest", "en": "Zebest"},
        "desc": {
            "uz": "Restoranlar uchun multi-tenant SaaS: QR-menyu va buyurtma, xodimlar panellari, kuryer va PWA.",
            "ru": "Мультитенантная SaaS для ресторанов: QR-меню и заказы, панели персонала, курьеры и PWA.",
            "en": "A multi-tenant SaaS for restaurants: QR menus and ordering, staff panels, couriers and a PWA.",
        },
        "facts": {
            "uz": "Schema-per-tenant\n5 xodim paneli\nPWA",
            "ru": "Schema-per-tenant\n5 панелей персонала\nPWA",
            "en": "Schema-per-tenant\n5 staff panels\nPWA",
        },
        "problem": {
            "uz": (
                "Har bir restoran o'z subdomeni, menyusi va dizayni bilan ishlaydigan, lekin bitta platformadan "
                "boshqariladigan tizim kerak edi. Mehmon stol ustidagi QR orqali buyurtma beradi, ofitsiant, "
                "oshxona, kassir va kuryer esa har biri o'z panelida ishlaydi."
            ),
            "ru": (
                "Нужна была система, где у каждого ресторана свой поддомен, меню и дизайн, но всё управляется с "
                "одной платформы. Гость заказывает по QR-коду на столе, а официант, кухня, кассир и курьер "
                "работают каждый в своей панели."
            ),
            "en": (
                "Each restaurant needed its own subdomain, menu and design, all run from one platform. Guests "
                "order through a QR code on the table, while waiters, kitchen, cashier and couriers each work "
                "in their own panel."
            ),
        },
        "solution": {
            "uz": (
                "django-tenants bilan har bir restoran uchun alohida PostgreSQL sxemasi — mijozlar ma'lumoti "
                "bir-biridan to'liq ajratilgan. Har stolga QR-kod: filial avtomatik aniqlanadi, kodlar PDF'ga "
                "ommaviy eksport qilinadi.\n\n"
                "Menejer, ofitsiant, oshxona, kuryer va kassir panellari bir xil 4 tabli pastki navigatsiyaga "
                "ega PWA. Xodimlar davomati selfi bilan, kamera faqat filial radiusida ochiladi; mijoz va "
                "kuryer o'rtasida chat bor. Avtomatik yangilanadigan sahifalar sinxron worker'larni band qilib "
                "qo'yayotgani aniqlangach, gunicorn gthread rejimiga o'tkazildi."
            ),
            "ru": (
                "django-tenants: у каждого ресторана своя схема PostgreSQL, данные клиентов полностью "
                "изолированы. QR-код на каждый стол: филиал определяется автоматически, коды массово "
                "экспортируются в PDF.\n\n"
                "Панели менеджера, официанта, кухни, курьера и кассира — PWA с одинаковой нижней навигацией из "
                "4 вкладок. Табель с селфи, причём камера открывается только в радиусе филиала; есть чат клиента "
                "с курьером. Когда выяснилось, что автообновляемые страницы занимают синхронные воркеры, "
                "gunicorn перевели на gthread."
            ),
            "en": (
                "django-tenants gives every restaurant its own PostgreSQL schema, so client data is fully "
                "isolated. Each table gets a QR code; the branch is detected automatically and codes export to "
                "PDF in bulk.\n\n"
                "The manager, waiter, kitchen, courier and cashier panels are PWAs sharing the same 4-tab bottom "
                "navigation. Staff clock in with a selfie, and the camera only opens inside the branch radius. "
                "Customers can chat with their courier. When auto-refreshing pages turned out to be tying up "
                "sync workers, gunicorn was switched to gthread."
            ),
        },
        "result": {
            "uz": "Platforma ishga tushirish bosqichida: asosiy domen va har bir restoran uchun wildcard subdomenlar ulanmoqda.",
            "ru": "Платформа на этапе запуска: подключаются основной домен и wildcard-поддомены для каждого ресторана.",
            "en": "The platform is in its launch phase: the main domain and wildcard subdomains for each restaurant are being connected.",
        },
        "highlights": {
            "uz": (
                "Har bir restoran — alohida PostgreSQL sxemasi va subdomen\n"
                "Stol QR-kodlari: filialni avtomatik aniqlash, PDF'ga ommaviy eksport\n"
                "5 ta xodim paneli PWA sifatida, bir xil 4 tabli navigatsiya\n"
                "Selfi bilan davomat — kamera faqat filial radiusida\n"
                "Mijoz va kuryer chati"
            ),
            "ru": (
                "Каждый ресторан — отдельная схема PostgreSQL и поддомен\n"
                "QR-коды столов: автоопределение филиала, массовый экспорт в PDF\n"
                "5 панелей персонала в виде PWA с единой навигацией из 4 вкладок\n"
                "Табель с селфи — камера только в радиусе филиала\n"
                "Чат клиента с курьером"
            ),
            "en": (
                "Each restaurant: its own PostgreSQL schema and subdomain\n"
                "Table QR codes: automatic branch detection, bulk PDF export\n"
                "5 staff panels as PWAs with the same 4-tab navigation\n"
                "Selfie attendance, with the camera locked to the branch radius\n"
                "Customer–courier chat"
            ),
        },
    },
}

OTHER = {
    "roma-food": {
        "order": 10,
        "title": {"uz": "Roma Food", "ru": "Roma Food", "en": "Roma Food"},
        "desc": {
            "uz": "Toshkentdagi fastfood restorani uchun QR-menyu: o'zbek va rus tillarida, savatcha bilan.",
            "ru": "QR-меню для фастфуд-ресторана в Ташкенте: на узбекском и русском, с корзиной.",
            "en": "A QR menu for a fast-food restaurant in Tashkent, in Uzbek and Russian, with a cart.",
        },
    },
    "geodezistman": {
        "order": 11,
        "title": {"uz": "Geodezistman.uz", "ru": "Geodezistman.uz", "en": "Geodezistman.uz"},
        "desc": {
            "uz": "Geodezistlar uchun onlayn kurslar platformasi.",
            "ru": "Платформа онлайн-курсов для геодезистов.",
            "en": "An online-course platform for land surveyors.",
        },
    },
    "lingvoapp": {
        "order": 12,
        "title": {"uz": "LingvoApp", "ru": "LingvoApp", "en": "LingvoApp"},
        "desc": {
            "uz": "Telegram Mini App'da ingliz tili: SM-2 takrorlash algoritmi bilan so'z yodlash.",
            "ru": "Английский в Telegram Mini App: запоминание слов по алгоритму SM-2.",
            "en": "English learning as a Telegram Mini App, with SM-2 spaced repetition.",
        },
    },
    "english-bot": {
        "order": 13,
        "title": {"uz": "English Bot", "ru": "English Bot", "en": "English Bot"},
        "desc": {
            "uz": "Ingliz tili o'rganish uchun Telegram bot asosi.",
            "ru": "Каркас Telegram-бота для изучения английского.",
            "en": "A Telegram bot scaffold for learning English.",
        },
    },
    "n8n-workflows": {
        "order": 14,
        "title": {"uz": "n8n workflow'lari", "ru": "Сценарии n8n", "en": "n8n workflows"},
        "desc": {
            "uz": "Telegram yangiliklar agregatori (Jaccard bilan takrorlarni aniqlash) va AI yordamida watermark topish.",
            "ru": "Агрегатор новостей для Telegram (дубли по Жаккару) и поиск водяных знаков с помощью AI.",
            "en": "A Telegram news aggregator (Jaccard de-duplication) and AI-assisted watermark detection.",
        },
    },
}

LANGS = ("uz", "ru", "en")


def forwards(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    SiteProfile = apps.get_model("portfolio", "SiteProfile")

    if not SiteProfile.objects.exists():
        SiteProfile.objects.create(
            full_name="Shohzod", about_uz=ABOUT["uz"], about_ru=ABOUT["ru"], about_en=ABOUT["en"]
        )

    # The restaurant SaaS is called Zebest now.
    if not Project.objects.filter(slug="zebest").exists():
        Project.objects.filter(slug="eltaom").update(slug="zebest")
    else:
        Project.objects.filter(slug="eltaom").update(is_active=False)  # never show both

    for slug, data in FEATURED.items():
        project, _ = Project.objects.get_or_create(
            slug=slug,
            defaults={f"{k}_{lang}": data[k][lang] for k in ("title", "desc") for lang in LANGS},
        )
        project.tier = "featured"
        project.is_active = True
        for key in ("order", "status", "link", "tags"):
            setattr(project, key, data[key])
        for key in ("title", "desc", "facts", "problem", "solution", "result", "highlights"):
            for lang in LANGS:
                setattr(project, f"{key}_{lang}", data[key][lang])
        project.save()

    for slug, data in OTHER.items():
        project = Project.objects.filter(slug=slug).first()
        if project is None:
            continue
        project.tier = "other"
        project.order = data["order"]
        for key in ("title", "desc"):
            for lang in LANGS:
                setattr(project, f"{key}_{lang}", data[key][lang])
        project.save()

    Project.objects.filter(slug="geo-portfolio").update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0006_case_pages_profile_security"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
