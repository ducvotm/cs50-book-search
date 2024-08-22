import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, search, filter

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
user_db = SQL("sqlite:///user.db")
book_db = SQL("sqlite:///book.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
        # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Ensure comfirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 403)
        
        # Ensure password and confirmation is same
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("the confirmation is not match", 403)

        # Query database for username
        rows = user_db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is not exists
        if len(rows) >= 1:
            return apology("username already exists", 403)
        
        #Insert the new user into users
        user_db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
        
        # Query database for username login
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")) ????????

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html") 


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = user_db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search_books():
    if request.method == "POST":
        data = request.form
        print(f"Received data: {data}")
        query = data.get("q")

        if query:
            search_results = search(query)

            if search_results is not None:
                print(f"Search results: {search_results}")
                return render_template("search_results.html", search_results=search_results)
            
            return jsonify({"error": "Error fetching search results"}), 500
        
        return jsonify({"error": "No query provided"}), 400
    
    return render_template("search.html")

@app.route("/filter", methods=["GET", "POST"])
def filter_books():
    if request.method == "POST":
        data = request.form
        print(f"Received data: {data}")
        
        # Extract filter criteria from the form data
        title = data.get("title")
        author = data.get("author")
        genre = data.get("genre")
        year = data.get("year")
        
        # Perform the filtering using the `filter` function
        books = filter(genre=genre, author=author, published_year=year)
        
        # Render the HTML template with the filtered results
        if books:
            print(f"Filtered books: {books}")
            return render_template("filter_results.html", books=books)
        return jsonify({"error": "No books found matching the criteria"}), 404
    
    # For GET request, just render the filter form
    return render_template("filter.html")

@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    
    if not user_id:
        return redirect("/login")   

    
    # Handle GET request logic here
    user = user_db.execute("SELECT username FROM users WHERE id = ?", user_id)
    posts = user_db.execute("SELECT content FROM posts WHERE user_id = ?", user_id)
    comments = user_db.execute("SELECT content FROM comments WHERE user_id = ?", user_id)
    
    return render_template("profile.html", user=user, posts=posts, comments=comments)

@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    if request.method == "POST":
        data = request.form
        book_id = data.get("book_id")
        rating = data.get("rating")
        review = data.get("review")
        
        # Validate the input
        if not book_id or not rating or not review:
            return jsonify({"error": "All fields are required"}), 400
        
        # Insert the review into the database
        user_db.execute("INSERT INTO reviews (user_id, book_id, rating, review) VALUES (?, ?, ?, ?)",
                        session["user_id"], book_id, rating, review)
        user_db.commit()
        
        return redirect("search.html")
    
    return render_template("review.html")
