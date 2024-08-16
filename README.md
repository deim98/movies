# Movies App
A FastAPI-based application for managing and interacting with movies, including features like adding movies, rating them, and leaving comments.

# Table of Contents
1. Description
2. Features
3. Installation
4. Usage
5. API Endpoints
6. Testing
7. Logging
8. License
9. Contact

# Description
The Movies App is a RESTful API built with FastAPI that allows users to manage a collection of movies. Users can add movies, rate them, and leave comments. The app uses a SQLite database for data persistence and includes authentication features.

# Features
1. User Authentication:
     User registration
     User login
     JWT token generation
2. Movie Listing:
     View a movie added (public access)
     Add a movie (authenticated access)
     View all movies (public access)
     Edit a movie (only by the user who listed it)
     Delete a movie (only by the user who listed it)
3. Movie Rating:
     Rate a movie (authenticated access)
     Get ratings for a movie (public access)
4. Comments:
    Add a comment to a movie (authenticated access)
    View comments for a movie (public access)
    Add comment to a comment i.e nested comments (authenticated access)

# Installation
Prerequisites
Python 3.8 or higher
Git (for cloning the repository)
Virtualenv (optional but recommended)

# STEPS
1. Clone the repository
- git clone [https://github.com/yourusername/movies-app.git]
- cd movies-app

2. Create and activate a virtual environment (optional but recommended):
- python -m venv venv
- source venv/bin/activate  # On Windows: venv\Scripts\activate

- Environment Variables

- `SECRET_KEY`: App's secret key.
- `ALGORITHM`: App's algorithm.
- `DB_URL`: Database url
- `ACCESS_TOKEN_EXPIRE_MINUTES`=integer

Create a `.env` file in the root directory and add your environment variables:

```env
SECRET_KEY=secret_key
ALGORITHM=algorithm
DB_URL=db_url
ACCESS_TOKEN_EXPIRE_MINUTES=int

3. Install the required dependencies:
- pip install -r requirements.txt

4. Set up the database:
- The app uses SQLite by default. The database will be automatically created when you run the app. Moreover you can set up the database by running migrations
- alembic upgrade head


5. Start the FastAPI server:
uvicorn app.main:app --reload
The app will be available at http://127.0.0.1:8000. 

6. Swagger UI will be available at http://127.0.0.1:8000/docs,

## API Endpoints
- Authentication
   POST /signup: Register a new user.
   POST /login: Login to get a JWT token.
- Movies
   GET /movies/: Get a list of all movies.
   POST /movies/: Add a new movie (requires JWT).
   GET /movies/{movie_id}/: Get details of a specific movie.
   PUT /movies/{movie_id}/: Update a movie (requires JWT, only by the owner).
   DELETE /movies/{movie_id}/: Delete a movie (requires JWT, only by the owner).
- Ratings
   POST /movies/{movie_id}/ratings: Rate a movie (requires JWT).
   GET /movies/{movie_id}/ratings: Get all ratings for a specific movie.
- Comments
   POST /movies/{movie_id}/comments: Add a comment to a movie (requires JWT).
   GET /movies/{movie_id}/comments: View all comments for a movie.
   POST /comments/{comment_id}/replies: Add a reply to a comment (requires JWT).
- Testing
   To run the tests for the application:
   pytest

## LICENSE
This project is licensed under the MIT License.



