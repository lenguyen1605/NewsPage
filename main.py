from fastapi import FastAPI, HTTPException
import firebase_admin
from datetime import date, time, datetime
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, time, datetime
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import firestore, credentials
from google.cloud.firestore_v1 import FieldFilter
from pydantic import BaseModel
from typing import List, Optional
# import datetime
from datetime import datetime
import uuid
import jwt
from fastapi.encoders import jsonable_encoder

cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

origins = [
    "http://localhost:3000"
]
SECRET_KEY = "c0f216988e911e0ded52ed9b9f4fca53554f9984aefeb96075ed2a94803376fd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    email: str
    password: str
    username: str
    id_post: List[str]
    # author: False


class LogIn(BaseModel):
    email: str
    password: str


class Post(BaseModel):
    categories: List[str]
    content: str
    # date_created: datetime
    # id_author: str
    image: str
    likes: int
    title: str
    summary: str
    id_author: str


@app.post("/Signup")
def create_user(user_data: User):
    db = firestore.client()
    try:
        new_user = db.collection('users').document()
        new_user.set({"email": user_data.email, "password": user_data.password, "username": user_data.username})
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/Signin")
def log_in(user_data: LogIn):
    db = firestore.client()
    try:
        ar = []
        all_users = db.collection('users').stream()
        data = {}
        for user in all_users:
            user_info = user.to_dict()
            if user_info['email'] == user_data.email:
                if user_info['password'] == user_data.password:
                    data = {'email': user_data.email, 'password': user_data.password, 'username': user_info['username'],
                            'id_user': user.id}
                    print("data", data)
                    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
                    return {"token": encoded_jwt}
        return {"token": "Login failed"}
        # size = len([user for user in all_users])
        # if size == 0:
        #     return {"token": "Login failed"}
        # else:
        #     print([user for user in all_users])
        # print("size", size)
        # data = {
        #     "email": user_data.email,
        #     "password": user_data.password,
        #
        # }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/setPost")
def set_post(post_info: Post):
    db = firestore.client()
    try:
        random_id = uuid.uuid4()
        new_post = db.collection('post').document(str(random_id))
        doc_categories = [db.collection('categories').document(category) for category in post_info.categories]
        print(doc_categories)
        new_post.set({"content": post_info.content, "date_created": datetime.now(),
                      "id_author": db.collection('users').document(post_info.id_author),
                      "likes": post_info.likes,
                      "title": post_info.title, "image": post_info.image,
                      "summary": post_info.summary, "categories": doc_categories, "id": str(random_id)})
        for category in post_info.categories:
            cat_ref = db.collection('categories').document(category)
            new_post_list = cat_ref.get().get("posts")
            new_post_list.append(db.collection('post').document(str(random_id)))
            cat_ref.update({"posts": new_post_list})

        return {"message": "Post created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getAllPost")
def get_all_post():
    db = firestore.client()
    try:
        all_posts = []
        docs = db.collection('post').stream()
        for doc in docs:
            data = doc.to_dict()
            data['id_author'] = doc.get("id_author").id
            data['categories'] = [category_ref.id for category_ref in doc.get("categories")]
            # data['date_created'] = datetime.datetime.fromtimestamp(doc.get('date_created').timestamp())
            nanoseconds_datetime = data['date_created']

            # Convert to standard Python datetime object
            standard_datetime = datetime(
                year=nanoseconds_datetime.year,
                month=nanoseconds_datetime.month,
                day=nanoseconds_datetime.day,
                hour=nanoseconds_datetime.hour,
                minute=nanoseconds_datetime.minute,
                second=nanoseconds_datetime.second,
                microsecond=nanoseconds_datetime.nanosecond // 1000,

            )
            data['date_created'] = standard_datetime
            author_name = db.collection('users').document(doc.get('id_author').id)
            data['author_name'] = author_name.get().get("username")
            # print(data)
            all_posts.append(data)
        # print(all_posts)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getPostbyID")
def get_post_by_id(id):
    db = firestore.client()
    try:
        this_post = []
        post_ref = db.collection('post').document(id)
        post = post_ref.get().to_dict()
        post['id_author'] = post_ref.get().get("id_author").id
        post['categories'] = [category_ref.id for category_ref in post_ref.get().get("categories")]

        nanoseconds_datetime = post['date_created']

        # Convert to standard Python datetime object
        standard_datetime = datetime(
            year=nanoseconds_datetime.year,
            month=nanoseconds_datetime.month,
            day=nanoseconds_datetime.day,
            hour=nanoseconds_datetime.hour,
            minute=nanoseconds_datetime.minute,
            second=nanoseconds_datetime.second,
            microsecond=nanoseconds_datetime.nanosecond // 1000,

        )
        post['date_created'] = standard_datetime
        author_name = db.collection('users').document(post_ref.get().get('id_author').id)

        post['author_name'] = author_name.get().get("username")

        # print(post)
        # this_post.append(post)
        # print(this_post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getPostByCategory")
def get_post_by_category(category):
    db = firestore.client()
    try:
        all_posts = []

        cat_ref = db.collection('categories').document(category)
        cat = cat_ref.get().to_dict()
        for post in cat["posts"]:
            data = post.get().to_dict()
            data["id_author"] = post.get().get("id_author").id
            data["categories"] = [category_ref.id for category_ref in post.get().get("categories")]
            nanoseconds_datetime = data['date_created']

            # Convert to standard Python datetime object
            standard_datetime = datetime(
                year=nanoseconds_datetime.year,
                month=nanoseconds_datetime.month,
                day=nanoseconds_datetime.day,
                hour=nanoseconds_datetime.hour,
                minute=nanoseconds_datetime.minute,
                second=nanoseconds_datetime.second,
                microsecond=nanoseconds_datetime.nanosecond // 1000,

            )
            data['date_created'] = standard_datetime
            author_name = db.collection('users').document(post.get().get('id_author').id)

            data['author_name'] = author_name.get().get("username")
            all_posts.append(data)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
