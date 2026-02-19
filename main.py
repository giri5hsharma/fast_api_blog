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

# from schemas import (UserCreate, UserUpdate, PostCreate, PostResponse,  UserResponse, PostUpdate)
# dont need schemas cuz they being using by the individual routers 

#ROUTERS need the basic router direectory with the __init__.py mandatory
from routers import posts, users

from contextlib import asynccontextmanager #lifespan function needed for async
from fastapi.exception_handlers import (http_exception_handler, request_validation_exception_handler) #needed for async

# create database tables before the app is initialized
# works on all models that inherit from Base
# Base.metadata.create_all(bind=engine)

#ALSO WHILE MKAING IT ASYNC WITH DATABSE ADD AWAT WITH COMMIT REFRESH AND EXECUTED, NOT ADD
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

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])


#SYNCHRONOUS PATH OPERATIONS
# running function with def keyword, runs in the main thread, blocks other operations until it finishes
# running route with async def allows other operations to run while waiting for the function to complete, 
# useful for I/O bound tasks like database queries or network requests

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).order_by(models.Post.date_posted.desc()),) #.options is the eager loading
    #.order_by(models.Post.date_posted.desc()) --> ordering posts by descending order
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
    result = await db.execute(select(models.User).where(models.User.id == user_id).order_by(models.Post.date_posted.desc()))
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
