from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()


users_db = []


class User(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(User):
    id: str



@app.get("/users", response_model=List[UserResponse])
def get_users(
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query("asc")
):
    results = users_db.copy()

    if search:
        results = [
            user for user in results
            if search.lower() in user["name"].lower()
            or search.lower() in user["email"].lower()
        ]

    
    if sort:
        reverse = True if order == "desc" else False
        try:
            results.sort(key=lambda x: x[sort], reverse=reverse)
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid sort field")

    return results


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", response_model=UserResponse)
def create_user(user: User):
    new_user = user.dict()
    new_user["id"] = str(uuid4())

    users_db.append(new_user)
    return new_user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, updated_user: User):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[index].update(updated_user.dict())
            return users_db[index]

    raise HTTPException(status_code=404, detail="User not found")



@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(index)
            return {"message": "User deleted successfully"}

    raise HTTPException(status_code=404, detail="User not found")