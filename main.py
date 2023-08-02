from fastapi import FastAPI, HTTPException
import firebase_admin

from firebase_admin import firestore, credentials
from pydantic import BaseModel

cred = credentials.Certificate("/Users/nguyennhatle/PycharmProjects/my-project/credentials.json")
firebase_admin.initialize_app(cred)

app = FastAPI()


class Item(BaseModel):
    name: str
    age: int


@app.post("/users")
def create_user(user_data: Item):
    db = firestore.client()
    # return {"message": "success"}
    try:
        new_user = db.collection('users').document(user_data.name)
        new_user.set({"name": user_data.name, "age": user_data.age})
        # new_user.set({"name": "John Doe"})
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/average")
def get_average():
    db = firestore.client()
    sum_age = 0
    total_users = 0
    try:
        all_users = db.collection('users').stream()
        for user_doc in all_users:
            user_data = user_doc.to_dict()
            sum_age += user_data['age']
            total_users += 1
        return {"average": sum_age/total_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
