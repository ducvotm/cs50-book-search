import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, render_template, request, session
from functools import wraps

#Define google books api key
GOOGLE_BOOKS_API_KEY = "AIzaSyBhiLmrNzOyI1qLN31CINB3N-JRD6l6MQo"

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={"Accept": "*/*", "User-Agent": request.headers.get("User-Agent")},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        price = round(float(quotes[-1]["Adj Close"]), 2)
        return {"price": price, "symbol": symbol}
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None
    
def search(query, max_results = 10):
    """Look up books by query using Google Books API."""

    # Prepare API request
    params = {
        "q": query,
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": max_results  # This value can be customized as needed
    }

    # Query API
    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}")
        return None
    
def filter(genre=None, author=None, published_year=None, max_results=10):
    """Filter books by genre, author, and published year using Google Books API."""

    # Construct the query string based on the provided filters
    query_parts = []
    if genre:
        query_parts.append(f"subject:{genre}")
    if author:
        query_parts.append(f"inauthor:{author}")
    if published_year:
        query_parts.append(f"inpublisher:{published_year}")
    query = " ".join(query_parts).strip()

    # Prepare API request
    params = {
        "q": query,
        "printType": "books",
        "maxResults": max_results,
        "key": GOOGLE_BOOKS_API_KEY
    }

    # Query API
    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return extract_books(data)
    except (requests.RequestException, ValueError) as e:
        print(f"Error: {e}")
        return []

def extract_books(data):
    """Extract book information from API response."""
    if "items" not in data:
        return []

    return [
        {
            "title": item["volumeInfo"].get("title"),
            "authors": item["volumeInfo"].get("authors"),
            "publishedDate": item["volumeInfo"].get("publishedDate"),
            "description": item["volumeInfo"].get("description"),
            "categories": item["volumeInfo"].get("categories"),
            "thumbnail": item["volumeInfo"].get("imageLinks", {}).get("thumbnail")
        } for item in data["items"]
    ]

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

