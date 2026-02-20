# FastAPI Async Blog API

A fully asynchronous RESTful blog API built with **FastAPI**, **SQLAlchemy (async)**, and **Pydantic**.
This project demonstrates a clean, modular backend architecture with complete **CRUD operations** for users and posts.

---

## Features

* Fully asynchronous API using **FastAPI** and **SQLAlchemy AsyncSession**
* Modular router-based architecture
* Complete CRUD operations for:

  * Users
  * Posts
* Input validation using **Pydantic**
* Automatic OpenAPI/Swagger documentation
* Template rendering using **Jinja2**
* Static and media file serving
* Proper HTTP error handling
* Eager loading of relationships to avoid async lazy-loading issues

---

## Tech Stack

**Backend**

* FastAPI
* Python (async/await)

**Database**

* SQLite
* SQLAlchemy (Async ORM)

**Data Validation**

* Pydantic

**Templating**

* Jinja2

---

## Project Structure

```
project/
│
├── main.py              # Application entry point
├── database.py          # Async DB engine and session
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic schemas
│
├── routers/
│   ├── posts.py         # Post endpoints
│   └── users.py         # User endpoints
│
├── templates/           # Jinja2 templates
├── static/              # Static files
├── media/               # Uploaded media
│
└── blog.db              # SQLite database
```

---

## API Endpoints

### Users

| Method | Endpoint                     | Description      |
| ------ | ---------------------------- | ---------------- |
| POST   | `/api/users`                 | Create user      |
| GET    | `/api/users/{user_id}`       | Get user         |
| GET    | `/api/users/{user_id}/posts` | Get user’s posts |
| PATCH  | `/api/users/{user_id}`       | Update user      |
| DELETE | `/api/users/{user_id}`       | Delete user      |

### Posts

| Method | Endpoint               | Description     |
| ------ | ---------------------- | --------------- |
| GET    | `/api/posts`           | Get all posts   |
| POST   | `/api/posts`           | Create post     |
| GET    | `/api/posts/{post_id}` | Get single post |
| PUT    | `/api/posts/{post_id}` | Replace post    |
| PATCH  | `/api/posts/{post_id}` | Update post     |
| DELETE | `/api/posts/{post_id}` | Delete post     |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy aiosqlite jinja2 pydantic
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

---

## API Documentation

After running the server, visit:

* Swagger UI:
  `http://127.0.0.1:8000/docs`

* ReDoc:
  `http://127.0.0.1:8000/redoc`

---

## Key Concepts Demonstrated

* Async database sessions
* Dependency injection in FastAPI
* ORM relationships with eager loading
* Router-based API structure
* Separation of models, schemas, and routes
* Proper HTTP status handling

---

## Future Improvements

* Authentication and authorization
* Deploying and hosting backend services on AWS
* More production-style architecture

