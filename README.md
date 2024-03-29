# FastAPI-based application

- Python
- FastAPI framework
- MongoDB support (motor asyncio)
- Docker deploy

## Installation

duplicate enviroment file 'env.example', write your own values and rename to '.env'<br>
run 'docker-compose up -d --build'


## Routes

':8081' - mongo-express <br>
'/docs' - API documentation <br>
GET '/extension/{id}' - get extension like zip archive (common HTTP response, file's meta info include in headers) <br>
GET '/user/{id}/extensions' - get all user's extensions meta info <br>
DELETE '/user/{user_id}/delete_extension/{extension_id}' - remove extension from DB and directory <br>
POST '/user/{user_id}/new_extension' - get file in request and create new Extension object <br>


## Application struct

- ./backend contains FastAPI application
-   - ./backend/app contains the logic of the application
-   -   - ./backend/app/models - Models
-   -   - ./backend/app/services - Controllers
-   -   - ./backend/app/core - Routes logic
-   -   - ./backend/app/source - storage of .zip archives
-   -   - ./backend/app/utils - Supporting tools (like connect to db...)
- ./db_vol contains DataBase files


## To do list
1. Add tests
2. Handle more exceptions
3. Upgrade models classes
