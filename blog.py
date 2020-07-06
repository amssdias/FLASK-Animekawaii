from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "5eb7cd06d1d3562dcb0220e3feed70a7"

@app.route("/")
def main():
    return render_template("main.html")




# Register page
@app.route("/register", methods=["POST", "GET"])
def register():

    db = sqlite3.connect("blog.db")
    c = db.cursor()

    # If user submits
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # User must type inside all fields
        if not name or not email or not password or not confirmation:
            error = "Must fill all the fields"
            return render_template("register.html", error=error)

        # User must type same password
        if password != confirmation:
            error = "Passwords must be equal"
            return render_template("register.html", error=error)

        # Check if email already exists in the table
        rows = c.execute("SELECT * FROM users WHERE email=? ", (email,)).fetchall()
        if len(rows) >= 1:
            error = "Email already exist"
            return render_template("register.html", error=error)

        password = generate_password_hash(password)

        c.execute("INSERT INTO users(name, email, password) VALUES(?, ?, ?)", (name, email, password))
        db.commit()
        db.close()

        return redirect("/login")
    else:
        if "user_id" in session:
            return redirect("/user")

        title = "Blog - Register"
        return render_template("register.html", title=title)




# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    db = sqlite3.connect("blog.db")
    c = db.cursor()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        rows = c.execute("SELECT * FROM users WHERE email=? ", (email,)).fetchall()

        if len(rows) != 1:
            error = "No email found, register first"
            return render_template("login.html", error=error)

        if not check_password_hash(rows[0][3], password):
            error = "Password Incorrect"
            return render_template("login.html", error=error)

        session['user_id'] = rows[0][0]

        db.close()

        return redirect("/user")

    else:
        if "user_id" in session:
            return redirect("/user")
        else:
            title = "Blog - Login"
            return render_template("login.html", title=title)


# Logout
@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")



# User page
@app.route("/user")
def user():
    if 'user_id' in session:
        title = "Welcome"
        return render_template("user_main.html", title=title, user=True)
    else:
        return redirect("/login")




# User list
@app.route("/mylist", methods=["POST", "GET"])
def mylist():

    db = sqlite3.connect("blog.db")
    c = db.cursor()

    if request.method == "POST":

        # If user press button to watch
        if request.form.get('btn_seen') or request.form.get('btn_seen_delete'):

            seen = request.form.get("seen").upper()
            if not seen:
                return redirect("/mylist")

            rows = c.execute("SELECT anime_name FROM my_list WHERE user_id=? AND anime_name = ?", (session["user_id"], seen)).fetchall()
            
            # Add button
            # Check if the user already have same anime name
            if request.form.get('btn_seen'):
                if len(rows) > 0:
                    error = "Already have this anime in your list"
                    return render_template("user_list.html", error=error, user=True)
            
                # Insert into table
                c.execute("INSERT INTO my_list(user_id, anime_name, option) VALUES(?, ?, 'seen')", (session['user_id'], seen,))

            # Delete button
            # Check if the user have the name in the list
            elif request.form.get('btn_seen_delete'):
                if len(rows) == 0:
                    error = "Don't have this anime in your list"
                    return redirect("/mylist")

                # Delete from table
                c.execute("DELETE FROM my_list WHERE anime_name = ? AND option = 'seen' ", (seen,))

            db.commit()
            db.close()

            return redirect("/mylist")


        # If user press button to watch
        elif request.form.get('btn_watch') or request.form.get('btn_watch_delete'):

            watch = request.form.get("watch").upper()
            if not watch:
                return redirect("/mylist")
            
            rows = c.execute("SELECT anime_name FROM my_list WHERE user_id = ? AND anime_name = ?", (session["user_id"], watch)).fetchall()
           
            # Add button
            # Check if the user already have posted same anime
            if request.form.get('btn_watch'):
                if len(rows) > 0:
                    error = "Already have this anime added to your list"
                    return redirect("/mylist")

                # Insert into table 
                c.execute("INSERT INTO my_list(user_id, anime_name, option) VALUES(?, ?, 'watch')", (session['user_id'], watch,))

            # Delete button
            # Check if the user have posted that anime
            elif request.form.get('btn_watch_delete'):
                if len(rows) == 0:
                    error = "Don't have this anime in your list"
                    return redirect("/mylist")

                # Delete from table
                c.execute("DELETE FROM my_list WHERE anime_name = ? AND option = 'watch' ", (watch,))

            db.commit()
            db.close()
            return redirect("/mylist")


    else:
        if 'user_id' in session:
            title = "Post Now"
            list_seen = c.execute("SELECT anime_name FROM my_list WHERE user_id = ? AND option='seen' ORDER BY anime_name", (session["user_id"],)).fetchall()
            list_watch = c.execute("SELECT anime_name FROM my_list WHERE user_id = ? AND option='watch' ORDER BY anime_name", (session["user_id"],)).fetchall()
            db.close()

            return render_template("user_list.html", title=title, user=True, list_seen=list_seen, list_watch=list_watch)
        else:
            return redirect("/login")



# Anime list
@app.route("/anime_list")
def anime_list():

    db = sqlite3.connect("blog.db")
    c = db.cursor()

    if 'user_id' in session:

        anime_name = c.execute("SELECT * FROM anime_list ORDER BY anime_name")
        
        return render_template('anime_list.html', user=True, anime_name=anime_name)
    else:
        return redirect("/login")




# Popular series
@app.route("/popular")
def popular():
    if 'user_id' in session:
        
        return render_template('popular.html', user=True)
    else:
        return redirect("/login")

    