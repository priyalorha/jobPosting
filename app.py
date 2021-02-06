import os
from datetime import datetime

from flask import (Flask, render_template, redirect, request, session, url_for, make_response)
from flask_wtf import form

from emails import sendEmails
from cvUploader import upload_cv
from models import Users, jobPosting
from templates.form_models import LoginForm, SignUpForm, jobSearch, EditProfileUser, jobPostingForm
from utils import random_with_N_digits, appendApplicants_jobPosting, savejobPosting, getJobs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['instance_path'] = 'img'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/job/<id>', methods=['GET', 'POST'])
def job(id):
    if id:
        id = int(id)
        job = getJobs(id)
        return render_template('jobList_individual.html',
                               job=getJobs(id))
    return render_template('jobList_individual.html'
                            )


@app.route('/setJobPosting', methods=['GET', 'POST'])
def setJobPosting():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        year = request.form['expiry_year']
        month = request.form['expiry_month']
        date = request.form['expiry_date']
        if request.form['latitude']:
            latitude = request.form.get('latitude', 0)
        else:
            latitude = request.cookies.get('latitude', 0)
        if request.form['longitude']:
            longitude = request.form.get('longitude', 0)
        else:
            longitude = request.cookies.get('longitude', 0)

        date_str = datetime(day=int(date),
                            month=int(month),
                            year=int(year))
        savejobPosting(title=title,
                       description=description,
                       location=[float(latitude), float(longitude)],
                       expiryDate=date_str.strftime('%x'))

    return dashboard()


@app.route('/applyJob', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        jobid = request.form['jobid']

        if file and allowed_file(file.filename):
            file.save(file.filename)
            res = upload_cv(file.filename)
            os.remove(file.filename)
            appendApplicants_jobPosting(applicant_email=session['email'], id=jobid)

    return dashboard()


@app.route('/apply/<field_id>', methods=['GET', 'POST'])
def apply(field_id):
    return render_template('applyJob.html', jobid=field_id)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.cookies.get('loggedin') == 'true':
        EditProfileUserForm = EditProfileUser()
        user = Users.objects(email=request.cookies.get('email'))
        if user:
            EditProfileUserForm.email.data = user[0].email
            EditProfileUserForm.name.data = user[0].name
            EditProfileUserForm.mobile.data = user[0].mobile
            type = user[0].admin
        if type == False or request.cookies['type'] == 'user':
            return render_template('dashboard.html',
                                   type=user,
                                   profile=EditProfileUserForm,
                                   job=jobSearch())
        else:

            return render_template('dashboard_admin.html',
                                   type=request.cookies.get('type'),
                                   profile=EditProfileUserForm,
                                   job=jobPostingForm(),
                                   jobList=getJobs()

                                   )

    return render_template('LoginSignUp.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    update_fields = {}
    if len(name) > 0:
        update_fields['name'] = name
    if len(email) > 0:
        update_fields['email'] = email
        res = make_response()
        res.set_cookie('email', email)
    if len(email) > 0:
        update_fields['mobile'] = mobile
    user = Users.objects(email=request.cookies.get('email'))[0]
    if user:
        user.update(**update_fields)

    return dashboard()


@app.route('/jobSearchAPi', methods=['GET', 'POST'])
def jobSearchAPi():
    points = []
    if request.method == 'POST':
        title = request.form['title']
        distance = request.form['distance']
        # latitude = request.form.get('latitude', 0)
        # longitude = request.form.get('latitude', 0)
        latitude = request.cookies.get('latitude') if request.cookies.get('latitude') else 0
        longitude = request.cookies.get('longitude') if request.cookies.get('longitude') else 0
        # print(f"token data ${request.get_json()['latitude']} {request.get_json()['longitude']}")

        if distance and latitude and longitude:
            points = [[float(latitude), float(longitude)], float(distance)]
        if points:
            jobs = jobPosting.objects(location__geo_within_sphere=points)

        else:
            jobs = jobPosting.objects()
        if jobs:
            job = [i.to_dict() for i in jobs if title in i.title.split()
                   or title in i.description.split()
                   and datetime.now() < i.expiryDate]
        if job:
            print(job)
            return render_template('jobList.html', job=job)
        if jobs:
            jobs = [i.to_dict() for i in jobs]
            print(jobs)

            return render_template('jobList.html', job=jobs)

    return render_template('jobList.html', message="could not find job :(")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('otp', None)
    res = make_response("Cookie Removed")
    res.set_cookie('email', '')
    res.set_cookie('loggedin', 'false')
    res.set_cookie('type', '')
    return render_template('LoginSignUp.html')


@app.route('/signup', methods=['POST'])
def signup():
    if request.form['email'] == session['email'] and str(request.form['otp']) == str(session['otp']):
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        Users(name=name, email=email, mobile=mobile).save()

        res = make_response()
        res.set_cookie('email', email)
        res.set_cookie('loggedin', 'true')
        res.set_cookie('type', 'user')

        return dashboard()

    return render_template('LoginSignUp.html')


@app.route('/login', methods=['POST'])
def login():
    print(request.form['email'] == session['email'] and str(request.form['otp']) == str(session['otp'])
          )
    print(request.form['email'], session['email'], str(request.form['otp']), str(session['otp'])
          )
    if request.form['email'] == session['email'] and str(request.form['otp']) == str(session['otp']):
        if session['is_admin']:
            res = make_response(render_template('dashboard.html', type="admin"))
            res.set_cookie('type', 'admin')
        else:
            res = make_response(render_template('dashboard.html', type="user"))
            res.set_cookie('type', 'user')
        res.set_cookie('email', request.form['email'])
        res.set_cookie('loggedin', 'true')
        return res
    otp = random_with_N_digits(6)
    print(otp)
    sendEmails(to_email=request.form['email'], otp=otp)
    session['otp'] = otp

    return render_template('LoginSignUp.html')


@app.route('/loginsignup', methods=['GET', 'POST'])
def loginsignup():
    if request.method == 'POST':
        email = request.form['email']
        otp = random_with_N_digits(6)
        print(otp)
        sendEmails(to_email=email, otp=otp)
        user = Users.objects(email=email)
        session['email'] = email
        session['otp'] = otp
        if user:
            user = user[0]
            form = LoginForm()
            form.email.data = email
            form.otp.label = "OTP: (check your email)"
            print(user.to_dict())
            session['is_admin'] = user.admin
            return render_template('login.html', title='login', form=form)
        else:
            form = SignUpForm()
            form.email.data = email
            form.otp.label = "OTP: (check your email)"
            return render_template('login.html', title='signup', form=form)

    return render_template('LoginSignUp.html')


@app.route('/')
def index():
    if request.cookies.get('loggedin') == 'true':
        return dashboard()
    return render_template('LoginSignUp.html')


if __name__ == '__main__':
   app.run(debug=True)

