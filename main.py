from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
# HTTPException used to respond with proper HTTP error responses
# status gives constants for HTTP status codes
# used for correct REST API practices

from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse #NOT NEEDED ANYMORE
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates  # the {{}} thing used in templates is jinja2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession #needed for async
from sqlalchemy.orm import selectinload #needed for async
from starlette.exceptions import HTTPException as StarletteHTTPException  # the thing which actually deals with the http exception

import models
from database import Base, engine, get_db
from schemas import (UserCreate, UserUpdate, PostCreate, PostResponse,  UserResponse, PostUpdate)

from contextlib import asynccontextmanager #lifespan function needed for async
from fastapi.exception_handlers import (http_exception_handler, request_validation_exception_handler) #needed for async

# create database tables before the app is initialized
# works on all models that inherit from Base
# Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(_app:FastAPI):
    #startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) #enables lazy loading of tables, creates tables if they don't exist when the app starts up
    yield #enables eager loading of related objects in async context
    #shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# mount media directory for user uploaded content
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")
### CRUD
# C - CREATE - Post
# R - READ - GET 
# U - UPDATE - PUT/PATCH
# D - DELETE - DELETE


#SYNCHRONOUS PATH OPERATIONS
# running function with def keyword, runs in the main thread, blocks other operations until it finishes
# running route with async def allows other operations to run while waiting for the function to complete, 
# useful for I/O bound tasks like database queries or network requests

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)),) #.options is the eager loading
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = await db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    # dependency injection: we request a database session via Depends(get_db)
    # allows easy access to DB without manually creating sessions
    result = await db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    # scalars extracts the actual user object
    # first gets the first result (username is unique)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    result = await db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)  # stages the insert
    await db.commit()  # executes the insert and saves the user
    await db.refresh(new_user)  # refresh to get updated object with id
    return new_user

@app.patch("/api/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result=db.execute(select(models.User).where(models.User.id == user_id))
    user=result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user_update.username and user_update.username!= user.username:
        result= await db.execute(select(models.User).where(models.User.username == user_update.username))
        existing_user=result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if user_update.email and user_update.email != user.email:
        result= await db.execute(select(models.User).where(models.User.email == user_update.email))
        existing_email=result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            ) 
    
    if user_update.username is not None:
        user.username= user_update.username
    if user_update.email is not None:
        user.email= user_update.email
    if user_update.image_file is not None:
        user.image_file= user_update.image_file
    
    await db.commit()
    await db.refresh(user)
    return user

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    #figure out when to use selectinload. async def and await for db is simple enough to eunderstna.d THIS SHIT IS CONFUSING
    posts = result.scalars().all()
    return posts

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await db.delete(user)
    await db.commit()

@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    return posts


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    await db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id),)    
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_full(post_id:int,  post_data: PostCreate, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


    if post_data.user_id != post.user_id:
        result = await db.execute(select(models.User).where(models.User.id == post.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    
    post.title= post_data.title
    post.content= post_data.content
    post.user_id= post_data.user_id

    await db.commit()
    await db.refresh(post)
    return post


@app.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_partial (post_id: int, post_data:PostUpdate, db:Annotated[AsyncSession, Depends(get_db)]):
    result=await db.execute(select(models.Post).where(models.Post.id == post_id))
    post=result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


    update_data= post_data.model_dump(exclude_unset=True) #exclude_unset=True essentially makes sure pydantic only includes the field specified by the user to be updated in the patch method

    for field, value in update_data.items():
        setattr(post, field, value)


    await db.commit()
    await db.refresh(post)
    return post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await db.delete(post)
    await db.commit()


# THE EXCEPTION HANDLERS
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    

    # if API route, return JSON
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception) #replace json response with this for both exception handlers
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    # if data not matching expected type or structure
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
