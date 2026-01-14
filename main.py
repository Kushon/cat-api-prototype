from contextlib import asynccontextmanager
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, delete, select
from cat_schema import CatSchema
from cat_model import Cat
from db import async_session, engine
from cache import cache_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    await cache_manager.connect()
    
    yield
    
    await cache_manager.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post("/cats")
async def create_cat(cat: CatSchema):
    """Create new cat and invalidate cache."""
    cat_model = Cat(**cat.model_dump())

    async with async_session() as session:
        session.add(cat_model)
        await session.commit()
        await session.refresh(cat_model)
    
    await cache_manager.delete("cats:all")

    return cat_model


@app.delete("/cats/{cat_id}")
async def delete_cat(cat_id: int):
    """Delete cat and invalidate cache."""
    async with async_session() as session:
        stmt = delete(Cat).where(Cat.id == cat_id)
        await session.execute(stmt)
        await session.commit()
    
    await cache_manager.delete("cats:all")
    
    return {"message": f"Cat with id '{cat_id}' was deleted"}


@app.get("/")
async def get_cats():
    """Get all cats with caching."""
    cache_key = "cats:all"
    
    cached_cats = await cache_manager.get(cache_key)
    if cached_cats is not None:
        return cached_cats
    
    async with async_session() as session:
        stmt = select(Cat)
        result = await session.execute(stmt)
        cats = result.scalars().all()
    
    await cache_manager.set(cache_key, cats, ttl=300)
    
    return cats


@app.patch("/cats/{cat_id}")
async def update_cat(cat_id: int, cat_for_update: CatSchema):
    """Update cat and invalidate cache."""
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
    
    await cache_manager.delete("cats:all")
    await cache_manager.delete(f"cat:{cat_id}")
    
    return cat_to_update


@app.get("/cats/{cat_id}")
async def get_cat_by_id(cat_id: int):
    """Get cat by ID with caching."""
    cache_key = f"cat:{cat_id}"
    
    cached_cat = await cache_manager.get(cache_key)
    if cached_cat is not None:
        return cached_cat
    
    async with async_session() as session:
        stmt = select(Cat).where(Cat.id == cat_id)
        result = await session.execute(stmt)
        cat = result.scalars().first()
    
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    await cache_manager.set(cache_key, cat, ttl=600)
    
    return cat


@app.get("/cats/search")
async def get_cat_by_name(cat_name: str):
    """Search cats by name with caching."""
    cache_key = f"cat:name:{cat_name}"
    
    cached_cats = await cache_manager.get(cache_key)
    if cached_cats is not None:
        return cached_cats
    
    async with async_session() as session:
        stmt = select(Cat).where(Cat.name == cat_name)
        result = await session.execute(stmt)
        cats = result.scalars().all()
    
    await cache_manager.set(cache_key, cats, ttl=300)
    
    return cats


@app.get("/cache/status")
async def cache_status():
    """Get cache status."""
    return {
        "enabled": cache_manager.enabled,
        "connected": cache_manager.redis_client is not None,
        "host": cache_manager.host,
        "port": cache_manager.port,
    }


@app.delete("/cache/flush")
async def flush_cache():
    """Clear all cache."""
    result = await cache_manager.flush()
    return {
        "success": result,
        "message": "Cache flushed successfully" if result else "Failed to flush cache"
    }
@app.get("/ra")
async def ra():
    await cache_manager.set('key', 'value')
    return {"message": "RAAAAAAAA"}