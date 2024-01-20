from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, session, Base
from .menus import routes as routes_menus
# from .submenus import routes as routes_submenus
# from .dishes import routes as routes_dishes

api_router = APIRouter()
api_router.include_router(routes_menus.router)
# api_router.include_router(routes_submenus.router)
# api_router.include_router(routes_dishes.router)

app = FastAPI()
app.include_router(api_router, prefix="/api/v1/menus")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/api/test")
# def test1():
#     return {"id": 1, "name": "sasa"}


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
