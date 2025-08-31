from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from src.shared.constants import version, title, description
from src.routes import files_route,health_route


app = FastAPI(version=version, title=title, description=description)

app.include_router(health_route.router)
app.include_router(files_route.router)
