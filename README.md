# Async FastAPI-based application

- Python
- FastAPI framework
- MongoDB support (motor asyncio)
- Docker deploy

## Installation

duplicate enviroment file 'env.example' and rename to '.env'
run 'docker-compose up -d --build'


## Routes

'/docs' - API documentation
GET '/extension/{id}' - get extension like zip archive (common HTTP response, file's meta info include in headers)
GET '/user/{id}/extensions' - get all user's extensions meta info
DELETE '/user/{user_id}/delete_extension/{extension_id}' - remove extension from DB and directory
POST '/user/{user_id}/new_extension' - get file in request and create new Extension object


## Application struct

- ./backend contains FastAPI application
-   - ./backend/app contains the logic of the application
-   -   - ./backend/app/models - Models
-   -   - ./backend/app/services - Controllers
-   -   - ./backend/app/core - Routes logic
-   -   - ./backend/app/utils - Supporting tools (like connect to db...)
- ./db_vol contains DataBase files

