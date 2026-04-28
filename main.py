from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def lol():
    return {3+3-2+9} 
