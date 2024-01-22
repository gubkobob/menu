from fastapi import APIRouter, FastAPI

from .database import engine
from .dishes import routes as routes_dishes
from .menus import routes as routes_menus
from .submenus import routes as routes_submenus

api_router = APIRouter()
api_router.include_router(routes_menus.router)
api_router.include_router(routes_submenus.router)
api_router.include_router(routes_dishes.router)

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
