from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional
import re
from sqlmodel import SQLModel, Field, Session, col, create_engine, Relationship, or_, select
from typing import Annotated
from fastapi import Depends


class NoteTag(SQLModel, table=True):
    __tablename__ = "note_tag"
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)
    


class Note(SQLModel, table=True):
    __tablename__ = 'notes'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)

    
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)

class Tag(SQLModel, table=True):
    __tablename__ = 'tags'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        unique=True, 
        index=True,
        min_length=2,
        max_length=30
    )
    
    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v):
        """
        Prueft den Tag-Namen und macht ihn einheitlich:
        - Leerzeichen vorne und hinten entfernen
        - alles klein schreiben
        - nur kleine Buchstaben, Zahlen und Bindestriche erlauben
        """
        if not isinstance(v, str):
            raise ValueError("name must be a string")
        
        
        v = v.strip().lower()
        
        
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("name must contain only lowercase letters, digits, and dashes")
        
        return v
    
    
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTag)
    


engine = create_engine("sqlite:///notes.db")


SQLModel.metadata.create_all(engine)

def validate_and_normalize_tag(tag_name: str) -> str:
    """
    Prueft einen Tag-Namen und macht ihn einheitlich:
    - Leerzeichen vorne und hinten entfernen
    - alles klein schreiben
    - Laenge pruefen (2 bis 30 Zeichen)
    - nur kleine Buchstaben, Zahlen und Bindestriche erlauben

    Wenn etwas falsch ist, wird ein ValueError geworfen.
    Zurueck kommt der bereinigte Tag-Name.
    """
    if not isinstance(tag_name, str):
        raise ValueError("tag name must be a string")
    
    
    tag_name = tag_name.strip().lower()
    
    
    if len(tag_name) < 2:
        raise ValueError("tag name must be at least 2 characters")
    
    
    if len(tag_name) > 30:
        raise ValueError("tag name must be at most 30 characters")
    
    
    if not re.match(r"^[a-z0-9-]+$", tag_name):
        raise ValueError("tag name must contain only lowercase letters, digits, and dashes")
    
    return tag_name

def get_session():
    """Erstellt fuer jede Anfrage eine neue Datenbank-Session."""
    with Session(engine) as session:
        yield session


def parse_iso_datetime(value: Optional[str], param_name: str) -> Optional[datetime]:
    if value is None:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail={"loc": ["query", param_name], "msg": "Invalid datetime format", "type": "value_error"},
        )


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(
    title="Note Taking API",
    description="Einfache Notizenverwaltung",
    version="1.0.0"
)

@app.get("/")
def root():
    
    return {"message": "Hello, World!"}

@app.get("/name/{name}")
def greet_name(name: str):
    
    return {"message": f"Hello, {name}!"}

@app.get("/calculate/{number}")
def calculate(number: float):
    result = number * 4 + 5
   
    return {"message": f"Der verrechnete Wert von {number} ist {result}"}




class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10000)
    category: str = Field(min_length=2, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=10)
    
    
    {
        "str_strip_whitespace": True,
        "extra": "forbid"
    }
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """Prueft jeden Tag in der Liste."""
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
        
        
        validated_tags = []
        seen = set()
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("each tag must be a string")
            
           
            try:
                tag_normalized = validate_and_normalize_tag(tag)
            except ValueError as e:
                raise ValueError(f"Invalid tag '{tag}': {str(e)}")
            
            
            if tag_normalized not in seen:
                validated_tags.append(tag_normalized)
                seen.add(tag_normalized)
        
        return validated_tags


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    
    class Config:
        from_attributes = True
    


class FileNote(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str

NOTES_FILE = Path("data/notes.json")

def load_notes():
    """Laedt Notizen aus der JSON-Datei und gibt auch die naechste ID zurueck."""
    notes_db = []
    note_id_counter = 1

    
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
        
            for note_dict in data:
                if 'tags' not in note_dict:
                    note_dict['tags'] = []

            
            notes_db = [FileNote(**note_dict) for note_dict in data]

            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Speichert die Notizen nach jeder Aenderung in der JSON-Datei."""

    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Erstellt eine neue Notiz in der Datenbank."""
    

    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    

    tag_objects = []
    seen_tags = set()
    
    
    for tag_name in note.tags:
        try:
            
            tag_name_normalized = validate_and_normalize_tag(tag_name)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Invalid tag: {str(e)}")
        
        
        if tag_name_normalized in seen_tags:
            continue
        
        seen_tags.add(tag_name_normalized)
        
        
        statement = select(Tag).where(Tag.name == tag_name_normalized)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_normalized)
            session.add(new_tag)
            tag_objects.append(new_tag)
    
    
    db_note.tags = tag_objects
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)  
    
    
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        category=db_note.category,
        tags=[tag.name for tag in db_note.tags],
        created_at=db_note.created_at.isoformat()
    )

@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
) -> list[NoteResponse]:
    """Listet Notizen auf. Filter koennen optional genutzt werden."""
    
    
    statement = select(Note)
    
    
    if category:
        statement = statement.where(Note.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(Note.tags).where(Tag.name == tag_lower)

    if created_after:
        created_after_dt = parse_iso_datetime(created_after, "created_after")
        statement = statement.where(Note.created_at >= created_after_dt)

    if created_before:
        created_before_dt = parse_iso_datetime(created_before, "created_before")
        statement = statement.where(Note.created_at <= created_before_dt)
    
    
    notes = session.exec(statement).all()
    
    
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]

@app.get("/notes/category/{category}")
def get_notes_by_category(category: str, session: SessionDep) -> list[NoteResponse]:
    """Gibt alle Notizen aus einer bestimmten Kategorie zurueck."""
    statement = select(Note).where(Note.category == category)
    notes = session.exec(statement).all()
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]


@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    """Gibt einfache Statistiken zu den Notizen zurueck."""
    # Alle Notizen mit ihren Tags laden.
    notes = session.exec(select(Note)).all()


    categories: dict[str, int] = {}
    tag_counts: dict[str, int] = {}

    
    for note in notes:
        categories[note.category] = categories.get(note.category, 0) + 1
        for tag in getattr(note, "tags", []) or []:
            # Tags sind in der Datenbank eigene Objekte.
            tag_name = getattr(tag, "name", None) or str(tag)
            tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1

    
    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    ][:5]

    unique_tags_count = len(session.exec(select(Tag)).all())

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": unique_tags_count
    }


@app.get("/notes/{note_id}")
def get_note(note_id: str, session: SessionDep) -> NoteResponse:
    """Gibt eine bestimmte Notiz ueber ihre ID zurueck."""
    try:
        note_id_int = int(note_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="note_id must be an integer")

    statement = select(Note).where(Note.id == note_id_int)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )



@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    """Aktualisiert eine vorhandene Notiz komplett."""

    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")


    update_data = note_update.dict(exclude_unset=True)

   
    if "tags" in update_data:
        tag_objects = []
        seen = set()
        for tag_name in update_data["tags"]:
            tag_name_lower = tag_name.lower().strip()
            if not tag_name_lower or tag_name_lower in seen:
                continue
            seen.add(tag_name_lower)
            stmt = select(Tag).where(Tag.name == tag_name_lower)
            existing = session.exec(stmt).first()
            if existing:
                tag_objects.append(existing)
            else:
                new_tag = Tag(name=tag_name_lower)
                session.add(new_tag)
                tag_objects.append(new_tag)

        note.tags = tag_objects


    for key, value in update_data.items():
        if key == "tags":
            continue
        setattr(note, key, value)

    session.commit()
    session.refresh(note)
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    """Loescht eine Notiz."""
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return Response(status_code=204)


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Gibt alle Tags zurueck, aber jeden Tag nur einmal."""
    statement = select(Tag)
    tags = session.exec(statement).all()
    
    return sorted([tag.name for tag in tags])



@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Gibt alle Notizen mit einem bestimmten Tag zurueck."""
    
    
    tag_lower = tag_name.lower()
    statement = select(Tag).where(Tag.name == tag_lower)
    tag = session.exec(statement).first()
    
    if not tag:
        return []  
    
    
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            category=note.category,
            tags=[t.name for t in note.tags],
            created_at=note.created_at.isoformat()
        )
        for note in tag.notes
    ]



@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    """Gibt alle Kategorien zurueck, aber jede Kategorie nur einmal."""
    statement = select(Note.category).distinct()
    categories = session.exec(statement).all()
    
    return sorted(categories)



@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    """Gibt alle Notizen aus einer bestimmten Kategorie zurueck."""
    statement = select(Note).where(Note.category == category_name)
    notes = session.exec(statement).all()
    
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            category=note.category,
            tags=[tag.name for tag in note.tags],
            created_at=note.created_at.isoformat()
        )
        for note in notes
    ]



class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = Field(None, min_length=2, max_length=30)
    tags: Optional[list[str]] = Field(None, max_length=10)
    
    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid"
    }
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """Prueft jeden Tag in der Liste, falls Tags angegeben wurden."""
        if v is None:
            return None
        
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
        
        
        validated_tags = []
        seen = set()
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("each tag must be a string")
            
            
    
            try:
                tag_normalized = validate_and_normalize_tag(tag)
            except ValueError as e:
                raise ValueError(f"Invalid tag '{tag}': {str(e)}")
            
            
            if tag_normalized not in seen:
                validated_tags.append(tag_normalized)
                seen.add(tag_normalized)
        
        return validated_tags
    
    @model_validator(mode="after")
    def validate_work_category_requires_work_tag(self):
        """
        Pruefung ueber mehrere Felder:
        Wenn die Kategorie "work" ist, muss auch der Tag "work" dabei sein.
        Das wird nur geprueft, wenn Kategorie und Tags angegeben wurden.
        """
        if self.category == "work" and self.tags is not None and "work" not in self.tags:
            raise ValueError("work notes must include the 'work' tag")
        return self

@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    """
    Aktualisiert eine Notiz teilweise.
    
    Im Gegensatz zu PUT werden nur die angegebenen Felder geaendert.
    """
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    
    update_data = note_update.dict(exclude_unset=True)

    
    if "tags" in update_data:
        tag_objects = []
        seen = set()
        for tag_name in update_data["tags"]:
            try:
                
                tag_name_normalized = validate_and_normalize_tag(tag_name)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=f"Invalid tag: {str(e)}")
            
           
            if tag_name_normalized in seen:
                continue
            seen.add(tag_name_normalized)
            
            stmt = select(Tag).where(Tag.name == tag_name_normalized)
            existing = session.exec(stmt).first()
            if existing:
                tag_objects.append(existing)
            else:
                new_tag = Tag(name=tag_name_normalized)
                session.add(new_tag)
                tag_objects.append(new_tag)

        note.tags = tag_objects

    for key, value in update_data.items():
        if key == "tags":
            continue
        setattr(note, key, value)

    session.add(note)
    session.commit()
    session.refresh(note)

    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )

