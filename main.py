# Imports
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Text
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date

# Importing forms
from forms import ProjectForm, RegisterForm, LoginForm, ContactForm


# Basic Flask app setup
app = Flask(__name__)
# Make the secret key an environmental variable specific to the machine or environment the application runs on.
app.secret_key = "any-string-you-want-just-keep-it-secret"
Bootstrap5(app) # initialise bootstrap-flask
CKEditor(app) # Initialise the CKEditor

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

# Database Creation
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///projects-collection.db"
db = SQLAlchemy(model_class=Base) # Create the extension
db.init_app(app) # Initialise the app with the extension

# Database Table Creation
class Project(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    projectName: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    technologiesUsed: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficultyRating: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)

# Table in DB with the UserMixin
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

# Flask Routes

# Home page, Displays all projects
@app.route('/')
def home():
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Project).order_by(Project.projectName))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_projects = result.scalars().all()
    return render_template("index.html", all_posts=all_projects, current_user=current_user)

# Displays all the details related to a particular project
@app.route("/project/<int:index>")
def all_project_details(index):
    # Using Project ID to retrieve it from the DB
    requested_project = db.get_or_404(Project, index)
    return render_template("post.html", project=requested_project, current_user=current_user)

# Add a project, contains a form for adding a project item
@app.route('/add', methods=["GET", "POST"])
@admin_only
def add():
    project_form = ProjectForm()
    if project_form.validate_on_submit():
        new_project = Project(
            projectName=request.form["projectName"],  # Alternative: projectName=form.projectName.data
            technologiesUsed=request.form["technologiesUsed"],
            description=request.form["description"],
            difficultyRating=request.form["difficultyRating"],
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=project_form, current_user=current_user)

# Edit a project
@app.route("/edit/<int:index>", methods=["GET", "POST"])
@admin_only
def edit(index):
    project = db.get_or_404(Project, index)
    # Autofilling edit form with existing data
    form = ProjectForm(
        projectName=project.projectName,
        technologiesUsed=project.technologiesUsed,
        description=project.description,
        difficultyRating=project.difficultyRating
    )
    if form.validate_on_submit():
        project.projectName = form.projectName.data
        project.technologiesUsed = form.technologiesUsed.data
        project.description = form.description.data
        project.difficultyRating = form.difficultyRating.data
        db.session.commit()
        return redirect(url_for("all_project_details", index=project.id))
    return render_template("add.html", form=form, is_edit=True, current_user=current_user)

# Delete a Project
@app.route("/delete/<int:index>")
@admin_only
def delete(index):
    # Deleting a record by ID
    project_to_delete = db.get_or_404(Project, index)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

# Downloading a file
@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/WebsiteDevelopment.txt")

# Registering an account on the site
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Checking if the email already has an account
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("Email already has an account, log in instead!")
            return redirect(url_for('login'))

        # Creating the account
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)
    # Add current_user=current_user to each instance of render_template throughout project


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Checking if the email has an account
        if not user:
            flash("That email does not have an account")
            return redirect(url_for('login'))
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash("Password is Incorrect")
            return redirect(url_for('login'))
        else:
            # Logging in the user
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# About page
@app.route('/about')
def about():
    return render_template("about.html", current_user=current_user)

# Contact page, contains a contact form
@app.route('/contact', methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        print(contact_form.email.data)
    return render_template("contact.html", form=contact_form, current_user=current_user)

# Code to run the program
if __name__ == "__main__":
    app.run(debug=True)