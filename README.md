# Shohzod — Portfolio

Django asosidagi shaxsiy portfolio. 3 tilda (har biri alohida URL'da:
`/uz/`, `/ru/`, `/en/`), "Blueprint" tuzilishi va muhandislik ko'k
palitrasida: hero'da interaktiv arxitektura diagrammasi, "Qanday quraman"
tamoyillari, ixcham "Stek" qatorlari. JavaScript o'chirilgan
holatda ham to'liq ishlaydi. Lighthouse (production rejimida): mobil
99/100/100/100, desktop 100/100/100/100.

## Tuzilishi

```
config/                    — settings, urls
portfolio/
  models.py                — SocialLink, Project, ContactMessage
  admin.py                 — admin panel (loyihalar, xabarlar, ijtimoiy tarmoqlar)
  content.py               — interfeys matnlari va ko'nikmalar (UZ/RU/EN)
  views.py                 — sahifa, til yo'naltirish, aloqa formasi, robots/sitemap
  forms.py                 — aloqa formasi (+ spam-tuzoq)
  notifications.py         — yangi xabarni Telegramga yuborish
  tests.py                 — 47 ta avtomatik test
templates/portfolio/       — index.html + qismlar (_diagram, _socials, _project_links)
static/portfolio/          — css (style + o'z serverimizdagi shriftlar), js, rasmlar, fonts/
```

## Nimani qayerdan o'zgartirasiz

- **Loyihalar** — admin panel → *Loyihalar*. Har biri 3 tilda (nom, tavsif,
  "asosiy jihatlar"), holat, havolalar, texnologiyalar, muqova rasmi.
  **Ko'rinish** maydoni joylashuvni boshqaradi:
  - *Asosiy — katta karta*: to'liq kenglikdagi flagship karta (hozir BuildOps).
    Muqova rasmi yuklansa, o'ng tomonda rasm chiqadi; bo'lmasa — "Asosiy
    jihatlar" ro'yxati.
  - *Oddiy karta*: 2 ustunli setka.
  - *Boshqa ishlar*: pastdagi ixcham ro'yxat (kichik/yordamchi ishlar uchun).
- **Xabarlar** — admin panel → *Xabarlar (aloqa formasi)*.
- **Ijtimoiy tarmoqlar** — admin panel → *Ijtimoiy tarmoqlar*. URL
  kiritilmagan ikonka xira ko'rinadi va bosilmaydi.
- **Interfeys matnlari va "Men haqimda"** — `portfolio/content.py`
  (`STRINGS`). Uchala tilda kalitlar bir xil bo'lishi shart — testlar buni
  tekshiradi.

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

## Production — xavfsizlik

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
schema.org `Person` (JSON-LD), `/robots.txt`, `/sitemap.xml` (3 til,
alternativlari bilan). Ijtimoiy tarmoqda ulashish rasmi:
`static/portfolio/img/og-image.jpg` (1200×630).

## Shriftlar

IBM Plex Sans (sarlavha va matn), IBM Plex Mono (metama'lumot) — o'z
serverimizda
(`static/portfolio/fonts/`, SIL Open Font License, litsenziyalar shu
papkada). Faqat lotin va kirill qismlari; brauzer faqat sahifaga kerakli
qismni yuklaydi.
