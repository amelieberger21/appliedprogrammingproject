from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field as PydanticField
from pydantic import field_validator, model_validator, ConfigDict
from datetime import datetime, timezone
datetime.now(timezone.utc).isoformat()
import json
from pathlib import Path
from collections import Counter             
from typing import Optional, Annotated                
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, Relationship, select, or_, col
from typing_extensions import Self


ALLOWED_CATEGORIES = {
    "work",
    "personal",
    "school",
    "ideas",
    "general"
}

class NoteUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    title: str | None = PydanticField(
        default=None,
        min_length=3,
        max_length=100
    )

    content: str | None = PydanticField(
        default=None,
        min_length=1,
        max_length=10000
    )

    category: str | None = PydanticField(
        default=None,
        min_length=2,
        max_length=30,
        #pattern=r"^[a-z]+$"
    )

    tags: list[str] | None = PydanticField(
        default=None,
        max_length=10
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:

        if value is None:
            return value

        value = value.lower()

        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )

        return value
    
    @field_validator("tags")
    @classmethod
    def clean_tags(cls, raw: list[str] | None) -> list[str] | None:

        if raw is None:
            return raw

        cleaned = []
        seen = set()

        for tag in raw:
            t = tag.strip().lower()

            if not t:
                raise ValueError(
                    "tags must not be empty"
                )

            if len(t) < 2:
                raise ValueError(
                    "tags must have at least 2 characters"
                )

            if t in seen:
                continue

            seen.add(t)
            cleaned.append(t)

        return cleaned
    

class NoteTagLink(SQLModel, table=True):
    note_id: Optional[int] = SQLField(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = SQLField(default=None, foreign_key="tags.id", primary_key=True)


class Note(SQLModel, table=True):
    __tablename__ = 'notes'
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = SQLField(default_factory=datetime.now)
    
    # Many-to-many relationship with Tag (implicit link table)
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)

class Tag(SQLModel, table=True):
    __tablename__ = 'tags'
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(
    unique=True,
    index=True,
    min_length=2,
    max_length=30,
    regex=r"^[a-z0-9-]+$"
) 
    
    @field_validator("name")
    @classmethod
    def clean_tag_name(cls, value: str) -> str:

        return value.strip().lower()
    
    # Many-to-many relationship with Note (implicit link table)
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)


engine = create_engine("sqlite:///notes.db")

SQLModel.metadata.create_all(engine)


class NoteCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    title: str = PydanticField(
        min_length=3,
        max_length=100
    )

    content: str = PydanticField(
        min_length=1,
        max_length=10000
    )

    category: str = PydanticField(
        min_length=2,
        max_length=30,
        #pattern=r"^[a-z]+$"
    )

    tags: list[str] = PydanticField(
        default_factory=list,
        max_length=10
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:

        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "title must have at least 3 characters"
            )

        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:

        value = value.lower()

        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )

        return value

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, raw: list[str]) -> list[str]:

        cleaned = []
        seen = set()

        for tag in raw:

            t = tag.strip().lower()

            if not t:
                raise ValueError(
                    "tags must not be empty"
                )

            if len(t) < 2:
                raise ValueError(
                    "tags must have at least 2 characters"
                )

            if t in seen:
                continue

            seen.add(t)
            cleaned.append(t)

        return cleaned

'''
    @model_validator(mode="after")
    def work_notes_need_work_tag(self) -> Self:

        # model_validator nötig, weil category und tags gleichzeitig geprüft werden müssen

        if self.category == "work" and "work" not in self.tags:

            raise ValueError(
                "work notes must include the 'work' tag"
            )

        return self
   ''' 

    

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    
    class Config:
        from_attributes = True
        

NOTES_FILE = Path("data/notes.json")
notes_db = []
note_id_counter = 1


def load_notes():
    """Load notes from JSON file"""
    global notes_db, note_id_counter
    
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            notes_db = [
                Note(**{**note, "category": note.get("category", "default")})
                for note in data
            ]
            
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1


def save_notes():
    """Save notes to JSON file"""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)


def get_session():
    """Create a new database session for each request"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI(
    title="Note Taking API",
    description="Simple note management",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Notes API",
        "version": "1.0.0"
    }

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Create a new note in database"""
    
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    tag_objects = []
    seen_tags = set()
    
    for tag_name in note.tags:
        tag_name_lower = tag_name.lower().strip()
        if not tag_name_lower or tag_name_lower in seen_tags:
            continue
        
        seen_tags.add(tag_name_lower)
        
    
        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
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
    created_after: datetime | None = None,
    created_before: datetime | None = None
) -> list[NoteResponse]:
    """List notes with filters"""
    
   
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
        statement = statement.where(Note.created_at >= created_after)

    if created_before:
        statement = statement.where(Note.created_at <= created_before)
    
    
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
    notes = session.exec(select(Note)).all()
    tags = session.exec(select(Tag)).all()

    categories = {}
    for note in notes:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1

    tags_count = Counter()
    for tag in tags:
        tags_count[tag.name] = len(tag.notes)

    top_tags = []
    for tag, count in tags_count.most_common(5):
        top_tags.append({
            "tag": tag,
            "count": count
        })

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": len(tags)
    }


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)

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


@app.get("/notes/category/{category}")
def get_notes_by_category(category: str, session: SessionDep) -> list[NoteResponse]:
    statement = select(Note).where(Note.category == category)
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


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Get all unique tags from the Tag table"""
    statement = select(Tag)
    tags = session.exec(statement).all()
    
    return sorted([tag.name for tag in tags])


@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes with specific tag"""
    
    # Find the tag
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
            tags=[tag.name for tag in note.tags],
            created_at=note.created_at.isoformat()
        )
        for note in tag.notes
    ]


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    notes = session.exec(select(Note)).all()

    unique_categories = {}
    for note in notes:
        if note.category not in unique_categories:
            unique_categories[note.category] = 1

    categories_list = []
    for category in unique_categories:
        categories_list.append(category)

    return sorted(categories_list)


@app.get("/categories/{category_name}/notes")
def get_notes_by_category_resource(category_name: str, session: SessionDep) -> list[NoteResponse]:
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

@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category

    tag_objects = []
    seen_tags = set()

    for tag_name in note_update.tags:
        tag_name_lower = tag_name.lower().strip()

        if not tag_name_lower or tag_name_lower in seen_tags:
            continue

        seen_tags.add(tag_name_lower)

        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()

        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
            session.add(new_tag)
            tag_objects.append(new_tag)

    note.tags = tag_objects

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


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_update.title is not None:
        note.title = note_update.title

    if note_update.content is not None:
        note.content = note_update.content

    if note_update.category is not None:
        note.category = note_update.category

    if note_update.tags is not None:
        tag_objects = []
        seen_tags = set()

        for tag_name in note_update.tags:
            tag_name_lower = tag_name.lower().strip()

            if not tag_name_lower or tag_name_lower in seen_tags:
                continue

            seen_tags.add(tag_name_lower)

            statement = select(Tag).where(Tag.name == tag_name_lower)
            existing_tag = session.exec(statement).first()

            if existing_tag:
                tag_objects.append(existing_tag)
            else:
                new_tag = Tag(name=tag_name_lower)
                session.add(new_tag)
                tag_objects.append(new_tag)

        note.tags = tag_objects

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


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()
    return

'''
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

#@=Decorator /name (name)=kann eigenen namen angeben, wenn name angegeben wird läuft Funktion darunter durch
@app.get("/name/{name}")
def greet_name(name: str):
    return {"message": f"Hello,{name}!"} #IP/name/Manuel -> Ausgabe im Browser

#Aufgabe: Weiteren Endpunkt bauen:
@app.get("/zahl/{zahl}")
def add_one(zahl: int):
    return {zahl +1}
'''

 
@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:
    namen = ['amelie', 'roman', 'sophia', 'artemas', 'helenefischer', 'olafscholz', 'deathnotetheanime', 'janeausten', 'martindercoolsteprof']
    if not param1:
        return{"namen": namen}
    
    namen_gefiltert = []
    for name in namen:
        if param1 is None or param1 in name:
            namen_gefiltert.append(name)

    return {
        "param1": param1,
        "param2": param2,
        "namen": namen_gefiltert
    }


@app.get("/test/123")
def test_fixed():
    return {
        "fixed message": "Hallo 123"
        }

@app.get("/test/{value}")
def test_value(value: str):
    return {
        "value": value
    }

@app.get("/test/{value}/test2/{value2}")
def test_test2_value(value: str, value2: str):
    return {
        "value": value,
        "value2": value2
    }

@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:
    namen = ['amelie', 'roman', 'sophia', 'artemas', 'helenefischer', 'olafscholz', 'deathnotetheanime', 'janeausten', 'martindercoolsteprof']