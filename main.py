from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import json
from pathlib import Path
from typing import Optional

# ===== FastAPI App =====
app = FastAPI(
    title="Note Taking API",
    description="Simple note management system",
    version="1.0.0"
)

# ===== Models =====
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=1, max_length=10000)
    category: str = Field(..., min_length=2, max_length=30)


class Note(NoteCreate):
    id: int
    created_at: str


# ===== Global Variables =====
NOTES_FILE = Path("data/notes.json")
ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas", "general"}

notes_db: list[Note] = []
note_id_counter: int = 1


# ===== Helper Functions =====
def load_notes() -> tuple[list[Note], int]:
    """Load notes from JSON file and return notes list and next ID counter"""
    global notes_db, note_id_counter
    
    notes_db = []
    note_id_counter = 1

    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            notes_db = [Note(**note) for note in data]

            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes: list[Note]) -> None:
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        # Convert Note objects to dicts
        notes_data = [note.model_dump() for note in notes]
        json.dump(notes_data, f, indent=2, ensure_ascii=False)


# ===== Load notes on startup =====
notes_db, note_id_counter = load_notes()


# ===== Root Endpoints =====
@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Note Taking API", "version": "1.0.0"}


@app.get("/status")
def get_status():
    """Get API status"""
    return {
        "status": "online",
        "version": "1.0.0",
        "total_notes": len(notes_db)
    }


@app.get("/student")
def get_student():
    """Get student information"""
    return {
        "name": "Amelie Berger",
        "semester": 1,
        "course": "Wirtschaftsinformatik",
        "university": "Hochschule Coburg"
    }


# ===== Square Calculator Endpoint (Hausaufgabe) =====
@app.get("/square/{number}")
def calculate_square(number: int):
    """Calculate the square of a number"""
    result = number * number
    return {
        "number": number,
        "square": result,
        "calculation": f"{number} × {number} = {result}"
    }


# ===== Notes Endpoints =====
@app.get("/notes")
def list_notes(category: Optional[str] = None) -> list[Note]:
    """Get a list of all notes, optionally filtered by category"""
    if category:
        category = category.lower()
        if category not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Allowed: {sorted(ALLOWED_CATEGORIES)}"
            )
        return [note for note in notes_db if note.category.lower() == category]
    
    return notes_db


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note:
    """Create a new note"""
    global note_id_counter, notes_db
    
    # Validate category
    if note.category.lower() not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Allowed: {sorted(ALLOWED_CATEGORIES)}"
        )
    
    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        category=note.category.lower(),
        created_at=datetime.now().isoformat()
    )
    
    notes_db.append(new_note)
    note_id_counter += 1
    save_notes(notes_db)
    
    return new_note


@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note:
    """Get a specific note by ID"""
    for note in notes_db:
        if note.id == note_id:
            return note
    
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )


@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate) -> Note:
    """Update an existing note"""
    # Validate category
    if note_update.category.lower() not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Allowed: {sorted(ALLOWED_CATEGORIES)}"
        )
    
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            updated_note = Note(
                id=note_id,
                title=note_update.title,
                content=note_update.content,
                category=note_update.category.lower(),
                created_at=note.created_at
            )
            notes_db[i] = updated_note
            save_notes(notes_db)
            return updated_note
    
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note by ID"""
    global notes_db
    
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return
    
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )
