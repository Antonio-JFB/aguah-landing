# Despliegue: aguah-landing (droplet 64.23.253.163)

Landing de login independiente para los dashboards de Agua de Hermosillo. Vive aparte de
`m2-landing` (la del municipio): su propio `.venv`, su propio `.env`, su propio `JWT_SECRET`,
su propio `systemd` unit y su propio dominio. No toca los servicios existentes (8001-8007, 3838).

Puerto asignado: **8008** (confirmar con `ss -tulpn` antes de asumirlo libre, por si cambió
desde que se escribió esto). Dominio: `appaguah2026.argentumdevelopment.com` (el registro DNS
ya existe y apunta a este droplet).

## 1. Generar el secreto propio

```bash
openssl rand -hex 32
```

Este secreto es **exclusivo de aguah-landing y del dashboard A2 AguaH** (y de cualquier otro
dashboard de AguaH que se conecte a esta landing más adelante). **No reutilizar** el
`JWT_SECRET` de `m2-landing`/`m2-predial` — son sistemas de login independientes a propósito.

## 2. Clonar el repo

```bash
git clone <url-del-repo-aguah-landing> /var/www/aguah_landing
```

## 3. Entorno + usuarios

```bash
cd /var/www/aguah_landing
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env
# editar .env: JWT_SECRET=<el generado en el paso 1>, APP_PORT=8008
./.venv/bin/python -m backend.seed --username operador.aguah --cliente aguah
```

## 4. Probar directo en el puerto, sin nginx

```bash
./.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8008 &
sleep 2
curl -s -i 127.0.0.1:8008/login   # debe responder 200 con el HTML de login
kill %1
```

## 5. systemd unit

`/etc/systemd/system/aguah_landing.service`:

```ini
[Unit]
Description=AguaH Landing - Argentum (FastAPI/uvicorn)
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/aguah_landing
EnvironmentFile=/var/www/aguah_landing/.env
ExecStart=/var/www/aguah_landing/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8008 --workers 1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now aguah_landing.service
sleep 3
systemctl status aguah_landing.service --no-pager
curl -s 127.0.0.1:8008/api/health
```

## 6. nginx

`/etc/nginx/sites-available/appaguah2026.argentumdevelopment.com`:

```nginx
server {
    listen 80;
    server_name appaguah2026.argentumdevelopment.com;

    location / {
        proxy_pass http://127.0.0.1:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/appaguah2026.argentumdevelopment.com /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx   # reload, NUNCA restart -> no corta las demas apps
```

## 7. DNS + TLS

```bash
dig +short appaguah2026.argentumdevelopment.com   # ya debe dar 64.23.253.163
certbot --nginx -d appaguah2026.argentumdevelopment.com
nginx -t && systemctl reload nginx
```

## 8. Verificación end-to-end

1. `https://appaguah2026.argentumdevelopment.com/login` → formulario de login (marca AguaH).
2. Login con el usuario sembrado en el paso 3 → redirige a `/dashboards` con la tarjeta de
   A2 AguaH.
3. Click en la tarjeta → entra directo a `https://appaguah2026.redes.argentumdevelopment.com/`
   sin pedir login otra vez.
4. Devtools → Application → Cookies: debe existir `aguah_session` con
   `Domain=.argentumdevelopment.com`, `Secure`, `HttpOnly` — y **no** debe tocar ni reemplazar
   la cookie `m2_session` de la landing del municipio si visitas ambas en el mismo navegador.
5. "Cerrar sesión" → vuelve a `/login`; entrar directo a `/dashboards` sin sesión → redirige a
   `/login?next=/dashboards`.
6. Confirmar que las demás apps del servidor (8001-8007, 3838, incluyendo `m2_landing` en 8006)
   siguen respondiendo después del `nginx reload`.

## 9. Rollback

```bash
systemctl stop aguah_landing.service
rm /etc/nginx/sites-enabled/appaguah2026.argentumdevelopment.com
nginx -t && systemctl reload nginx
```
