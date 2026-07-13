# Docker

## Local dev

```bash
# 1) Levantar Postgres + Redis + Console API
docker compose up -d postgres redis console

# 2) Levantar frontend en modo dev (hot reload) desde host
cd web && npm install && npm run dev
# → http://localhost:5173  (Vite dev server)
# → http://localhost:7000  (Console API)
```

## Local prod-like

```bash
docker compose --profile production up
# → http://localhost:7000  (Nginx sirviendo build + proxy a /api)
```

## Reset total

```bash
docker compose down -v
rm -rf .console_keys/
```

## Notas

- Postgres expuesto en `5433:5432` para no chocar con Postgres del host.
- Redis expuesto en `6380:6379` por la misma razón.
- El volumen `console_keys` guarda la clave Ed25519 de Console. No lo borres a menos que quieras reemitir la clave.
