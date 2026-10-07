# Shohzod — Portfolio (o'zbekcha qo'llanma)

[English README](README.md)

Django asosidagi shaxsiy portfolio. 3 tilda (har biri alohida URL'da:
`/uz/`, `/ru/`, `/en/`), "Blueprint" uslubida. Bosh sahifa qisqa — 4 bo'lim:
hero (interaktiv arxitektura diagrammasi bilan), tanlangan ishlar, men
haqimda, aloqa. Har bir asosiy loyihaning alohida case-study sahifasi bor
(`/uz/work/buildops/`) — mijozga shu havolani yuborasiz. JavaScript
o'chirilgan holatda ham to'liq ishlaydi.

## Tuzilishi

```
config/                    — settings, urls
portfolio/
  models.py                — SiteProfile, SocialLink, Project, ContactMessage, LoginFailure
  admin.py                 — admin panel
  content.py               — interfeys matnlari va ko'nikmalar (UZ/RU/EN)
  views.py                 — bosh sahifa, case sahifa, til yo'naltirish, aloqa formasi, robots/sitemap
  security.py              — CSP sarlavhalari, admin login cheklovi, IP hash
  forms.py                 — aloqa formasi (+ spam-tuzoq)
  notifications.py         — yangi xabarni Telegramga yuborish
  tests.py                 — avtomatik testlar
templates/portfolio/       — base.html, index.html, case.html + qismlar (_diagram, _socials)
static/portfolio/          — css, js, rasmlar, o'z serverimizdagi shriftlar
```

## Nimani qayerdan o'zgartirasiz

- **Ism va "Men haqimda" matni** — admin panel → *Sayt profili*. 3 tilda,
  bo'sh qator — yangi xatboshi. Ism sarlavhada, Google ma'lumotlarida va
  sahifa nomida ishlatiladi.
- **Loyihalar** — admin panel → *Loyihalar*:
  - *Tanlangan — karta*: bosh sahifadagi 3 ta asosiy karta (3 tadan
    oshirmang). Kartada qisqa tavsif (bitta jumla) va 3 tagacha "raqam"
    (`258 test`, `8 til`) ko'rinadi.
  - *Boshqa ishlar*: pastdagi bir qatorli ro'yxat.
  - *Case sahifasi* bloklari (vazifa, yechim, natija, asosiy yechimlar)
    to'ldirilsa, loyiha uchun alohida sahifa ochiladi va kartada
    «Batafsil» havolasi chiqadi. Muqova rasmi yuklansa, avtomatik 1600px
    WebP'ga siqiladi va case sahifasida ko'rinadi.
- **Ijtimoiy tarmoqlar** — admin panel → *Ijtimoiy tarmoqlar*. Faqat URL
  kiritilganlari saytda ko'rinadi. **Telegram** URL'i kiritilsa, u
  saytdagi asosiy "Telegram orqali yozish" tugmasiga aylanadi.
- **Xabarlar** — admin panel → *Xabarlar (aloqa formasi)*.
- **Interfeys matnlari** — `portfolio/content.py` (`STRINGS`). Uchala
  tilda kalitlar bir xil bo'lishi shart — testlar buni tekshiradi.

## Mahalliy ishga tushirish (PowerShell)

Birinchi marta yoki yangilanishdan keyin:

```
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Admin uchun foydalanuvchi (bir marta):

```
python manage.py createsuperuser
```

Sayt: http://127.0.0.1:8000/ (avtomatik `/uz/` ga o'tadi) · Admin: http://127.0.0.1:8000/admin/
(yoki `.env` dagi `DJANGO_ADMIN_URL` manzili)

Testlar:

```
python manage.py test
```

## Aloqa formasi → Telegram (ixtiyoriy)

Sozlanmasa ham forma ishlaydi: xabarlar admin panelda saqlanadi.
Telegramga ham kelishi uchun:

1. @BotFather'da bot yarating va tokenni oling.
2. Botga bitta xabar yozing, so'ng o'zingizning chat ID'ingizni
   @userinfobot orqali bilib oling.
3. `.env` ga qo'shing:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   TELEGRAM_CHAT_ID=123456789
   ```

Spamdan himoya:

- ko'rinmas "tuzoq" maydon (`leave_empty` — botlar to'ldiradi, odamlar
  ko'rmaydi; brauzer avtomatik to'ldiradigan nom emas);
- bir IP'dan soatiga 5 tagacha xabar (`CONTACT_RATE_LIMIT_PER_HOUR`) va
  butun sayt bo'yicha soatiga 30 tagacha (`CONTACT_GLOBAL_LIMIT_PER_HOUR`).
  Hisob bazada yuritiladi — bir nechta gunicorn worker'da ham, qayta
  ishga tushirishdan keyin ham ishlaydi. IP o'zi saqlanmaydi, faqat
  SECRET_KEY bilan olingan hash'i.
- `CONTACT_TRUST_PROXY_HEADERS=True` faqat sayt nginx yoki PythonAnywhere
  orqasida turganda yoqiladi (ular `X-Real-IP` ni o'zi qo'yadi). Proksisiz
  yoqilsa, har kim sarlavhani soxtalashtirib limitni aylanib o'tadi.

## Xavfsizlik

- **Admin manzili**: `.env` da `DJANGO_ADMIN_URL=boshqaruv-7f3k/` kabi
  standart bo'lmagan manzil bering — botlar `/admin/` ni urib yotadi.
- **Admin login cheklovi**: bir IP'dan 15 daqiqada 5 ta xato urinishdan
  keyin login vaqtincha bloklanadi (`ADMIN_LOGIN_MAX_FAILURES`,
  `ADMIN_LOGIN_WINDOW_MINUTES`).
- **Content-Security-Policy**: sayt faqat o'z serveridagi skript, stil,
  shrift va rasmlarni yuklaydi; yagona inline skript hash orqali
  ruxsat etilgan. Admin panelga CSP qo'yilmaydi.
- **Loglar**: xatolar stderr'ga yoziladi — serverda `journalctl -u gunicorn`,
  PythonAnywhere'da *Error log*.
- **Email**: `SITE_CONTACT_EMAIL` o'rnatilmasa, saytda email bloki
  ko'rinmaydi va `manage.py check` ogohlantiradi.

## Production — ishga tushirishdan oldin

`DJANGO_DEBUG=False` bilan ishga tushirishdan oldin:

1. Yangi SECRET_KEY yarating (standart kalit bilan sayt ataylab ishga tushmaydi):
   ```
   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
   ```
2. `DJANGO_ALLOWED_HOSTS` va `DJANGO_CSRF_TRUSTED_ORIGINS=https://domeningiz.uz`.
3. `python manage.py collectstatic --noinput` — albatta (WhiteNoise manifest).
4. `/media/` (yuklangan muqova rasmlari) server tomonidan xizmat qilinishi
   kerak — pastga qarang.

## PythonAnywhere

1. Kodni clone qiling, virtualenv yarating, `pip install -r requirements.txt`.
2. Web tab → Manual configuration → WSGI faylda `config.wsgi.application`.
3. Static files: `/static/` → `.../staticfiles`, `/media/` → `.../media`.
4. Environment: `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY=...`,
   `DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com`,
   `CONTACT_TRUST_PROXY_HEADERS=True`.
5. `python manage.py migrate` va `python manage.py collectstatic --noinput`.
6. Web tab → **Reload**.

## Hetzner VPS (nginx + gunicorn)

Server buyruqlari:

```
cd /home/deploy/shohzodev_portfolio
git pull
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

nginx: `location /static/` → `staticfiles/`, `location /media/` → `media/`.
Aloqa formasidagi IP-limit to'g'ri ishlashi uchun nginx haqiqiy IP'ni
uzatishi kerak:

```
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

va `.env` da `CONTACT_TRUST_PROXY_HEADERS=True`.

## SEO

Har bir til alohida URL'da, `hreflang` + `x-default`, kanonik havola,
schema.org `Person` va case sahifalarda `CreativeWork` (JSON-LD),
`/robots.txt`, `/sitemap.xml` (bosh sahifa + barcha case sahifalar, 3 tilda,
alternativlari bilan). Ijtimoiy tarmoqda ulashish rasmi:
`static/portfolio/img/og-image.jpg` (1200×630).

## Shriftlar

IBM Plex Sans (sarlavha va matn), IBM Plex Mono (metama'lumot) — o'z
serverimizda
(`static/portfolio/fonts/`, SIL Open Font License, litsenziyalar shu
papkada). Faqat lotin va kirill qismlari; brauzer faqat sahifaga kerakli
qismni yuklaydi.
