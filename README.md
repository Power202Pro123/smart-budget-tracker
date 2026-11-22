# Smart Budget Tracker

#### Video Demo: https://youtu.be/H6zVsOrB0fo

#### Description:

Smart Budget Tracker is a personal finance management web application developed using Python, Flask, and SQLite. The purpose of this project is to help users manage their monthly finances and keep track of their savings goals.

I developed this application as my CS50x final project. I wanted to create something practical that could help users  manage their money more effectively.

The application provides an interactive dashboard alongside dedicated sections for managing expenses, setting  budgets, and creating savings goals.

### Features

**1. User Authentication**

- Users can create accounts and log in using a username and password.
- Passwords are securely hashed using Werkzeug's password hashing functions.
- User sessions are managed using Flask-Session.
- Protected routes prevent unauthenticated users from accessing private pages. (preventing browsers from caching pages, especially private user data. Dedicated ruotes. Prioritizing enforcing profile completion first. Storing session data on the server rather client side.)
- New users, after registering, must complete their profile setup before accessing the dashboard.

**2. Profile Setup**

After registration, its compulsory for users to provide their city, country, preferred currency, and initial monthly budget. Users can not move to any other ruote before successfully completing profile setup. This information is stored in the database (table is Users and User_info) and associated with their account.

**3. Dashboard**

The dashboard provides an overview of the user's monthly finances, displaying:

- Total monthly budget.
- Total expenses.
- Remaining balance.
- Percentage of budget used.
- List of budget information.
- List of Recent expenses.

Users can also update their total monthly budget, top right button *Update Monthly Budget* directly from the dashboard.

**4. Budget Management**

Users can create individual budgets for different spending categories, such as Food, Transport, Shopping, Bills, Entertainment, Housing, Education, Health, and Other.

The application calculates spending against each category's allocated budget and displays progress percentages. It also prevents users from allocating more than their total monthly budget.

Monthly budgets are automatically created for new months using the previous month's total budget as the starting amount. User can see the budgets they allocated allocated for any month of the year.

chart.js was used for circular chart showing how spending or budget allocations are distributed across categories.

The app uses Flask's flash() messages to show styled, one-time alert banners for errors, warnings, and user feedback across redirects. Each message category automatically applies a matching CSS style so users can easily tell errors apart from warnings or successfull implementations. (I used Flask’s flash() across every possible routes to give immediate feedback on user actions and errors)

The application calculates remaining budget, total budget, total spending and number of active categories in budgets for the month.

Uses vanilla JavaScript to toggle a clean pop-up modal for adding new budget without leaving the current page.

**5. Expense Tracking**

Users can record expenses by providing an amount, category, description, date, and payment method (Cash, Card / Debit, Bank Transfer, Digital Wallet)

They can also delete existing expenses and view transactions for different months.

The application calculates total spending, average daily spending, the highest spending category, and the number of transactions.

Uses vanilla JavaScript to toggle a clean pop-up modal for adding new expenses without leaving the current page.

**6. Savings Goals**

Users can create personal savings goals by specifying a name, description, and target amount.

They can view their goals, delete them, and mark them as completed (Flask's flash() used to give feedback on the deletion or completion of the goal). Before allowing a goal to be completed, the application checks whether sufficient funds remain in the user's monthly budget. Once completed, the goal is recorded as an expense for the month.

**7. Settings**

Users can access their account settings and change their username or password after verifying their current password.

Logout button to erase the session cookies of the user.

**8. Layout**

`layout.html`: Acts as the base template for the application. It defines the overall page structure (the sidebar navigation, logo, and main content area). It uses Jinja template inheritance through `{% block main %}` so other pages can extend the layout without repeating the same HTML structure. It also imports the shared stylesheet and Font Awesome icons, and dynamically highlights the active navigation link based on the current route.

### Technologies Used

- **Python:** Main programming language for application logic and backend functionality.
- **Flask:** Web framework used to handle routes, requests, sessions, and page rendering.
- **SQLite:** Relational database used to store user accounts, budgets, expenses, profile information, and savings goals.
- **CS50 SQL:** Used to execute database queries.
- **HTML:** Used to structure the application's web pages.
- **CSS:** Used to style the interface and create a consistent design across different pages.
- **JavaScript:** Used for client-side interactions.
- **Jinja:** Used for rendering dynamic HTML templates.
- **Werkzeug:** Used for secure password hashing and password verification.
- **Icons**: Font Awesome used for assigning symbols.
- **Charts**: Chart.js

### Project Structure

- `app.py`: Main Flask application containing the routes, authentication logic, database queries, budget calculations, expense management, savings goal functionality, and settings functionality.
- `budget.db`: SQLite database containing the application's data.
- `requirements.txt`: Lists the Python packages required to run the application.
- `static/`: Contains static assets, including the application logo and CSS stylesheets.
- `templates/`: Contains the HTML templates used to render the application's pages.

The CSS files are organized according to their respective pages:

- `style.css`: Styling for Registration and Login pages only.
- `style1.css`: Styling for layout and navigation only.
- `style2.css`: Styling for profile page only.
- `style3.css`: Styling for goals page only.
- `style4.css`: Styling for budget and Expense pages only.
- `style5.css`: Styling for settings page only.
- `style6.css`: Styling for dashboard only.

### Database Design

The application uses six SQLite tables:

- `Users`: Stores account details, including names, usernames, hashed passwords, and profile completion status.
- `User_info`: Stores additional profile information, including currency, city, and country.
- `Monthly_Budgets`: Stores each user's total monthly budget.
- `Budgets`: Stores individual category-based budgets.
- `Expenses`: Stores expense transactions and their associated information.
- `goals`: Stores savings goals, target amounts, descriptions, and completion status.

The tables are connected through foreign keys referencing the Users table. This associates each user's financial records with their account.

### Design Decisions

I chose Flask because it provides a straightforward way to build a web application using Python while allowing flexibility in handling backend functionality.

SQLite was selected because it is lightweight and suitable for an application that requires structured data storage without a ***separate database server***.

I separated the HTML templates and CSS stylesheets to keep the frontend organized and make individual pages easier to maintain.

I also implemented a custom `login_required` decorator to protect application routes and ensure users complete their profile setup before accessing the main application.

Another design decision was to use parameterized SQL queries (like ?) through CS50 SQL to interact with the database.

### Installation and Usage

1. Clone or download the project.
2. Open the project directory in a terminal.
3. Install the required dependencies:

   `pip install -r requirements.txt`

4. Run the Flask application:

   `flask --app app run`

5. Open the local address provided by Flask in your browser.
6. Register an account, complete your profile setup, and start managing your finances.

### Future Improvements

Possible future improvements include AI-powered financial insights (connecting an LLM such as gemini api to the web application), data export functionality and better data spending
reports.

---

**Built with ❤️ — Thank you, CS50x!**
