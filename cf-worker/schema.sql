-- D1 `onboarding-eingang` — Rohsätze des Onboarding-Formulars (seit 10.11.2026, ClickUp raus)
-- Einspielen:  npx wrangler d1 execute onboarding-eingang --remote --file schema.sql
-- Der Worker legt die Tabelle beim ersten Eingang auch selbst an (src/eingang.js › EINGANG_SCHEMA, gleiche Spalten).
-- Gelesen (nur SELECT) von CEO-GPT/system/scripts/onboarding_eingang.py; verarbeitete IDs merkt sich der Abholer selbst.
CREATE TABLE IF NOT EXISTS onboarding_eingang (
  id TEXT PRIMARY KEY,
  eingegangen_am TEXT NOT NULL,
  firma TEXT NOT NULL,
  service_type TEXT NOT NULL,
  drive_link TEXT,
  root_folder_id TEXT,
  leistungen TEXT,
  form_data TEXT NOT NULL,
  missing TEXT,
  abgeleitet TEXT NOT NULL,
  client_v INTEGER
);
CREATE INDEX IF NOT EXISTS onboarding_eingang_zeit ON onboarding_eingang (eingegangen_am);
