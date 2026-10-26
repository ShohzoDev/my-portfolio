# Shohzod — Portfolio (o'zbekcha qo'llanma)

[English README](README.md)

Django asosidagi shaxsiy portfolio. 3 tilda (har biri alohida URL'da:
`/uz/`, `/ru/`, `/en/`). Bitta qisqa sahifa, 3 qism: kimman (rasm, sarlavha,
stek, Telegram va ijtimoiy tarmoqlar), loyihalar, aloqa. Har bir loyihaning
o'z sayti bor, shuning uchun portfolio ularni havolalar ro'yxati sifatida
ko'rsatadi: nomi, bir qatorli tavsif va domeni. Sahifa toza HTML va CSS —
JavaScript yo'q.

## Tuzilishi

```
config/                    — settings, urls
portfolio/
  models.py                — SiteProfile, SocialLink, Project, LoginFailure
  admin.py                 — admin panel
  content.py               — interfeys matnlari (UZ/RU/EN) va stek qatori
  views.py                 — bosh sahifa, til yo'naltirish, robots/sitemap
  security.py              — CSP sarlavhalari, admin login cheklovi, IP hash
  tests.py                 — avtomatik testlar
templates/portfolio/       — base.html, index.html, _socials.html
static/portfolio/          — css, rasmlar, o'z serverimizdagi shriftlar
```

## Nimani qayerdan o'zgartirasiz

- **Ism** — admin panel → *Sayt profili*. Ism sahifada, sarlavhada va
  Google ma'lumotlarida ishlatiladi.
- **Loyihalar** — admin panel → *Loyihalar*. Har biri uchun: nomi, bir
  qatorli tavsif (3 tilda), sayt havolasi, holat va tartib. Butun qator
  saytga olib boradi, havola esa domen ko'rinishida chiqadi
  (`https://www.zebest.uz/` → `zebest.uz`). «Ishlamoqda»dan boshqa holat
  nom yonida yoziladi; «Men asoschiman» belgilansa — «Asoschi» belgisi.
- **Ijtimoiy tarmoqlar** — admin panel → *Ijtimoiy tarmoqlar*. Faqat URL
  kiritilganlari saytda ko'rinadi. **Telegram** URL'i kiritilsa, u
  saytdagi asosiy "Telegram'da yozing" tugmasiga aylanadi.
- **Matnlar va stek qatori** — `portfolio/content.py` (`STRINGS`, `STACK`). Uchala
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

## Xavfsizlik

- **Admin manzili**: `.env` da `DJANGO_ADMIN_URL=boshqaruv-7f3k/` kabi
  standart bo'lmagan manzil bering — botlar `/admin/` ni urib yotadi.
- **Admin login cheklovi**: bir IP'dan 15 daqiqada 5 ta xato urinishdan
  keyin login vaqtincha bloklanadi (`ADMIN_LOGIN_MAX_FAILURES`,
  `ADMIN_LOGIN_WINDOW_MINUTES`).
- **Content-Security-Policy**: sayt faqat o'z serveridagi stil, shrift va
  rasmlarni yuklaydi; JavaScript umuman yo'q (`script-src 'none'`). Admin
  panelga CSP qo'yilmaydi.
- **Proksi**: `CONTACT_TRUST_PROXY_HEADERS=True` faqat sayt nginx yoki
  PythonAnywhere orqasida turganda yoqiladi — shunda admin login cheklovi
  haqiqiy IP'ni ko'radi. Proksisiz yoqilsa, IP'ni soxtalashtirish mumkin.
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

## PythonAnywhere

1. Kodni clone qiling, virtualenv yarating, `pip install -r requirements.txt`.
2. Web tab → Manual configuration → WSGI faylda `config.wsgi.application`.
3. Static files: `/static/` → `.../staticfiles`.
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

nginx: `location /static/` → `staticfiles/`. Admin login cheklovi to'g'ri
ishlashi uchun nginx haqiqiy IP'ni uzatishi kerak:

```
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

va `.env` da `CONTACT_TRUST_PROXY_HEADERS=True`.

## SEO

Har bir til alohida URL'da, `hreflang` + `x-default`, kanonik havola,
schema.org `Person` (JSON-LD), `/robots.txt`, `/sitemap.xml` (bosh sahifa
3 tilda, alternativlari bilan). Ijtimoiy tarmoqda ulashish rasmi:
`static/portfolio/img/og-image.jpg` (1200×630).

## Shriftlar

IBM Plex Sans (sarlavha va matn), IBM Plex Mono (metama'lumot) — o'z
serverimizda
(`static/portfolio/fonts/`, SIL Open Font License, litsenziyalar shu
papkada). Faqat lotin va kirill qismlari; brauzer faqat sahifaga kerakli
qismni yuklaydi.
