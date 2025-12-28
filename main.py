from contextlib import asynccontextmanager
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, delete, select
from cat_schema import CatSchema
from cat_model import Cat
from db import async_session, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/cats")
async def create_cat(cat: CatSchema):
    cat_model = Cat(**cat.model_dump())

    async with async_session() as session:
        session.add(cat_model)
        await session.commit()
        await session.refresh(cat_model)

    return cat_model


@app.delete("/cats/{cat_id}")
async def delete_cat(cat_id: int):
    async with async_session() as session:
        stmt = delete(Cat).where(Cat.id == cat_id)
        await session.execute(stmt)
        await session.commit()

        return {"message": f"Cat with id '{cat_id}' was deleted"}


@app.get("/")
async def get_cats():
    async with async_session() as session:
        stmt = select(Cat)
        result = await session.execute(stmt)
        cats = result.scalars().all()
        return cats


@app.patch("/cats/{cat_id}")
async def update_cat(cat_id: int, cat_for_update: CatSchema):
    async with async_session() as session:
        stmt = select(Cat).where(Cat.id == cat_id)
        result = await session.execute(stmt)
        cat_to_update = result.scalars().first()
        if not cat_to_update:
            raise HTTPException(status_code=404, detail="Cat not found")

        for key, value in cat_for_update.model_dump(exclude_unset=True).items():
            setattr(cat_to_update, key, value)

        await session.commit()
        await session.refresh(cat_to_update)
        return cat_to_update


@app.get("/cats/{cat_id}")
async def get_cat_by_id(cat_id: int):
    async with async_session() as session:
        stmt = select(Cat).where(Cat.id == cat_id)
        result = await session.execute(stmt)
        cat = result.scalars().first()
        if not cat:
            raise HTTPException(status_code=404, detail="Cat not found")
        return cat


@app.get("/cats")
async def get_cat_by_name(cat_name: str):
    async with async_session() as session:
        stmt = select(Cat).where(Cat.name == cat_name)
        result = await session.execute(stmt)
        cats = result.scalars().all()
        return cats
