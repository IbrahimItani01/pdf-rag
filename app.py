from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.shared.constants import version, title, description,origins
from src.routes import files_route,health_route,users_route


app = FastAPI(version=version, title=title, description=description)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],
)


app.include_router(health_route.router)
app.include_router(files_route.router)
app.include_router(users_route.router)
