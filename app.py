from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os, secrets
from functools import wraps
from datetime import datetime

# configure application
app = Flask(__name__)

# Secret key for flash / gen random 24-byte secret key
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(24))

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"   #store session data  on the server rather client side
Session(app)

# Get to use database
db = SQL("sqlite:///budget.db")

# Prevent browsers from caching pages, especially private user data
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Prevent caching of the pages so history not shown
    response.headers["Expires"] = 0                       # Further prevention of caching of older browsers/proxies
    response.headers["Pragma"] = "no-cache"
    return response


#HELPER DECORATOR  #I used decorator function to ensure user has completed profile setup before moving onto any other route of my web application. (A concept I had to learn through yt video)"A decorator is just a function that takes another function as an argument, adds some kind of functionality, and then returns another function."this will ensure I only move to different ruote if I have completed my profile setup

def login_required(f):   # Redirect login if user not logged in.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in first!", "error")
            return redirect("/login")

        #Ensure profile setup is done
        if request.endpoint != "profile":   #if /profile is not typed
            user = db.execute("SELECT profile_complete FROM Users WHERE id = ?", session["user_id"])
            if user and user[0]["profile_complete"] == 0:
                flash("Please complete your profile setup first!", "warning")
                return redirect("/profile")
        return f(*args, **kwargs)
    return decorated_function







#ROUTES
#Log user in
@app.route("/login", methods=["GET", "POST"])
def login():
    # clears session["user_id"] / logout
    session.clear()
    if request.method == "POST":
            username = request.form.get("User")
            password = request.form.get("Password")

            # Ensure username was submitted
            if not username:
                flash("Must provide username!", "error")                    #flash(message, category)
                return render_template("Login.html")

            # Ensure password was submitted
            if not password:
                flash("Must provide password!", "error")
                return render_template("Login.html")

            # Query database for username
            rows = db.execute("SELECT * FROM Users WHERE username = ?", username)  #returns list of dictionaries

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
                flash("Invalid username or password!", "error")
                return render_template("Login.html")

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")


    else:
        return render_template("Login.html")

#Register a user
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("User")
        password = request.form.get("Password")
        confirmpass = request.form.get("Confirm-Password")
        name = request.form.get("Name")

        # Ensure username was submitted
        if not username:
            flash("Must provide username!", "error")
            return render_template("Register.html")

        # Ensure password was submitted
        if not password:
            flash("Must provide password!", "error")
            return render_template("Register.html")

        # Ensure second password was submitted
        if not confirmpass:
            flash("Must provide confirmation password!", "error")
            return render_template("Register.html")

        # Ensure name was provided
        if not name:
            flash("Must provide your name!", "error")
            return render_template("Register.html")

        #Ensure passwords match
        if password != confirmpass:
            flash("Must provide passwords that match!", "error")
            return render_template("Register.html")

        #Ensure user is not taken
        rows = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(rows) > 0:
            flash("Username already exists!", "error")
            return render_template("Register.html")
        else:
            db.execute("INSERT INTO Users (name, username, password) VALUES(?, ?, ?)", name, username, generate_password_hash(password))

            # Remember which user has logged in
            user_id = db.execute("SELECT * FROM Users WHERE username = ?", username)
            session["user_id"] = user_id[0]["id"]

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("Register.html")


#Profile setup
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        city = request.form.get("city")
        country = request.form.get("country")
        currency = request.form.get("currency")
        Tbudget =  request.form.get("budget")

        #Ensure all data given
        if not city:
            flash("Must provide city!", "error")
            return render_template("profile.html")

        if not country:
            flash("Must provide country!", "error")
            return render_template("profile.html")

        if not currency:
            flash("Must provide currency!", "error")
            return render_template("profile.html")

        if not Tbudget:
            flash("Must provide Total Monthly budget!", "error")
            return render_template("profile.html")

        #Ensure budget is positive
        Tbudget = float(Tbudget)
        if Tbudget < 1:
            flash("Incorrect budget value!", "error")
            return render_template("profile.html")

        # profile status complete
        db.execute("UPDATE Users SET profile_complete = 1 WHERE id = ?",session["user_id"])

        #Add data to db
        db.execute("INSERT INTO User_info (user_id, city, country, currency) VALUES(?, ?, ?, ?)", session["user_id"], city, country, currency)

        #Add data to table of Monthly_Budgets
        db.execute("INSERT INTO Monthly_Budgets (user_id, date, total_budget) VALUES(?, ?, ?)", session["user_id"], datetime.now().strftime("%Y-%m"), Tbudget)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("profile.html")



#Budget
@app.route("/budget", methods=["GET"])
@login_required
def budget():
        #AUTO-updater of Monthly_Budgets table
        currentmonth = datetime.now().strftime("%Y-%m") #2026-09
        rows = db.execute("SELECT * FROM Monthly_Budgets WHERE user_id = ?", session["user_id"])
        if currentmonth not in [row["date"] for row in rows]:

            #latest month's budget
            latestentry = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? ORDER BY date DESC LIMIT 1", session["user_id"])
            #insert the previous month's budget for new months
            db.execute("INSERT INTO Monthly_Budgets (user_id, date, total_budget) VALUES (?, ?, ?)", session["user_id"], currentmonth, latestentry[0]["total_budget"])

        #TOTAL BUDGET IS ALWAYS PRESENT BCZ PROFILE SETUP IS NECESSARY

        #Get date for budget display
        select_month = request.args.get("month")

        if select_month and len(select_month) >= 7:
            #extract only left 7
            targetmonth = select_month[:7]
        else:
            targetmonth = currentmonth

        #Total budget for the month
        Total_budget_row = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? AND date = ?", session["user_id"], targetmonth)
        if not Total_budget_row:
            Total_budget = 0.01
        else:
            Total_budget = Total_budget_row[0]["total_budget"]


        #calcu total spend
        spent = db.execute("SELECT SUM(spent) AS total FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?", session["user_id"], targetmonth)
        if spent[0]["total"]:
            Total_spent = spent[0]["total"]
        else:
            Total_spent = 0

        #remaining money left
        Remaining = Total_budget - Total_spent

        #number of categories of the month   #DISTINCT counting only unique categories
        Num_category = db.execute("SELECT COUNT(DISTINCT category) AS cats FROM Budgets WHERE user_id = ? AND date = ?", session["user_id"], targetmonth)[0]["cats"]


        #table calculation. COALESCE if there is no sum of spent then 0 is returned
        items = db.execute("SELECT b.id, b.category, b.amount, COALESCE(SUM(e.spent), 0) AS spent FROM Budgets b LEFT JOIN Expenses e ON b.user_id = e.user_id AND b.category = e.category AND substr(e.date, 1, 7) = b.date WHERE b.user_id = ? AND b.date = ? GROUP BY b.category, b.amount", session["user_id"], targetmonth)

        #Chart calculation
        categories = [
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Housing",
            "Education",
            "Health",
            "Other",
        ]

        Category_amount = [0.0] * 9

        rows = db.execute("SELECT category, SUM(amount) AS total FROM Budgets WHERE user_id = ? AND date = ? GROUP BY category",session["user_id"],targetmonth)

        for row in rows:
            if row["category"] in categories:
                index = categories.index(row["category"])
                Category_amount[index] = float(row["total"] or 0.0)

        budget_usage = int((Total_spent/Total_budget)*100)


        for item in items:
            item["percent"] = (min(round((item["spent"] / item["amount"]) * 100), 100) if item["amount"] > 0 else 0)

        return render_template("budget.html", items=items, budget_usage=budget_usage, Remaining=Remaining, Num_category=Num_category, Total_budget=Total_budget, Total_spent=Total_spent, Category_amount=Category_amount ,selected_month=targetmonth)

#Deletion in Budget Table
@app.route("/delete-budget", methods=["POST"])
@login_required
def delete_budget():
    budget_id = request.form.get("budget_id")

    if budget_id:
        db.execute("DELETE FROM Budgets WHERE id = ? AND user_id = ?", budget_id, session["user_id"])
    return redirect("/budget")


# + new Budget
@app.route("/create-budget", methods=["GET", "POST"])
@login_required
def create_budget():
    category = request.form.get("category")
    amount = float(request.form.get("amount"))
    month = request.form.get("month")        # extracts string like '2026-09'

    #Ensure user input provided
    if not category:
        flash("Please select a category.", "danger")
        return redirect("/budget")

    if not amount or amount <= 0:
        flash("Please enter a valid budget amount.", "danger")
        return redirect("/budget")

    if not month:
        flash("Please select a valid month.", "danger")
        return redirect("/budget")

    #Exceding Budget
    #Total budget for the month
    Total_budget_row = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? AND date = ?", session["user_id"], month)
    if not Total_budget_row:
        Total_budget = 0
    else:
        Total_budget = float(Total_budget_row[0]["total_budget"])

    #already_allocated. COALESCE if there is no sum of spent then 0 is returned
    rows = db.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM Budgets WHERE user_id = ? AND date = ?",session["user_id"],month)
    already_allocated = float(rows[0]["total"])

    if (amount + already_allocated) > Total_budget:
        flash("Going over Total Budget", "danger")
        return redirect("/budget")

    # 3. Insert or update record in database
    db.execute("INSERT INTO Budgets (user_id, category, amount, date) VALUES (?, ?, ?, ?)", session["user_id"], category, amount, month)

    # 4. Redirect user back to the main budget page
    return redirect("/budget")

# + new Expense
@app.route("/create-expense", methods=["POST"])
@login_required
def create_expense():
    category = request.form.get("category")
    spent = request.form.get("amount")
    description = request.form.get("description")
    payment_method = request.form.get("payment_method")
    date = request.form.get("date")        # YYYY-MM-DD


    #Ensure user input provided
    if not category:
        flash("Please select a category.", "danger")
        return redirect("/expenses")

    if not spent or float(spent) <= 0:
        flash("Please enter a valid amount spent.", "danger")
        return redirect("/expenses")

    if not payment_method:
        flash("Please select a payment method.", "danger")
        return redirect("/expenses")

    if not date:
        flash("Please select a valid date.", "danger")
        return redirect("/expenses")





    # 3. Insert or update record in database
    db.execute("INSERT INTO Expenses (user_id, category, date, description, spent, payment_method) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], category, date, description, spent, payment_method)

    # redirect user back to the main budget page
    return redirect("/expenses")

#Deletion in Expense Table
@app.route("/delete-expense", methods=["POST"])
@login_required
def delete_expense():
    expense_id = request.form.get("expense_id")

    if expense_id:
        db.execute("DELETE FROM Expenses WHERE id = ? AND user_id = ?", expense_id, session["user_id"])
    return redirect("/expenses")

#Expenses
@app.route("/expenses", methods=["GET"])
@login_required
def expense():
    currentmonth = datetime.now().strftime("%Y-%m") #2026-09

    #Get date for expenses display
    select_month = request.args.get("month")

    if select_month and len(select_month) >= 7:
        #extract only left 7. YYY-MM
        targetmonth = select_month[:7]
    else:
        targetmonth = currentmonth

    #Error for spending more than total budget
        #already total spent
        spended = db.execute("SELECT SUM(spent) AS total FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?", session["user_id"], targetmonth)
        if spended[0]["total"]:
            Total_spent = spended[0]["total"]
        else:
            Total_spent = 0

        #calcu total budget

        Total_budget_row = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? AND date = ?", session["user_id"], targetmonth)
        Total_budget = float(Total_budget_row[0]["total_budget"]) if Total_budget_row else 0.0
        if float(Total_spent) > Total_budget:
            flash("Budget limit reached. Please reduce the amount or increase your total budget", "danger")


    #data for table
    items = db.execute("SELECT * FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ? ORDER BY date DESC", session["user_id"], targetmonth)

    #total expenses
    TExpenses = 0
    for item in items:
        TExpenses = TExpenses + item["spent"]

    #daily average
    #MAX(date) returns single row else returns NULL if no existing
    latestentry = db.execute("SELECT MAX(date) AS latestdate FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?",session["user_id"],targetmonth)
    if latestentry and latestentry[0]["latestdate"]:   #making sure NULL not returned
        date = latestentry[0]["latestdate"]
        day = int(date[8:10])
        if day != 0:
            average = round(TExpenses / day, 2)
        else:
            average = 0
    else:
        average = 0

    #highest categories. Calculates total of a category in expenses for a month to get the highest category that money was spent on.
    Hcategory = db.execute("SELECT category, SUM(spent) AS spent FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ? GROUP BY category ORDER BY spent DESC LIMIT 1",session["user_id"],targetmonth)
    if Hcategory:                      #check list isn't empty
        Hcategory = Hcategory[0]["category"]
    else:
        Hcategory = "N/A"

    #total transactions this month
    Ttransactions = db.execute("SELECT COUNT(category) AS Num_Category FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?",session["user_id"],targetmonth)
    if Ttransactions:
        Ttransactions = Ttransactions[0]["Num_Category"]
    else:
        Ttransactions = 0

    return render_template("expense.html", items=items, TExpenses=TExpenses, Ttransactions=Ttransactions, Hcategory=Hcategory, average=average, selected_month=targetmonth)



#Logout
@app.route("/logout", methods=["GET", "POST"])
@login_required
def Logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#Settings
@app.route("/settings", methods=["GET"])
@login_required
def Settings():
    return render_template("settings.html")

#Change User
@app.route("/change-user", methods=["POST"])
@login_required
def Changeuser():
    New_User = request.form.get("New_User")
    Password_U = request.form.get("Password_U")

    if not New_User:
         flash("Please enter your new username.", "danger")
         return redirect("/settings")

    if not Password_U:
        flash("Please enter your password.", "danger")
        return redirect("/settings")

    #Check if current password is correct
    stored_hash = db.execute("SELECT password FROM Users WHERE id = ?", session["user_id"])[0]["password"] #hashed pass
    if not check_password_hash(stored_hash, Password_U):
        flash("Incorrect Password Entered.", "danger")
        return redirect("/settings")



    #Ensure user is not taken
    rows = db.execute("SELECT username FROM users WHERE username = ?", New_User)
    if len(rows) > 0:
        flash("Username already taken.", "danger")
        return redirect("/settings")

    else:
        db.execute("UPDATE Users SET username = ? WHERE id = ?", New_User, session["user_id"])
        flash("Username updated successfully!", "success")
        return redirect("/settings")




#Change Password
@app.route("/change-password", methods=["POST"])
@login_required
def Changepassword():
    Password_P = request.form.get("Password_P")
    New_Password = request.form.get("New_Password")
    C_New_Password = request.form.get("C_New_Password")

    if not Password_P:
         flash("Please enter your current password.", "danger")
         return redirect("/settings")

    if not New_Password:
        flash("Please enter the new password.", "danger")
        return redirect("/settings")

    if not C_New_Password:
        flash("Please confirm your new password", "danger")
        return redirect("/settings")

    #check password matches
    if New_Password != C_New_Password:
        flash("Passwords do not match.", "danger")
        return redirect("/settings")


    #Check if current password is correct
    stored_hash = db.execute("SELECT password FROM Users WHERE id = ?", session["user_id"])[0]["password"] #hashed pass
    if not check_password_hash(stored_hash, Password_P):
        flash("Incorrect Password Entered.", "danger")
        return redirect("/settings")

    else:
        db.execute("UPDATE Users SET password = ? WHERE id = ?", generate_password_hash(New_Password), session["user_id"])
        flash("Password changed successfully!", "success")
        return redirect("/settings")

#Goals setup
@app.route("/goals", methods=["GET"])
@login_required
def Dashboard():
    #Total goals
    T_goals = db.execute("SELECT COUNT(*) AS total FROM goals WHERE user_id = ?", session["user_id"])[0]["total"]

    #Count completed
    Compeleted = db.execute("SELECT COUNT(*) AS total FROM goals WHERE user_id = ? AND completed_goal = ?", session["user_id"], 1)[0]["total"]

    #Count Total Target
    Target = db.execute("SELECT COALESCE(SUM(target), 0) AS total FROM goals WHERE user_id = ? AND completed_goal = ?", session["user_id"], 0)[0]["total"]

    #Count total saved
    total_saved = db.execute("SELECT COALESCE(SUM(target), 0) AS total FROM goals WHERE user_id = ? AND completed_goal = 1",session["user_id"])[0]["total"]

    #database data retrevial
    goals = db.execute("SELECT * FROM goals WHERE user_id = ?", session["user_id"])

    return render_template("goal.html", T_goals=T_goals, Compeleted=Compeleted, Target=Target, total_saved=total_saved, goals=goals)

# +new goals
@app.route("/create-goal", methods=["POST"])
@login_required
def create_goals():
    name = request.form.get("name")
    description = request.form.get("description")
    target = float(request.form.get("target"))

    #Ensure user input provided
    if not name:
        flash("Please enter a name.", "danger")
        return redirect("/goals")

    if not target or target <= 0:
        flash("Please enter a valid goal's target amount.", "danger")
        return redirect("/goals")

    #add to table
    db.execute("INSERT INTO goals (user_id, name, target, description) VALUES (?, ?, ?, ?)", session["user_id"], name, target, description)

    # 4. Redirect user back to the main budget page
    return redirect("/goals")

#Deletion in Goals Table
@app.route("/delete-goal", methods=["POST"])
@login_required
def delete_goal():
    goal_id = request.form.get("goal_id")

    if goal_id:
        db.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", goal_id, session["user_id"])
        flash("Deleted goal successfully.", "success")
    return redirect("/goals")

#Completion in Goals Table
@app.route("/complete-goal", methods=["POST"])
@login_required
def complete_goal():
    goal_id = request.form.get("goal_id")

    if goal_id:
        #remaining money left

        #Total budget for the month
        targetmonth = datetime.now().strftime("%Y-%m")
        Total_budget_row = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? AND date = ?", session["user_id"], targetmonth)
        if not Total_budget_row:
            Total_budget = 0.01
        else:
            Total_budget = float(Total_budget_row[0]["total_budget"])


        #calcu total spend
        spent = db.execute("SELECT SUM(spent) AS total FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?", session["user_id"], targetmonth)
        if spent[0]["total"]:
            Total_spent = float(spent[0]["total"])
        else:
            Total_spent = 0

        Remaining = Total_budget - Total_spent

        #check if goal can be completed
        goal = db.execute("SELECT * FROM goals WHERE id = ? AND user_id = ?", goal_id,session["user_id"])
        targetam = goal[0]["target"]
        if targetam > Remaining:
            flash("You don't have enough remaining funds to complete this goal yet. Wait until you save more, or increase your total budget on the dashboard. ", "danger")
            return redirect("/goals")
        else:
            db.execute("UPDATE goals SET completed_goal = 1 WHERE id = ? AND user_id = ?",goal_id,session["user_id"])
            flash("Completed goal successfully.", "success")


            # 2. Insert into expenses table
            if goal[0]["description"]:
                expense_description = f"Goal: {goal[0]['name']} - {goal[0]['description']}"
            else:
                expense_description = f"Goal: {goal[0]['name']}"



            current_date = datetime.now().strftime("%Y-%m-%d")
            db.execute("INSERT INTO expenses (user_id, date, category, description, spent, payment_method) VALUES (?, ?, ?, ?, ?, ?)",session["user_id"],current_date,"Goal completion",expense_description,targetam,"NA")


    return redirect("/goals")

#Dashboard
@app.route("/")
@login_required
def dashboard():
    currentmonth = datetime.now().strftime("%Y-%m")

    #Total_budget
    Total_budget_row = db.execute("SELECT total_budget FROM Monthly_Budgets WHERE user_id = ? AND date = ?", session["user_id"], currentmonth)
    if not Total_budget_row:
        Total_budget = 0.01
    else:
        Total_budget = Total_budget_row[0]["total_budget"]


    #Total_Spent
    spent = db.execute("SELECT SUM(spent) AS total FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ?", session["user_id"], currentmonth)
    if spent[0]["total"]:
        Total_spent = spent[0]["total"]
    else:
        Total_spent = 0

    #Remaining
    Remaining = Total_budget - Total_spent

    #percentage_budget_left
    budget_usage = int((Total_spent/Total_budget)*100)

    #budgets YYYY-MM
    budgets = db.execute("SELECT * FROM Budgets WHERE user_id = ? AND date = ?", session["user_id"], currentmonth)

    #expenses"
    expenses = db.execute("SELECT * FROM Expenses WHERE user_id = ? AND substr(date, 1, 7) = ? ORDER BY date DESC", session["user_id"], currentmonth)

    return render_template("dashboard.html", Total_spent=Total_spent, Remaining=Remaining, Total_budget=Total_budget, budgets=budgets, budget_usage=budget_usage, expenses=expenses)


#update_total_budget
@app.route("/update-budget", methods=["POST"])
@login_required
def update_budget():
    amount = request.form.get("amount")

    if not amount or float(amount) <= 0:
        flash("Please enter a valid total budget amount.", "danger")
        return redirect("/")

    currentmonth = datetime.now().strftime("%Y-%m")
    # 3. Insert or update record in database
    db.execute("UPDATE Monthly_Budgets SET total_budget = ? WHERE date = ? AND user_id = ?", float(amount), currentmonth, session["user_id"])
    flash("Successfully updated total monthly budget.", "success")
    # redirect user back dashboard
    return redirect("/")
