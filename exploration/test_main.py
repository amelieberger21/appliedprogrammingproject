@app.get("/courses/{course_id}")
def get_course(course_id: int):
    # course_id is automatically converted to int
    pass

@app.get("/courses/code/{course_code}")
def get_course_by_code(course_code: str):
    # course_code stays as string
    pass

@app.get("/students/{student_id}/courses/{course_id}")
def get_student_course(student_id: int, course_id: int):
    # Multiple path parameters
    pass 

@app.get("/courses")
def list_courses(
    semester: int = None,
    min_ects: int = 0,
    search: str = None
):
    # Apply all filters
    pass

@app.get("/courses")
def list_courses(
    semester: int = None,      # Optional, no filter if omitted
    limit: int = 10,           # Default 10 if not specified
    offset: int = 0            # Default 0 if not specified
):
    pass

class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str  # From homework!
    created_at: str

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.1.0",
        "day": 1}

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.1.0",
        "day": 1} 
