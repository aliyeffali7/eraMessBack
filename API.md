# Messenger API — frontend inteqrasiyası üçün

Base URL: `http://169.58.161.115/api` (prod, hələ HTTP — tezliklə HTTPS olacaq)
Auth: JWT (SimpleJWT). Hər sorğuya `Authorization: Bearer <access>` başlığı.

## Auth

| Metod | Endpoint | Body | Cavab |
|---|---|---|---|
| POST | `/accounts/login/` | `{username, password}` | `{access, refresh}` |
| POST | `/accounts/login/refresh/` | `{refresh}` | `{access}` |
| GET | `/accounts/me/` | — | user obyekti (`id, username, degree, section, public_key`) |
| PATCH | `/accounts/me/public-key/` | `{public_key}` | user |
| GET | `/accounts/users/?search=<q>` | — | user siyahısı (yeni çat üçün) |

## Çat

| Metod | Endpoint | Qeyd |
|---|---|---|
| GET | `/chat/conversations/` | istifadəçinin bütün söhbətləri, son aktivliyə görə sıralı, `unread_count` ilə |
| POST | `/chat/conversations/direct/` | `{user_id}` → 1:1 söhbət yarat/tap |
| POST | `/chat/conversations/group/` | `{name, member_ids}` (yalnız admin) |
| GET | `/chat/conversations/<id>/` | söhbət detalı + üzvlər |
| GET | `/chat/conversations/<id>/messages/?after=<msgId>` | mesajlar (artımlı çəkmə üçün `after`) |
| POST | `/chat/conversations/<id>/messages/` | mesaj göndər — aşağıya bax |
| POST | `/chat/conversations/<id>/read/` | oxundu işarələ |
| PATCH | `/chat/conversations/<id>/rename/` | `{name}` (qrup admini) |
| POST/DELETE | `/chat/conversations/<id>/members/...` | üzv idarəsi (qrup admini) |
| POST | `/chat/conversations/<id>/leave/` | qrupdan çıx |

### Mesaj formatı (VACİB — E2EE)

- **1:1 söhbət:** mesaj **client-də şifrələnir**. Body: `{ciphertext, nonce}` (hər ikisi base64).
  Server məzmunu **görmür**, yalnız saxlayıb ötürür.
- **Qrup söhbət (hələlik):** `{text}` düz mətn. (Qrup E2EE sonrakı mərhələdə.)

Şifrələmə: Curve25519 `nacl.box` (tweetnacl). Hər cihaz öz açar cütünü yaradır,
gizli açar cihazdan çıxmır, public açar `/accounts/me/public-key/` ilə serverə yüklənir.
Mesajı deşifrə etmək üçün göndərənin `public_key`-i lazımdır (`/accounts/me/` və ya
`/accounts/users/` cavabından).

> Qeyd: hazırda `public_key` user başına **tək sahədir** — çox cihaz dəstəyi
> (cihaz reyestri) planlaşdırılır, o zaman bu dəyişəcək.

### Qoşmalar (səs mesajı / fayl)

- Göndərmə: `POST /chat/conversations/<id>/messages/` **multipart/form-data**, əlavə sahə `attachment` (fayl, maks. 15 MB).
  - **1:1:** fayl cihazda `nacl.secretbox` (təsadüfi 32B açar + 24B nonce) ilə şifrələnir, şifrəli blob `attachment` kimi yüklənir.
    Mesajın şifrəli mətni (`ciphertext`) `"ATT:" + JSON` olur: `{kind:"voice"|"file", name, mime, size, dur?, key, nonce}` (key/nonce base64).
  - **Qrup:** fayl olduğu kimi yüklənir, `text` = `"ATT:" + JSON` (key/nonce yoxdur).
- Mesaj cavabında `has_attachment: true` olur (URL verilmir).
- Yükləmə: `GET /chat/conversations/<id>/messages/<msgId>/attachment/` (JWT, yalnız söhbət üzvləri) → xam bayt (1:1-də şifrəli blob).
- Qoşması olan mesaj redaktə oluna bilməz. Mesaj silinəndə fayl da silinir.
- Serverdə nginx: `client_max_body_size 20m;` olmalıdır.

## Digər

| Metod | Endpoint | Qeyd |
|---|---|---|
| POST | `/notifications/register-token/` | `{token}` push bildiriş üçün (məzmun payload-da deyil) |
| GET | `/library/`, `/meetings/`, `/org/...` | köməkçi modullar |

## Lokal işə salma (Next.js developer üçün)

Öz localhost origin-ini backend-ə əlavə etməlisən: prod-da
`CORS_ALLOWED_ORIGINS` env dəyişəni (məs. `http://localhost:3000`).
Aliyə de ki serverdə `.env`-ə əlavə etsin.

Backend-i lokal qaldırmaq: `DJANGO_SETTINGS_MODULE=config.settings.dev`,
`pip install -r requirements.txt`, `python manage.py migrate`, `runserver`.
`secrets/firebase-adminsdk.json` repoda yoxdur — push bildirişsiz lokal işləyir.
