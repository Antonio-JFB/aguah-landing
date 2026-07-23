# AguaH Landing - Argentum

Landing page de login para los dashboards de Agua de Hermosillo. Autentica al usuario y lo
redirige al dashboard correspondiente emitiendo una cookie de sesion (JWT firmado) compartida
entre subdominios de `argentumdevelopment.com`. Cada dashboard valida esa cookie localmente con
el mismo `JWT_SECRET`, sin llamar de vuelta a esta landing en cada request.

Es independiente de `m2-landing` (la landing del municipio de Hermosillo): usuarios, base de
datos, `JWT_SECRET` y nombre de cookie (`aguah_session` vs `m2_session`) propios, para que ambos
sistemas de login no se pisen entre si en el navegador.

## Instalacion y ejecucion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
# editar .env y definir JWT_SECRET (unico para este proyecto, no reusar el de m2-landing)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8008 --env-file .env
```

## Alta de usuarios

No hay UI de administracion; los usuarios se dan de alta por linea de comandos:

```powershell
python -m backend.seed --username operador.aguah --cliente aguah
```

Pide la contrasena de forma interactiva (o usa `--password` para no interactivo, ej. en scripts
de aprovisionamiento).

## Dashboards visibles por cliente

El mapeo `cliente -> dashboards` vive en `backend/registry.py`. Agregar un dashboard nuevo es
agregar una entrada a ese diccionario.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Despliegue

Ver `DEPLOY.md` para los pasos de systemd, nginx y certbot en el servidor compartido.
