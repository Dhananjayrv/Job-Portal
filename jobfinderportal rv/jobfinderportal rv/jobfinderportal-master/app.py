from flask import Flask, render_template, request, redirect, url_for, flash, abort,session ,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'img', 'logo')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

def get_logo_filename(company_name):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}

    for ext in allowed_extensions:
        filename = f"{company_name}.{ext}"
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace('/', os.path.sep))

        if os.path.exists(logo_path):
            return filename

    # If no valid logo is found, use a default image or handle accordingly
    return 'default_logo.png'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.String(1000), nullable=True)
    company_name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(20), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    posted_date = db.Column(db.String(50), nullable=True)
    company_logo = db.Column(db.String(255), nullable=True)
    job_category = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.String(20), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    applications = db.relationship('JobApplication', backref='job', lazy=True)

    def __repr__(self):
        return f"Job(id={self.id}, job_title={self.job_title}, company_name={self.company_name}, location={self.location}, salary={self.salary}, job_type={self.job_type}, posted_date={self.posted_date}, company_logo={self.company_logo}, user_id={self.user_id})"

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    full_name = db.Column(db.String(255), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    linkedin_profile = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    degree = db.Column(db.String(50), nullable=True)
    school = db.Column(db.String(50), nullable=True)
    graduation_date = db.Column(db.String(20), nullable=True)
    previous_employer = db.Column(db.String(255), nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    dates_of_employment = db.Column(db.String(50), nullable=True)
    job_responsibilities = db.Column(db.String(1000), nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    reference_name = db.Column(db.String(120), nullable=True)
    reference_contact = db.Column(db.String(20), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    resume = db.Column(db.String(255), nullable=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    job = db.Column(db.String(50), nullable=True)
    education = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    user_type = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)

    jobs = db.relationship('Job', backref='user', lazy=True)
    applications = db.relationship('JobApplication', backref='user', lazy=True)

with app.app_context():
    db.create_all()



    super_admin = User.query.filter_by(username='rage').first()

    if not super_admin:
        hashed_password = generate_password_hash('Dhananjay@7', method='sha256')

        super_admin_user = User(
            email='kdhananjay444@gmail.com',
            password=hashed_password,
            username='rage',
            name='rage',
            user_type='super_admin'
        )

        db.session.add(super_admin_user)
        db.session.commit()

        all_jobs = Job.query.all()

        for job in all_jobs:
            job.user_id = super_admin_user.id

        db.session.commit()

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    # Retrieve filter options dynamically from the database
    categories = db.session.query(Job.job_category.distinct()).all()
    types = db.session.query(Job.job_type.distinct()).all()
    locations = db.session.query(Job.location.distinct()).all()

    if request.method == 'POST':
        # Handle filter parameters sent from the form
        category_filter = request.form.get('category_filter')
        type_filters = request.form.getlist('type_filter')
        location_filter = request.form.get('location_filter')
        experience_filters = request.form.getlist('experience_filter')
        posted_within_filter = request.form.get('posted_within_filter')

        # Use the filters to query the database
        job_listings = Job.query

        if category_filter:
            job_listings = job_listings.filter(Job.job_category == category_filter)

        if type_filters:
            job_listings = job_listings.filter(Job.job_type.in_(type_filters))

        if location_filter:
            job_listings = job_listings.filter(Job.location == location_filter)

        if experience_filters:
            job_listings = job_listings.filter(Job.experience.in_(experience_filters))

        if posted_within_filter:
            # Add logic to filter based on posted within
            if posted_within_filter == 'today':
                today = datetime.now()
                job_listings = job_listings.filter(Job.posted_date == today.strftime('%Y-%m-%d'))
            elif posted_within_filter == 'last_week':
                last_week = datetime.now() - timedelta(days=7)
                job_listings = job_listings.filter(Job.posted_date >= last_week.strftime('%Y-%m-%d'))

        job_listings = job_listings.all()

    else:
        # If it's a GET request, display all jobs
        job_listings = Job.query.all()

    return render_template(
        'index.html',
        job_listings=job_listings,
        categories=categories,
        types=types,
        locations=locations,
        get_logo_filename=get_logo_filename
    )

@login_required
def download_resume(application_id):
    application = JobApplication.query.get_or_404(application_id)

    resume_folder = os.path.join(app.root_path, 'static', 'img', 'logo', 'job_applications')
    resume_path = os.path.join(resume_folder, application.resume_filename)

    # Set the custom filename with the applicant's name
    custom_filename = f"{application.user.username}_{application.resume_filename}"

    return send_from_directory(resume_folder, application.resume_filename, as_attachment=True, download_name=custom_filename)



@app.route('/job_details')
def job_details():
    return render_template('job_details.html')

@app.route('/job_listing', methods=['GET', 'POST'])
def job_listing():
    # Retrieve filter options dynamically from the database
    categories = db.session.query(Job.job_category.distinct()).all()
    types = db.session.query(Job.job_type.distinct()).all()
    locations = db.session.query(Job.location.distinct()).all()

    if request.method == 'POST':
        # Handle filter parameters sent from the form
        category_filter = request.form.get('category_filter')
        type_filters = request.form.getlist('type_filter')
        location_filter = request.form.get('location_filter')
        experience_filters = request.form.getlist('experience_filter')
        posted_within_filter = request.form.get('posted_within_filter')

        # Use the filters to query the database
        job_listings = Job.query

        if category_filter:
            job_listings = job_listings.filter(Job.job_category == category_filter)

        if type_filters:
            job_listings = job_listings.filter(Job.job_type.in_(type_filters))

        if location_filter:
            job_listings = job_listings.filter(Job.location == location_filter)

        if experience_filters:
            job_listings = job_listings.filter(Job.experience.in_(experience_filters))

        if posted_within_filter:
            # Add logic to filter based on posted within
            if posted_within_filter == 'today':
                today = datetime.now()
                job_listings = job_listings.filter(Job.posted_date == today.strftime('%Y-%m-%d'))
            elif posted_within_filter == 'last_week':
                last_week = datetime.now() - timedelta(days=7)
                job_listings = job_listings.filter(Job.posted_date >= last_week.strftime('%Y-%m-%d'))

        job_listings = job_listings.all()

        return render_template(
            'job_listing.html',
            job_listings=job_listings,
            categories=categories,
            types=types,
            locations=locations,
            get_logo_filename=get_logo_filename
        )

    # If it's a GET request, display all jobs
    job_listings = Job.query.all()

    return render_template(
        'job_listing.html',
        job_listings=job_listings,
        categories=categories,
        types=types,
        locations=locations,
        get_logo_filename=get_logo_filename
    )

@app.route('/single_blog')
def single_blog():
    return render_template('single-blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/elements')
def elements():
    return render_template('elements.html')

@app.route('/manage_applicant/<int:user_id>', methods=['GET'])
@login_required  # Use this decorator to ensure only authenticated users can access the page
def manage_applicant(user_id):
    # Fetch the user details and any additional information needed for the applicant
    user = User.query.get_or_404(user_id)
    # You might need to adapt the query based on your database structure

    return render_template('manage_applicant.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['username'] = user.username
            session['user_type'] = user.user_type

            if user.user_type == 'employee':
                return redirect(url_for('job_listing'))
            elif user.user_type == 'employer':
                return redirect(url_for('manage_jobs'))
            elif user.user_type == 'super_admin':
                return redirect(url_for('manage_jobs'))
        else:
            flash("Authentication failed. Please check your credentials.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        phone = request.form['phone']
        job = request.form['job']
        education = request.form['education']
        address = request.form['address']
        user_type = request.form['user_type']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered. Please use a different email.", 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(
            email=email,
            password=hashed_password,
            username=email.split('@')[0],
            name=name,
            phone=phone,
            job=job,
            education=education,
            address=address,
            user_type=user_type
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please login.", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/contact_process', methods=['POST'])
def contact_process():
    # your contact process logic here
    return "Message sent successfully"

@app.route('/manage_jobs', methods=['GET', 'POST'])
@login_required
def manage_jobs():
    if current_user.user_type == 'super_admin':
        jobs = Job.query.all()
        applications = JobApplication.query.all()
    else:
        jobs = Job.query.filter_by(user_id=current_user.id).all()
        # Fetch job applications associated with the logged-in employer
        applications = JobApplication.query.join(Job).filter(Job.user_id == current_user.id).all()

    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        company_name = request.form['company_name']
        location = request.form['location']
        salary = request.form['salary']
        job_type = request.form['job_type']

        if 'company_logo' in request.files:
            logo_file = request.files['company_logo']

            if logo_file.filename != '':
                if '.' in logo_file.filename and \
                        logo_file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
                    
                    # Sanitize the company name to create a valid filename
                    sanitized_company_name = secure_filename(company_name)
                    
                    # Combine company name and file extension to create a unique filename
                    filename = f"{sanitized_company_name}.{logo_file.filename.rsplit('.', 1)[1].lower()}"
                    
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace('/', os.path.sep))
                    logo_file.save(logo_path)
                else:
                    flash('Invalid file type for company logo. Allowed types are: png, jpg, jpeg, gif', 'error')

        new_job = Job(
            job_title=job_title,
            job_description=job_description,
            company_name=company_name,
            location=location,
            salary=salary,
            job_type=job_type,
            user_id=current_user.id,
            company_logo=filename if 'filename' in locals() else None
        )

        db.session.add(new_job)
        db.session.commit()

        return redirect(url_for('job_listing'))

    return render_template('manage_jobs.html', jobs=jobs, applications=applications)


@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get(job_id)

    if request.method == 'POST':
        job.job_title = request.form['job_title']
        job.job_description = request.form['job_description']
        job.company_name = request.form['company_name']
        job.location = request.form['location']
        job.salary = request.form['salary']
        job.job_type = request.form['job_type']

        db.session.commit()
        flash('Job updated successfully', 'success')
        return redirect(url_for('manage_jobs'))

    return render_template('edit_job.html', job=job)

@app.route('/delete_selected_jobs', methods=['POST'])
@login_required
def delete_jobs():
    job_ids_to_delete = request.form.getlist('selected_jobs[]')

    if not job_ids_to_delete:
        flash('No jobs selected for deletion', 'error')
        return redirect(url_for('manage_jobs'))

    if current_user.user_type == 'super_admin':
        jobs_to_delete = Job.query.filter(Job.id.in_(job_ids_to_delete)).all()
    else:
        jobs_to_delete = Job.query.filter(Job.id.in_(job_ids_to_delete), Job.user_id == current_user.id).all()

    for job in jobs_to_delete:
        db.session.delete(job)

    db.session.commit()
    flash('Selected jobs deleted successfully', 'success')

    return redirect(url_for('manage_jobs'))

@app.route('/confirmation_page')
def confirmation_page():
    return render_template('confirmation_page.html')

# New routes for job applications

@app.route('/application_form/<int:job_id>', methods=['GET', 'POST'])
@login_required
def application_form(job_id):
    job = Job.query.get(job_id)

    if not job:
        abort(404)  # Job not found, handle appropriately

    if request.method == 'POST':
        resume_file = request.files['resume']
        cover_letter = request.form['cover_letter']
        linkedin_profile = request.form['linkedin_profile']
        full_name = request.form['full_name']
        email = request.form['email']
        degree = request.form['degree']
        school = request.form['school']
        graduation_date = request.form['graduation_date']
        previous_employer = request.form['previous_employer']
        job_title = request.form['job_title']
        skills = request.form['skills']
        reference_name = request.form['reference_name']
        reference_contact = request.form['reference_contact']
        portfolio = request.form['portfolio']

        if resume_file.filename != '':
            resume_filename = secure_filename(resume_file.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_applications', resume_filename)
            resume_file.save(resume_path)

            new_application = JobApplication(
                user_id=current_user.id,
                job_id=job_id,
                resume_filename=resume_filename
            )

            # Add other fields to the JobApplication instance
            new_application.cover_letter = cover_letter
            new_application.linkedin_profile = linkedin_profile
            new_application.full_name = full_name
            new_application.email = email
            new_application.degree = degree
            new_application.school = school
            new_application.graduation_date = graduation_date
            new_application.previous_employer = previous_employer
            new_application.job_title = job_title
            new_application.skills = skills
            new_application.reference_name = reference_name
            new_application.reference_contact = reference_contact
            new_application.portfolio = portfolio

            print("New Application Details:")
            print(f"User ID: {new_application.user_id}")
            print(f"Job ID: {new_application.job_id}")
            print(f"Resume Filename: {new_application.resume_filename}")
            print(f"Cover Letter: {new_application.cover_letter}")
            print(f"LinkedIn Profile: {new_application.linkedin_profile}")
            # Add more print statements for other fields

            db.session.add(new_application)
            db.session.commit()

            flash('Application submitted successfully', 'success')
            return redirect(url_for('job_listing'))
        else:
            flash('Please upload a resume file', 'error')

    return render_template('application_form.html', job=job)




@app.route('/manage_applications', methods=['GET', 'POST'])
@login_required
def manage_applications():
    if current_user.user_type == 'super_admin':
        jobs = Job.query.all()
        applications = JobApplication.query.all()
    else:
        jobs = Job.query.filter_by(user_id=current_user.id).all()
        applications = JobApplication.query.join(Job).filter(Job.user_id == current_user.id).all()

    if request.method == 'POST':
        # Your existing code for adding a new job
        flash('Job added successfully', 'success')
        return redirect(url_for('manage_applications'))

    return render_template('manage_jobs.html', jobs=jobs, applications=applications)


# New route for viewing details of a specific job application
@app.route('/manage_applications/<int:application_id>')
@login_required
def view_application(application_id):
    # Retrieve applicant details based on the application_id
    application = JobApplication.query.get(application_id)

    if not application:
        flash('Job application not found', 'error')
        return redirect(url_for('manage_applications'))

    return render_template('manage_applications.html', application=application)
    
@app.route('/job_applications/<int:job_id>')
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    applications = job.applications

    for application in applications:
        print(f"Application ID: {application.id}")
        print(f"Applicant: {application.user.full_name}") 
        print(f"Email: {application.user.email}")
        print(f"Phone Number: {application.user.phone}")
        print(f"Address: {application.address}")  
        print(f"Resume: {application.resume}")
        print(f"Cover Letter: {application.cover_letter}")
        print(f"LinkedIn Profile: {application.linkedin_profile}")
        print(f"Degree: {application.degree}")
        print(f"School: {application.school}")
        print(f"Graduation Date: {application.graduation_date}")
        print(f"Previous Employer: {application.previous_employer}")
        print(f"Job Title: {application.job_title}")
        print(f"Dates of Employment: {application.dates_of_employment}")
        print(f"Job Responsibilities: {application.job_responsibilities}")
        print(f"Skills: {application.skills}")
        print(f"Reference Name: {application.reference_name}")
        print(f"Reference Contact: {application.reference_contact}")
        print(f"Portfolio: {application.portfolio}")
        print("\n") 
    
    return render_template('job_applications.html', job=job, applications=applications)

@app.route('/download_resume/<int:application_id>')
@login_required
def download_resume(application_id):
    application = JobApplication.query.get_or_404(application_id)

    resume_folder = os.path.join(app.root_path, 'static', 'img', 'logo', 'job_applications')
    resume_path = os.path.join(resume_folder, application.resume_filename)

    # Set the custom filename with the applicant's name
    custom_filename = f"{application.user.username}_{application.resume_filename}"

    return send_from_directory(resume_folder, application.resume_filename, as_attachment=True, download_name=custom_filename)


if __name__ == '__main__':
    app.run(debug=True)
