In dem projekt *Appliedprogramming* wurden eine performante und leichtgewichtige REST-API zur Verwaltung von Notizen. Das Projekt basiert auf **FastAPI** und nutzt **SQLModel** (SQLAlchemy + Pydantic) für eine robuste Datenvalidierung und nahtlose SQLite-Datenbankinteraktion.

---

## Features

*   **Vollständiges CRUD**: Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Löschen von Notizen.
*   **Many-to-Many Tagging**: Notizen können beliebig viele Tags besitzen. Tags werden automatisch datenbankseitig dedupliziert und bereinigt.
*   **Strikte Validierung**: Validierung von Eingabedaten über Pydantic (inkl. Whitespace-Stripping, Längenbeschränkungen und Regex-Prüfungen für Tags).
*   **Erweiterte Filterung**: Filtere Notizen nach Kategorie, Tags, Volltextsuche im Inhalt/Titel oder Erstellungszeitraum (`created_after` / `created_before`).
*   **Statistik-Endpunkt**: Aggregierte Metriken über die Gesamtanzahl, Notizen pro Kategorie und die Top-5 der am häufigsten genutzten Tags.

---

## Datenmodell & Validierung

Die API erzwingt vordefinierte Regeln für eine saubere Datenstruktur:

### Erlaubte Kategorien
Notizen müssen genau einer der folgenden Kategorien zugeordnet sein:
`work`, `personal`, `school`, `ideas`, `general` (Groß-/Kleinschreibung wird automatisch angepasst).

### Validierungsregeln
*   **Titel**: Min. 3, max. 100 Zeichen.
*   **Inhalt**: Min. 1, max. 10000 Zeichen.
*   **Tags**: Müssen zwischen 2 und 30 Zeichen lang sein, dürfen nur Kleinbuchstaben, Zahlen und Bindestriche enthalten (`^[a-z0-9-]+$`). Maximal 10 Tags pro Notiz.

---

## API Endpunkte (Übersicht)

### Notizen (Notes)
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/notes` | Listet alle Notizen (Unterstützt Query-Filter: `category`, `search`, `tag`, `created_after`, `created_before`) |
| **POST** | `/notes` | Erstellt eine neue Notiz (Status `201 Created`) |
| **GET** | `/notes/{note_id}` | Gibt eine spezifische Notiz anhand ihrer ID zurück |
| **PUT** | `/notes/{note_id}` | Aktualisiert eine Notiz vollständig |
| **PATCH** | `/notes/{note_id}` | Aktualisiert eine Notiz teilweise (Partial Update) |
| **DELETE** | `/notes/{note_id}` | Löscht eine Notiz (Status `204 No Content`) |

### Kategorien & Tags
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/notes/stats` | Liefert globale Statistiken (Top-Tags, Kategorien-Verteilung) |
| **GET** | `/categories` | Gibt alle aktuell genutzten Kategorien sortiert zurück |
| **GET** | `/categories/{category_name}/notes` | Gibt alle Notizen einer bestimmten Kategorie zurück |
| **GET** | `/tags` | Gibt alle existierenden Tags alphabetisch sortiert zurück |
| **GET** | `/tags/{tag_name}/notes` | Gibt alle Notizen zurück, die ein bestimmtes Tag besitzen |
| **GET** | `/` | Root-Verzeichnis mit API-Metadaten |

---

## Installation & Start

### 1. Voraussetzungen
Stelle sicher, dass Python (Version 3.10 oder höher empfohlen) installiert ist.

### 2. Abhängigkeiten installieren
Erstelle optional eine virtuelle Umgebung und installiere die benötigten Pakete:

```bash
pip install fastapi uvicorn sqlmodel pydantic

```

### 3. API starten

Speichere den Code in einer Datei (z. B. `main.py`) und starte den Uvicorn-Server:

```bash
uvicorn main:app --reload

```

> **Hinweis**: Beim ersten Start wird automatisch eine SQLite-Datenbankdatei namens `notes.db` im Projektverzeichnis erstellt und alle Tabellen (`notes`, `tags`, `notetaglink`) werden initialisiert.

---

## Interaktive Dokumentation

Sobald der Server läuft, stellt FastAPI automatisch eine interaktive API-Dokumentation zur Verfügung, über die alle Endpunkte direkt im Browser getestet werden können:

* **Swagger UI**: [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](https://www.google.com/search?q=http://127.0.0.1:8000/redoc)

---

## Projektstruktur (Logik im Code)

* **Datenbank**: SQLite via `SQLModel`. Die Session-Verwaltung erfolgt sicher über einen Context Manager per Dependency Injection (`SessionDep`).
Hier ist eine professionelle, übersichtliche und direkt einsatzbereite **README.md** für dein FastAPI-Projekt.

---

```markdown
# Note Taking API

Eine robuste und performante REST-API zur Verwaltung von Notizen, gebaut mit **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic) und **SQLite**. Die API unterstützt Kategorisierungen, ein dynamisches Many-to-Many-Tagging-System sowie umfangreiche Filter- und Statistik-Funktionen.

---

## Features

*   **Vollständiges CRUD**: Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Löschen von Notizen.
*   **Many-to-Many Tagging**: Notizen können beliebig viele Tags besitzen. Tags werden automatisch datenbankseitig dedupliziert und bereinigt.
*   **Strikte Validierung**: Validierung von Eingabedaten über Pydantic (inkl. Whitespace-Stripping, Längenbeschränkungen und Regex-Prüfungen für Tags).
*   **Erweiterte Filterung**: Filtere Notizen nach Kategorie, Tags, Volltextsuche im Inhalt/Titel oder Erstellungszeitraum (`created_after` / `created_before`).
*   **Statistik-Endpunkt**: Aggregierte Metriken über die Gesamtanzahl, Notizen pro Kategorie und die Top-5 der am häufigsten genutzten Tags.

---

## Datenmodell & Validierung

Die API erzwingt vordefinierte Regeln für eine saubere Datenstruktur:

### Erlaubte Kategorien
Notizen müssen genau einer der folgenden Kategorien zugeordnet sein:
`work`, `personal`, `school`, `ideas`, `general` (Groß-/Kleinschreibung wird automatisch angepasst).

### Validierungsregeln
*   **Titel**: Min. 3, max. 100 Zeichen.
*   **Inhalt**: Min. 1, max. 10000 Zeichen.
*   **Tags**: Müssen zwischen 2 und 30 Zeichen lang sein, dürfen nur Kleinbuchstaben, Zahlen und Bindestriche enthalten (`^[a-z0-9-]+$`). Maximal 10 Tags pro Notiz.

---

## API Endpunkte (Übersicht)

### Notizen (Notes)
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/notes` | Listet alle Notizen (Unterstützt Query-Filter: `category`, `search`, `tag`, `created_after`, `created_before`) |
| **POST** | `/notes` | Erstellt eine neue Notiz (Status `201 Created`) |
| **GET** | `/notes/{note_id}` | Gibt eine spezifische Notiz anhand ihrer ID zurück |
| **PUT** | `/notes/{note_id}` | Aktualisiert eine Notiz vollständig |
| **PATCH** | `/notes/{note_id}` | Aktualisiert eine Notiz teilweise (Partial Update) |
| **DELETE** | `/notes/{note_id}` | Löscht eine Notiz (Status `204 No Content`) |

### Kategorien & Tags
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/notes/stats` | Liefert globale Statistiken (Top-Tags, Kategorien-Verteilung) |
| **GET** | `/categories` | Gibt alle aktuell genutzten Kategorien sortiert zurück |
| **GET** | `/categories/{category_name}/notes` | Gibt alle Notizen einer bestimmten Kategorie zurück |
| **GET** | `/tags` | Gibt alle existierenden Tags alphabetisch sortiert zurück |
| **GET** | `/tags/{tag_name}/notes` | Gibt alle Notizen zurück, die ein bestimmtes Tag besitzen |
| **GET** | `/` | Root-Verzeichnis mit API-Metadaten |

---

## Installation & Start

### 1. Voraussetzungen
Stelle sicher, dass Python (Version 3.10 oder höher empfohlen) installiert ist.

### 2. Abhängigkeiten installieren
Erstelle optional eine virtuelle Umgebung und installiere die benötigten Pakete:

```bash
pip install fastapi uvicorn sqlmodel pydantic

```

### 3. API starten

Speichere den Code in einer Datei (z. B. `main.py`) und starte den Uvicorn-Server:

```bash
uvicorn main:app --reload

```

> **Hinweis**: Beim ersten Start wird automatisch eine SQLite-Datenbankdatei namens `notes.db` im Projektverzeichnis erstellt und alle Tabellen (`notes`, `tags`, `notetaglink`) werden initialisiert.

---

## Interaktive Dokumentation

Sobald der Server läuft, stellt FastAPI automatisch eine interaktive API-Dokumentation zur Verfügung, über die alle Endpunkte direkt im Browser getestet werden können:

* **Swagger UI**: [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](https://www.google.com/search?q=http://127.0.0.1:8000/redoc)

---

## Projektstruktur (Logik im Code)

* **Datenbank**: SQLite via `SQLModel`. Die Session-Verwaltung erfolgt sicher über einen Context Manager per Dependency Injection (`SessionDep`).
* **Datenbereinigung**: Benutzereingaben bei Tags und Kategorien werden vor dem Speichern via Pydantic-`field_validator` automatisch in Kleinbuchstaben umgewandelt und von führenden/folgenden Leerzeichen befreit. Duplicate-Prevention sorgt dafür, dass keine doppelten Tags in der Datenbank oder der Notiz landen.

```

```