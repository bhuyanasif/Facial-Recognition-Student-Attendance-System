import os
import secrets
import numpy as np
import cv2
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, AttendanceForm, TakePhotoForm, ManualAttendanceForm
from flaskblog.models import Student, Faculty, Subject, Attendance, ImageData
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", )
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/stlogin", methods=['GET', 'POST'])
def stlogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(id=form.id.data).first()
        if user and form.password.data==user.password:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('stattendance'))
        else:
            flash('Login Unsuccessful. Please check ID and password', 'danger')
    return render_template('stlogin.html', title='Login', form=form)

@app.route("/flogin", methods=['GET', 'POST'])
def flogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = Faculty.query.filter_by(id=form.id.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('fhome'))
        else:
            flash('Login Unsuccessful. Please check ID and password', 'danger')
    return render_template('flogin.html', title='Login', form=form)


@app.route("/stattendance")
@login_required
def stattendance():
    user = Student.query.filter_by(id=current_user.id).first()
    sublist = Subject.query.filter_by(course=user.course, sem=user.sem).all()
    return render_template('stattendance.html', title='About', sublist=sublist)


@app.route("/ftakeattendance", methods=['GET', 'POST'])
@login_required
def ftakeattendance():
    return render_template('ftakeattendance.html', title='About')

def predict_face(imageNp):
    file_path = os.path.join(app.root_path, "haarcascade_frontalface_default.xml")
    detector= cv2.CascadeClassifier(file_path)
    faces=detector.detectMultiScale(imageNp,1.1,4)

    face = []
    label = []
    for (x,y,w,h) in faces:
        face.append(imageNp[y:y+h,x:x+w])
    model = cv2.face.LBPHFaceRecognizer_create()
    file_path = os.path.join(app.root_path, "trainner.yml")
    model.read(file_path)

    for f in face:
        labels = model.predict(f)
        label.append(labels[0])
    return label

@app.route("/fhome")
@login_required
def fhome():
    return render_template('fhome.html', title="choose")

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    f = request.files['file']
    if f:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(f.filename)
        if (f_ext == '.jpg' or f_ext == '.jpeg' or f_ext == '.png'):
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.root_path, 'static/attphoto', picture_fn)

            i = Image.open(f)
            i.save(picture_path)
            att = ImageData.query.filter_by(fid=current_user.id).first()
            sub = 'a'
            if att:
                att.image_file = picture_path
                att.fid = current_user.id
                sub = att.subname
                db.session.commit()
            details = Subject.query.filter_by(subname=sub,fid=current_user.id).first()
            flash('Uploaded','success')
            getImage=''
            pilImage='12'
            label = []
            getImage = ImageData.query.filter_by(fid=current_user.id).first()
            ImageData.query.filter_by(fid=current_user.id).delete()
            db.session.commit()
            label = []
            if getImage:
                pilImage=Image.open(getImage.image_file).convert('L')

                imageNp=np.array(pilImage,'uint8')
                label = predict_face(imageNp)
            ImageData.query.filter_by(fid=current_user.id).delete()
            db.session.commit()

            student = Student.query.all()
            if details:
                student = Student.query.filter_by(sem=details.sem,course=details.course).all()
            flag = 0
            attd_details = []
            attd_details_temp = {}
            attd_details_attd = []
            attd_details_percent = []
            attd_details_status = []
            i=0
            totalclass = 0;
            sem = 0
            course=''

            label.sort()
            stdlabel = []
            for num in label:
                if num not in stdlabel:
                    stdlabel.append(num)
            while i < len(student):
                attd_details_temp['id']=(student[i].id)
                attd_details_temp['name']=(student[i].username)
                for l in stdlabel:
                    if student[i].id == l and details:
                        st = Attendance.query.filter_by(subid=details.id,id=student[i].id).all()
                        attd_details_temp['attd'] = ((details.totalclass + 1) - len(st))
                        attd_details_temp['percentage'] = ((((details.totalclass + 1) - len(st))/(details.totalclass+1))*100)
                        attd_details_temp['status'] = ('P')
                        flag = 1
                        break
                if flag == 0 and details:
                    atd = Attendance(id=student[i].id,subid=details.id)
                    db.session.add(atd)
                    db.session.commit()
                    st = Attendance.query.filter_by(subid=details.id,id=student[i].id).all()
                    attd_details_temp['attd']=((details.totalclass + 1) - len(st))
                    attd_details_temp['percentage']=((((details.totalclass + 1) - len(st))/(details.totalclass+1))*100)
                    attd_details_temp['status']=('A')
                flag = 0
                i+=1
                attd_details.append(attd_details_temp)
                attd_details_temp = {}
            if details:
                details.totalclass += 1
                totalclass = details.totalclass
                sem = details.sem
                course = details.course
            db.session.commit()

            return render_template('upload.html', attd_details= attd_details, totalclass = totalclass, sub=sub, sem=sem, course=course)
        else:
            flash("Please upload photo in jpg/jpeg/png format")
            return redirect(url_for('ftakeattendance'))
    else:
        flash("Please upload a photo")
        return redirect(url_for('ftakeattendance'))
    return render_template('upload.html', title='About')
    if request.method == 'GET':
        return render_template('upload.html', title='About')


@app.route("/manualadd",methods=['GET','POST'])
@login_required
def manualadd():
    form = ManualAttendanceForm()
    id = form.regid.data
    flash(id)
    return render_template('manualadd.html')

@app.route("/fattendance", methods=['GET', 'POST'])
@login_required
def fattendance():
    form = AttendanceForm()
    form.sub.choices = [(subj.id , subj.subname) for subj in Subject.query.filter_by(fid=current_user.id).all()]
    if request.method == 'POST':
        clist = Subject.query.filter_by(subname=form.sub.data,fid=current_user.id).first()
        course=0
        sem=0
        if clist:
            course = clist.course
            sem = clist.sem
            att = ImageData.query.filter_by(subname=form.sub.data,fid=current_user.id).first()
            if att:
                ImageData.query.filter_by(subname=form.sub.data,fid=current_user.id).delete()
            att = ImageData(subname=form.sub.data,fid=current_user.id)
            db.session.add(att)
            db.session.commit()
        return render_template('ftakeattendance.html', title='Attendance', sub = form.sub.data, course = course, sem = sem)
    return render_template('fattendance.html', form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
