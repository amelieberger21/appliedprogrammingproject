# Note Taking API
In dem projekt *Appliedprogramming* wurden eine performante und leichtgewichtige REST-API zur Verwaltung von Notizen. Das Projekt basiert auf **FastAPI** und nutzt **SQLModel** (SQLAlchemy + Pydantic) für eine robuste Datenvalidierung und nahtlose SQLite-Datenbankinteraktion.

---

## Features

*   **Vollständiges CRUD-System:** Notizen erstellen, lesen, aktualisieren (PUT & PATCH) und löschen.
*   **Many-to-Many Tag-System:** Notizen können mehrere Tags haben; Tags werden automatisch dedupliziert und klein geschrieben.
*   **Strikte Validierung:** Eingabeprüfung via Pydantic (Längenbeschränkungen, Erlaubte Kategorien, Whitespace-Stripping).
*   **Erweiterte Filterung:** Filtere Notizen nach Kategorien, Tags, Erstellungsdatum (`created_after`/`created_before`) oder Volltextsuche in Titel und Inhalt.
*   **Statistik-Endpoint:** Erhalte auf einen Blick Metriken über die Gesamtanzahl, Kategorienverteilung und die Top 5 der am häufigsten genutzten Tags.

---

## Technologie-Stack

*   **Framework:** FastAPI
*   **ORM / Datenbank-Wrapper:** SQLModel (kombiniert SQLAlchemy & Pydantic)
*   **Datenbank:** SQLite (automatische Datei-Generierung unter `notes.db`)
*   **Validierung:** Pydantic v2

---

## Anforderungen & Installation

### 1. Repository klonen & Verzeichnis betreten
```bash
git clone <repository-url>
cd <repository-folder>

# Note Taking API
In dem projekt *Appliedprogramming* wurden eine performante und leichtgewichtige REST-API zur Verwaltung von Notizen. Das Projekt basiert auf **FastAPI** und nutzt **SQLModel** (SQLAlchemy + Pydantic) für eine robuste Datenvalidierung und nahtlose SQLite-Datenbankinteraktion.

---

## Features

*   **Vollständiges CRUD-System:** Notizen erstellen, lesen, aktualisieren (PUT & PATCH) und löschen.
*   **Many-to-Many Tag-System:** Notizen können mehrere Tags haben; Tags werden automatisch dedupliziert und klein geschrieben.
*   **Strikte Validierung:** Eingabeprüfung via Pydantic (Längenbeschränkungen, Erlaubte Kategorien, Whitespace-Stripping).
*   **Erweiterte Filterung:** Filtere Notizen nach Kategorien, Tags, Erstellungsdatum (`created_after`/`created_before`) oder Volltextsuche in Titel und Inhalt.
*   **Statistik-Endpoint:** Erhalte auf einen Blick Metriken über die Gesamtanzahl, Kategorienverteilung und die Top 5 der am häufigsten genutzten Tags.

---

## Technologie-Stack

*   **Framework:** FastAPI
*   **ORM / Datenbank-Wrapper:** SQLModel (kombiniert SQLAlchemy & Pydantic)
*   **Datenbank:** SQLite (automatische Datei-Generierung unter `notes.db`)
*   **Validierung:** Pydantic v2

---

## Anforderungen & Installation

### 1. Repository klonen & Verzeichnis betreten
```bash
git clone <repository-url>
cd <repository-folder>