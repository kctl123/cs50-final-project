from flask import Flask,render_template,request,redirect,session
import sqlite3, os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True


DB_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.db") 

#using os.path.join ensures it works across computers like Mac and Windows
#using os.path.dirname(__file__) gets the directory of current file app.py 
#then we append "data" and "restaurants.db" to that path
#end result is that DB_PATH points to C:\Users\Keefe\Downloads\cs50-final-project\data\restaurants.db

conn = sqlite3.connect(DB_PATH) 
#creates connection to restaurant.database -- if restaurants.db does not exist, it will be created

db = conn.cursor()
#creates a cursor object to interact with the database such that i can do db.execute("SQL QUERY")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)