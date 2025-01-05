import requests
from flask import redirect, render_template, request, session
from functools import wraps

# Define google books api key
GOOGLE_BOOKS_API_KEY = "AIzaSyBhiLmrNzOyI1qLN31CINB3N-JRD6l6MQo"
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/meme-filter/blob/main/filter.py#L100
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask-login.readthedocs.io/en/latest/#how-to-use-it
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def search(query, max_results = 10):
    """Look up books by query using Google Books API."""
    params = {
        "q": query,
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": max_results
    }

    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}")
        return None

