from flask import Flask,render_template,request,redirect,session,flash
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "password123"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


db_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(db_dir, exist_ok=True)

DB_PATH = os.path.join(db_dir, "restaurants.db")

#using os.path.join ensures it works across computers like Mac and Windows
#using os.path.dirname(__file__) gets the directory of current file app.py 
#then we append "data" to that path
#end result is that DB_PATH points to C:\Users\Keefe\Downloads\cs50-final-project\data\restaurants.

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#creates connection to restaurant.database -- if restaurants.db does not exist, it will be created

db = conn.cursor()
#creates a cursor object to interact with the database such that i can do db.execute("SQL QUERY")

db.row_factory = sqlite3.Row
#this allows us to access columns by name like user["username"] instead of user[0]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access the recommendation form.", "warning")
        return redirect("/login")
    
    if request.method == "POST":

        #Single-select fields
        region = request.form.get("region")
        budget = request.form.get("budget")
        occasion = request.form.get("occasion")

        #Multi-select fields
        cuisine = request.form.getlist("cuisine")
        dietary_restrictions = request.form.getlist("diet")
        vibe = request.form.getlist("vibe")

        #Convert lists to comma-separated strings for storage
        cuisine_str = ",".join(cuisine)
        dietary_restrictions_str = ",".join(dietary_restrictions)
        vibe_str = ",".join(vibe)

        #Server-side validation
        if not region:
            flash("Region is required.", "danger")
            return redirect("/dashboard")
        
        if not budget:
            flash("Budget is required.", "danger")
            return redirect("/dashboard")
        
        if not occasion:
            flash("Occasion is required.", "danger")
            return redirect("/dashboard")
        
        if not cuisine:
            flash("At least one cuisine must be selected.", "danger")
            return redirect("/dashboard")
        
        if not dietary_restrictions:
            flash("At least one dietary restriction must be selected.", "danger")
            return redirect("/dashboard")
        
        if not vibe:
            flash("At least one vibe must be selected.", "danger")
            return redirect("/dashboard")
    
        db.execute("INSERT INTO preferences (user_id, region, budget, occasion, cuisine, dietary_restrictions, vibe) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, region, budget, occasion, cuisine_str, dietary_restrictions_str, vibe_str))
        conn.commit()
    
    prefs = db.execute("SELECT * FROM preferences WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()

    return render_template("recommend.html", prefs=prefs)
    

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        security_question = request.form.get("security_question")
        security_answer = request.form.get("security_answer")

        if not username:
            flash("Username is required.", "danger")
            return redirect("/register")
        if not password:
            flash("Password is required.", "danger")
            return redirect("/register")
        if not security_question:
            flash("Security question is required.", "danger")
            return redirect("/register")
        if not security_answer:
            flash("Security answer is required.", "danger")
            return redirect("/register")
        
        hashed_password = generate_password_hash(password)

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        #user is a tuple like (john, hashed_password, question, answer) or None if no such user

        if user:
            flash("Username already taken. Please choose a different one.", "danger")
            return redirect("/register")
        
    
        db.execute("INSERT INTO users (username, password_hash, security_question, security_answer) VALUES (?, ?, ?, ?)", (username, hashed_password, security_question, security_answer))
        conn.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required.", "danger")
            return redirect("/login")
        if not password:
            flash("Password is required.", "danger")
            return redirect("/login")
        
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None:
            flash("Invalid username", "danger")
            return redirect("/login")
        
        if not check_password_hash(user["password_hash"], password):
            flash("Invalid password", "danger")
            return redirect("/login")
        
        
        session["username"] = username
        session["user_id"] = user["id"]
        flash("Login successful!", "success")
        return redirect("/dashboard")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/forgot", methods = ["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form.get("username")

        if not username:
            flash("Username is required.", "danger")
            return redirect("/forgot")
        
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            flash("Username not found.", "danger")
            return redirect("/forgot")
        
        return render_template("reset.html", username=username)
    
    return render_template("forgot.html")

@app.route("/reset", methods = ["GET", "POST"])
def reset():
    if request.method == "POST":
        user = request.form.get("username")
        security_question = request.form.get("security_question")
        security_answer = request.form.get("security_answer")
        new_password = request.form.get("new_password")

        if not security_question:
            flash("Security question is required.", "danger")
            return redirect("/reset")
        if not security_answer:
            flash("Security answer is required.", "danger")
            return redirect("/reset")
        if not new_password:
            flash("New password is required.", "danger")
            return redirect("/reset")
        
        user_record = db.execute("SELECT * FROM users WHERE username = ?",  (user,)).fetchone()
        if security_question != user_record["security_question"] or security_answer != user_record["security_answer"]:
            flash("Security question or answer is incorrect.", "danger")
            return redirect("/reset")
        
        hashed_new_password = generate_password_hash(new_password)
        db.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_new_password, user))
        conn.commit()
        flash("Password reset successful! Please log in with your new password.", "success")
        return redirect("/login")

    return render_template("reset.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)