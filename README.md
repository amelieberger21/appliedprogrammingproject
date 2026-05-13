# Note Taking API

Eine einfache und benutzerfreundliche REST API zum Verwalten von Notizen mit Tags und Kategorien.

## Features

- ✅ **CRUD-Operationen** — Notizen erstellen, lesen, aktualisieren, löschen
- ✅ **Tags & Kategorien** — Organisiere Notizen mit flexiblen Tags und vordefinierten Kategorien
- ✅ **Filterung & Suche** — Suche nach Titel/Inhalt, Filter nach Kategorie oder Tag
- ✅ **Datum-Filter** — Notizen nach Erstellungsdatum filtern
- ✅ **Statistiken** — Übersicht mit Notizen-Anzahl, Top-Tags und Kategorien
- ✅ **SQLite-Datenbank** — Persistente Speicherung
- ✅ **Interaktive API-Dokumentation** — Swagger UI & ReDoc

## Installation

### Voraussetzungen
- Python 3.13+
- `uv` (UV package manager)

### Setup

```bash
cd appliedprogrammingproject
uv sync
```

## Server starten

```bash
cd appliedprogrammingproject
./.venv/bin/python3 -m uvicorn main:app --reload
```

Server läuft auf: **http://127.0.0.1:8000**

## API-Dokumentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Endpunkte

### Notizen

| Methode | Endpoint | Beschreibung |
|---------|----------|-------------|
| `GET` | `/` | Welcome Message |
| `POST` | `/notes` | Neue Note erstellen |
| `GET` | `/notes` | Alle Notizen auflisten (mit Filtern) |
| `GET` | `/notes/{note_id}` | Einzelne Note abrufen |
| `PUT` | `/notes/{note_id}` | Note vollständig ersetzen |
| `PATCH` | `/notes/{note_id}` | Note teilweise ändern |
| `DELETE` | `/notes/{note_id}` | Note löschen |

### Tags

| Methode | Endpoint | Beschreibung |
|---------|----------|-------------|
| `GET` | `/tags` | Alle Tags auflisten |
| `GET` | `/tags/{tag_name}/notes` | Alle Notizen mit Tag |

### Kategorien

| Methode | Endpoint | Beschreibung |
|---------|----------|-------------|
| `GET` | `/categories` | Alle Kategorien auflisten |
| `GET` | `/categories/{category_name}/notes` | Alle Notizen einer Kategorie |

### Statistiken

| Methode | Endpoint | Beschreibung |
|---------|----------|-------------|
| `GET` | `/notes/stats` | Statistiken (Total, nach Kategorie, Top-Tags) |

## Beispiel-Request

```bash
curl -X POST "http://127.0.0.1:8000/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Meine erste Note",
    "content": "Das ist der Inhalt",
    "category": "work",
    "tags": ["wichtig", "code"]
  }'
```

## Filter-Beispiele

```
# Nach Kategorie filtern
GET /notes?category=work

# Nach Tag filtern
GET /notes?tag=code

# Volltextsuche
GET /notes?search=python

# Nach Datum filtern
GET /notes?created_after=2026-01-01T00:00:00
```

## Kategorien

Erlaubte Kategorien:
- `work`
- `personal`
- `school`
- `ideas`
- `general`

## Technologie-Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Datenbank**: SQLite
- **Validierung**: Pydantic
- **Server**: Uvicorn

## Struktur

```
appliedprogrammingproject/
├── main.py          # Hauptanwendung
├── notes.db         # SQLite-Datenbank
├── pyproject.toml   # Projektabhängigkeiten
└── README.md        # Diese Datei
```

## Abhängigkeiten

```
fastapi>=0.136.1
sqlmodel>=0.0.38
uvicorn>=0.46.0
pydantic>=2.0.0
```

## Lizenz

MIT