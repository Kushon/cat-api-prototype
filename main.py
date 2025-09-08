from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from cat import Cat

app = FastAPI()
cats: dict[int, Cat] = {}
counter = 0

@app.post("/cats")
def create_cat(cat: Cat):   
    global counter
    counter+= 1
    cats[counter]= cat
    return {'id': counter, **cat.model_dump()}

@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int):
    if cat_id not in cats:
        raise HTTPException(status_code=404, detail="Cat not found")
    cats.pop(cat_id)
    return {"message": f"Cat with id '{cat_id}' was deleted"}

@app.get("/")
def get_cats():
    return cats

@app.patch("/cats/{cat_id}")
def update_cat(cat_id: int, cat_for_update: Cat):
    if cat_id not in cats:
        raise HTTPException(status_code=404, detail="Cat not found")
    cat_to_update = cats[cat_id]
    upd_data = cat_for_update.model_dump(exclude_unset=True)
    cats[cat_id] = cat_to_update.model_copy(update=upd_data)
    return cats[cat_id]

@app.get("/cats/{cat_id}")
def get_cat_by_id(cat_id: int):
    return cats.get(cat_id, {})

@app.get('/cats/')
def get_cat_by_name(cat_name: Optional[str] = None):
    if cat_name is None:
        return cats
    return [cat for cat in cats.values() if cat.name.lower() == cat_name]
