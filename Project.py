#!/usr/bin/python
from flask import Flask, render_template,  request , flash , redirect, url_for , session , send_from_directory
from wtforms import Form, StringField, TextAreaField, RadioField, SelectField , validators , PasswordField , IntegerField
from articleinfo import ArticleInfo
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_security import UserMixin, RoleMixin, login_required
import datetime

from articleinfo import ArticleInfo
from Magazine import Magazine
from Book import Book
from Clinic import Clinic
from Disease import Disease

from flask_wtf.file import FileField, FileAllowed , FileRequired
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm

from chat import Chat
import random
from pubmotd import healthtips
import firebase_admin
from firebase_admin import credentials, db
from flask.ext.security.forms import LoginForm

cred = credentials.Certificate('./cred/oopp-shaq-firebase-adminsdk-1j479-4539b4b30b.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://oopp-shaq.firebaseio.com/'
})


root = db.reference()


#Set up locations where uploaded file will be stored
UPLOAD_PHOTOS_DEST = 'C:\Garena\Libary\static\images'





app = Flask(__name__)
app.config.update(
    DEBUG=False,
    SQLALCHEMY_DATABASE_URI='sqlite:///users.db',
    SECRET_KEY='James Bond',
    SECURITY_REGISTERABLE=True,
    SECURITY_PASSWORD_SALT = 'Some_salt',
    SECURITY_SEND_REGISTER_EMAIL = False
)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_PHOTOS_DEST
#only upload photo by UploadSet function
photos = UploadSet('photos', IMAGES)
#call configure_upload to store configuration of flask upload into flask app
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


db = SQLAlchemy(app)

Bootstrap(app)
Mail(app)
roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(),
                                                db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
Security(app, user_datastore)


def __str__(self):
    return self.email


class INFO(FlaskForm):
    title = StringField('Title', [
        validators.DataRequired()
    ])
    info = TextAreaField('Description', [
        validators.DataRequired()
    ])
    artphoto = FileField('Upload the image you want', validators=[FileRequired(), FileAllowed(photos, u'Image only!')])



@app.route('/chatlogin', methods=['GET', 'POST'])
def chatlogin():
    form = logintest(request.form)
    if request.method == 'POST':
        username = form.username.data
        session['username'] = username
        print(session['username'])

        flash('Login successful')
        return redirect(url_for('msgs'))
    return render_template('chatlogin.html', form=form)


@app.route('/adminmotd')
def motdhome():
    return render_template('motdhome.html')


class SendMessage(Form):
    message = TextAreaField('Message', [
        validators.Length(min=1),
        validators.DataRequired()
    ])
userlist = []
@app.route('/chatroom', methods=['GET', 'POST'])
def msgs():
    form = SendMessage(request.form)
    if request.method == 'POST' and form.validate():
        username = session['username']
        print(username)
        if username not in userlist:
            userlist.append(username)

        message = form.message.data
        chatnumber = datetime.time(datetime.now())
        chatnumber = str(chatnumber)

        msg = Chat(message, username, chatnumber)
        chatno = str(chatnumber)
        msg_db = root.child('chathistory' + username)
        print(username)
        msg_db.push({
            'message': msg.get_message(),
            'username': msg.get_username(),
            'chatnumber': msg.get_chatnumber()

        })

    print(userlist)
    username = session['username']
    timenow = datetime.time(datetime.now())
    print(timenow)
    chathist = root.child('chathistory' + username).get()
    list = []
    if chathist is not None:
        for chatid in chathist:
            eachmsg = chathist[chatid]
            msg = Chat(eachmsg['message'], eachmsg['username'], eachmsg['chatnumber'])
            msg.set_chatid(chatid)
            list.append(msg)

    return render_template('chat.html', form=form, chathist=list, username=username, now=timenow)



@app.route('/viewusers')
def viewusers():
    print(userlist)
    return render_template('viewusers.html', userlist=userlist)

@app.route('/chathome')
def chathome():
    return render_template('userchathome.html')


@app.route('/chathomedoc')
def chathomedoc():


    return render_template('doctorchathome.html')





@app.route('/motdpage')
def motd():
    tips = root.child('healthtips').get()
    list = []  # create a list to store all the publication objects
    for pubid in tips:
        eachpub = tips[pubid]
        print(eachpub)
        pub = healthtips(eachpub['title'], eachpub['description'])
        pub.set_pubid(pubid)
        print(pub.get_pubid())
        list.append(pub)
    rndmsg = random.choice(list)
    print(rndmsg.get_title())

    return render_template('MOTD.html', rndmsg=rndmsg)

@app.route('/viewtips')
def viewtips():
    tips = root.child('healthtips').get()
    list = []  # create a list to store all the publication objects
    for pubid in tips:
        eachpub = tips[pubid]
        print(eachpub)
        pub = healthtips(eachpub['title'], eachpub['description'])
        pub.set_pubid(pubid)
        print(pub.get_pubid())
        list.append(pub)
    print(list)
    return render_template('view_all_motd.html', publications=list)

class MotdForm(Form):
    title = StringField('Title', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    description = TextAreaField('Description')




@app.route('/createtip', methods=['GET', 'POST'])
def newtip():
    form = MotdForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        pub = healthtips(title, description)
        pub_db = root.child('healthtips')
        pub_db.push({
            'title': pub.get_title(),
            'description': pub.get_description()
        })

        flash('Message Inserted Successfully.', 'success')

        return redirect(url_for('viewtips'))

    return render_template('create_motd.html', form=form)

@app.route('/update/<string:id>/', methods=['GET', 'POST'])
def update_motd(id):
    form = MotdForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        pub = healthtips(title, description)

        pub_db = root.child('healthtips/' + id)
        pub_db.set({
            'title': pub.get_title(),
            'description': pub.get_description()
            })

        flash('Magazine Updated Sucessfully.', 'success')

        return redirect(url_for('viewtips'))
    else:
        url = 'healthtips/' + id
        eachpub = root.child(url).get()
        pub = healthtips(eachpub['title'], eachpub['description'])
        pub.set_pubid(id)

        return render_template('update_motd.html', form=form)



@app.route('/article')
def home():
    newinfo = root.child('newinfo').get()
    list = []
    if list is not None:
     for i in newinfo:
        eachinfo = newinfo[i]
        info = ArticleInfo(eachinfo['title'],
                           eachinfo['info'],
                           eachinfo['artphoto'])
        list.append(info)


    return render_template('admin.html', newinfo=list)

@app.route('/viewarticle')
def viewarticle():
    newinfo = root.child('newinfo').get()
    list = []  # create a list to store all the publication objects
    if newinfo is not None:
        for artid in newinfo:
            eachinfo = newinfo[artid] #or eachinfo = root.child('newinfo/'+ artid).get()
            info = ArticleInfo(eachinfo['title'],eachinfo['info'],eachinfo['artphoto'])
            info.set_artid(artid)
            print(info.get_artid())

            list.append(info)

    return render_template('viewarticles.html', newinfo=list)

@app.route('/update_article/<string:id>/', methods=['GET', 'POST'])
def update_article(id):
    form = INFO(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        info = form.info.data
        filename = photos.save(form.artphoto.data)

        information = ArticleInfo(title, info, filename)

        information_db = root.child('newinfo/' + id)
        information_db.set({
            'title': information.get_title(),
            'info': information.get_info(),
            'photo': information.get_photo(),
            })

        flash('Article Updated Sucessfully.', 'success')

        return redirect(url_for('viewarticle'))
    else:
        url = 'newinfo/' + id
        eachinfo = root.child(url).get()

        info = ArticleInfo(eachinfo['title'], eachinfo['info'], eachinfo['artphoto'])

        info.set_artid(id)
        form.title.data = info.get_title()
        form.info.data = info.get_info()
        form.artphoto.data = info.get_artphoto()


    return render_template('update_article.html', form=form)

@app.route('/delete_article/<string:id>', methods=['POST'])
def delete_article(id):
    information_db = root.child('newinfo/' + id)
    information_db.delete()
    flash('Article information deleted', 'success')
    return redirect(url_for('viewarticle'))



@app.route('/createarticle', methods=['GET', 'POST'])
def edit():
    form = INFO()
    if form.validate_on_submit():
        title = form.title.data
        info = form.info.data
        filename = photos.save(form.artphoto.data)

        information = ArticleInfo(title, info, filename)

        information_db = root.child('newinfo')
        information_db.push({
            'title': information.get_title(),
            'info': information.get_info(),
            'artphoto': information.get_artphoto(),
        })


        flash('Article Information Updated Successfully', 'success')

        return redirect(url_for('viewarticle'))

    return render_template('editarticle1.html', form=form)

@app.route('/login')
def Login():

    session['id'] = request.form['id']
    return redirect(url_for('/login'))


@app.route('/Logout')
def logout():
 session.clear()
 return redirect(url_for('main'))


@app.route('/chat/<email>')
def profile(email):
    user = User.query.filter_by(email=email).first()
    form='form'
    return render_template('chat.html',email=email,user=user,form=form)
@app.route('/post_user',methods=['POST'])
def post_user():
    user = User(request.form['username'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('home'))



class DoctorForm(Form):
    dname = StringField('Dname', [
        validators.Length(min=3, max=30),
        validators.DataRequired()])
    dinformation = TextAreaField('Dinformation')


class MotdForm(Form):
    title = StringField('Title', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    description = TextAreaField('Description')




@app.route('/delete_publication/<string:id>', methods=['POST'])
def delete_publication(id):
    pub_db = root.child('healthtips/' + id)
    pub_db.delete()
    flash('Publication Deleted', 'success')

    return redirect(url_for('viewtips'))




class logintest(Form):
    username = StringField('username', [
        validators.length(min=5, max=30),
        validators.DataRequired()],
                           render_kw={'placeholder': 'Full Name'})


@app.route('/register',methods=['GET','POST'])
def index():
    return render_template('register_user.html')


@app.route('/monitor')
def monitor():

    queues = root.child('queues').get()
    list = []  # create a list to store all the booking objects


    if queues is not None:
      for pubid in queues:
        eachqueue = queues[pubid]
        if eachqueue['type'] == 'smag':
            magazine = Magazine(eachbooking['title'], eachbooking['publisher'], eachbooking['status'],
                                eachbooking['created_by'], eachbooking['category'], eachbooking['type'],
                                eachbooking['frequency'])
            magazine.set_pubid(pubid)
            print(magazine.get_pubid())
            list.append(magazine)
        else:
            queue = Queue(eachqueue['title'], eachqueue['publisher'], eachqueue['status'],
                        eachqueue['created_by'], eachqueue['category'], eachqueue['type'],
                        eachqueue['synopsis'], eachqueue['author'], eachqueue['isbn'],eachqueue['patient_status'])
            queue.set_pubid(pubid)
            list.append(queue)
    return render_template('Monitoring.html',queues=list)


@app.route('/ClinicQueue')
def clinicq():
    return render_template('ClinicQueue page.html')

@app.route('/Clinic Queue - YishunPolyClinic.html')
def buddhist():
    queues = root.child('queues').get()
    list = []  # create a list to store all the booking objects


    if queues is not None:
      for pubid in queues:
        eachqueue = queues[pubid]
        if eachqueue['type'] == 'smag':
            magazine = Magazine(eachbooking['title'], eachbooking['publisher'], eachbooking['status'],
                                eachbooking['created_by'], eachbooking['category'], eachbooking['type'],
                                eachbooking['frequency'])
            magazine.set_pubid(pubid)
            print(magazine.get_pubid())
            list.append(magazine)
        else:
            queue = Queue(eachqueue['title'], eachqueue['publisher'], eachqueue['status'],
                        eachqueue['created_by'], eachqueue['category'], eachqueue['type'],
                        eachqueue['synopsis'], eachqueue['author'], eachqueue['isbn'],eachqueue['patient_status'])
            queue.set_pubid(pubid)
            list.append(queue)
    return render_template('Monitoring.html',queues=list)


@app.route('/Clinic Queue - Parkway Shenton.html')
def parkway():
    return render_template('Clinic Queue - Parkway Shenton.html')

@app.route('/Clinic Queue - Sata Commhealth.html')
def sata():
    return render_template('Clinic Queue - Sata Commhealth.html')

@app.route('/Clinic Queue - Healthway Medical.html')
def healthway():
    return render_template('Clinic Queue - Healthway Medical.html')

@app.route('/Clinic Queue - Raffles Medical.html')
def raffles():
    return render_template('Clinic Queue - Raffles Medical.html')

@app.route('/Clinic Queue - YishunPolyclinic.html')
def acumed():
    return render_template('Clinic Queue - YishunPolyclinic.html')

@app.route('/Clinic Queue - Kinder Clinic.html')
def kinder():
    return render_template('Clinic Queue - Kinder Clinic.html')

@app.route('/Clinic Queue - OneDoctors.html')
def onedoctors():
    return render_template('Clinic Queue - OneDoctors.html')

@app.route('/Clinic Queue - My Family Clinic.html')
def family():
    return render_template('Clinic Queue - My Family Clinic.html')

@app.route('/deletemonitoringbooking/<string:id>', methods=['POST','GET'])
def deletemonitoringbooking(id):
    book_db = root.child('bookings/' + id)
    book_db.delete()
    flash('booking Deleted', 'success')

    return redirect(url_for('viewbookings'))


@app.route('/main')
def main():
    tips = root.child('healthtips').get()
    list = []  # create a list to store all the publication objects
    for pubid in tips:
        eachpub = tips[pubid]
        print(eachpub)
        pub = healthtips(eachpub['title'], eachpub['description'])
        pub.set_pubid(pubid)
        print(pub.get_pubid())
        list.append(pub)
    rndmsg = random.choice(list)
    print(rndmsg.get_title())
    return render_template('home.html', rndmsg=rndmsg)

@app.route('/doctormain', methods=['GET', 'POST'])
def docmain():
    return render_template('dochome.html')

@app.route('/')
def loggedin():
    return render_template('home2.html')


@app.route('/viewbookings', methods=['GET', 'POST'])
def viewbookings():
    bookings = root.child('bookings').get()
    list = []  # create a list to store all the booking objects
    form = bookingForm(request.form)
    if bookings is not None:
     for pubid in bookings:
        eachbooking = bookings[pubid]

        if eachbooking['type'] == 'smag':
            magazine = Magazine(eachbooking['title'], eachbooking['publisher'], eachbooking['status'],
                                eachbooking['created_by'], eachbooking['category'], eachbooking['type'],
                                eachbooking['frequency'])
            magazine.set_pubid(pubid)
            print(magazine.get_pubid())
            list.append(magazine)
        else:
            book = Book(eachbooking['title'], eachbooking['publisher'], eachbooking['status'],
                        eachbooking['created_by'], eachbooking['category'], eachbooking['type'],
                        eachbooking['synopsis'], eachbooking['author'], eachbooking['isbn'],
                        eachbooking['patient_status']
                        )
            book.set_pubid(pubid)
            list.append(book)

        if request.method == 'POST' and form.validate():
            if form.pubtype.data == 'smag':
                title = form.title.data
                type = form.pubtype.data
                category = form.category.data
                status = form.status.data
                frequency = form.frequency.data
                publisher = form.publisher.data
                created_by = "U0001"  # hardcoded value

                mag = Magazine(title, publisher, status, created_by, category, type, frequency)

                mag_db = root.child('bookings')
                mag_db.push({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
                })

                flash('Magazine Inserted Sucessfully.', 'success')

            elif form.pubtype.data == 'sbook':
                title = form.title.data
                type = form.pubtype.data
                category = form.category.data
                status = form.status.data
                isbn = form.isbn.data
                author = form.author.data
                synopsis = form.synopsis.data
                publisher = form.publisher.data
                created_by = "U0001"  # hardcoded value
                patient_status = form.patient_status.data
                book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn,patient_status)
                book_db = root.child('queues')
                book_db.push({
                    'title': book.get_title(),
                    'type': book.get_type(),
                    'category': book.get_category(),
                    'status': book.get_status(),
                    'author': book.get_author(),
                    'publisher': book.get_publisher(),
                    'isbn': book.get_isbnno(),
                    'synopsis': book.get_synopsis(),
                    'created_by': book.get_created_by(),
                    'create_date': book.get_created_date(),
                    'patient_status': book.get_patient_status()
                })

                flash('Appointment Sucessfully Sent.', 'success')

    return render_template('view_all_booking.html', bookings=list, form=form)

class RequiredIf(object):

    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.items():
            if name not in form._fields:
                validators.Optional()(field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data:
                    validators.DataRequired().__call__(form, field)
                else:
                    validators.Optional().__call__(form, field)


class  bookingForm(Form):
    title = StringField('NRIC', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    pubtype = RadioField('Gender', choices=[('sbook', 'Male'), ('smag', 'Female')], default='sbook')
    category = StringField('Email', [validators.DataRequired()],

                           default='')
    publisher = StringField('Name', [
        validators.Length(min=1, max=100),
        validators.DataRequired()])
    status = StringField('Birthday', [validators.DataRequired()])

    isbn = StringField('Choice Of Clinic', [
        validators.Length(min=1, max=100),
        RequiredIf(pubtype='sbook')])
    author = StringField('Drug Allergies', [
        validators.Length(min=1, max=100),
        RequiredIf(pubtype='sbook')])
    synopsis = StringField('Reason for Appointment', [
        RequiredIf(pubtype='sbook')])
    frequency =  StringField('Phone Number', [RequiredIf(pubtype='sbook')],)

    patient_status = StringField('Patient status', [RequiredIf(pubtype='sbook')], )


@app.route('/newbooking', methods=['GET', 'POST'])
def new():
    form = bookingForm(request.form)
    if request.method == 'POST' and form.validate():
        if  form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001" # hardcoded value

            mag = Magazine(title, publisher, status, created_by, category, type, frequency)

            mag_db = root.child('bookings')
            mag_db.push({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Inserted Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value
            patient_status = form.patient_status.data
            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn, patient_status)
            book_db = root.child('bookings')
            book_db.push({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date(),
                'patient_status': book.get_patient_status()
            })

            flash('Appointment Sucessfully Sent.', 'success')




    return render_template('create_booking.html', form=form)

@app.route('/delete_chat/<string:id>', methods=['POST'])
def delete_chat(id):
    pub_db = root.child('publications/' + id)
    pub_db.delete()
    flash('Publication Deleted', 'success')

    return redirect(url_for('viewtips'))


@app.route('/delete_msg/<string:id>', methods=['POST'])
def delete_msg(id):
    msg_db = root.child('chathistory/' + id)
    msg_db.delete()
    flash('Message Deleted', 'success')

    return redirect(url_for('msgs'))


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


@app.route('/motdloggin', methods=['GET', 'POST'])
def logign():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        if email == 'admin' and password == 'P@ssw0rd':  # hardcoded username and password=
            session['logged_in'] = True  # this is to set a session to indicate the user is login into the system.
            session['username'] = email
            return redirect(url_for('viewtips'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('motdlogin.html', form=form)

    return render_template('motdlogin.html', form=form)



@app.route('/cliniclogin', methods=['GET', 'POST'])
def loginclinic():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        if email == 'yishunpoly@gmail.com' and password == '123456':  # hardcoded username and password=
            session['logged_in'] = True  # this is to set a session to indicate the user is login into the system.
            session['username'] = email
            return redirect(url_for('/viewbookings'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('login_clinic.html', form=form)

    return render_template('login_clinic.html', form=form)


@app.route('/doctorlogin', methods=['GET', 'POST'])
def logindoctor():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        if email == 'doctor@gmail.com' and password == '123456':  # hardcoded username and password=
            session['logged_in'] = True  # this is to set a session to indicate the user is login into the system.
            session['username'] = email
            return redirect(url_for('/doctormain'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('login_doctor.html', form=form)

    return render_template('login_doctor.html', form=form)

@app.route('/adminlogin', methods=['GET', 'POST'])
def loginadmin():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        if email == 'admin@gmail.com' and password == '123456':  # hardcoded username and password=
            session['logged_in'] = True  # this is to set a session to indicate the user is login into the system.
            session['username'] = email
            return redirect(url_for('/adminhome'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('login_admin.html', form=form)

    return render_template('login_admin.html', form=form)


@app.route('/update/<string:id>/', methods=['GET', 'POST'])
def update_booking(id):
    form = bookingForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value
            mag = Magazine(title, publisher, status, created_by, category, type, frequency)
            # create the magazine object
            mag_db = root.child('bookings/' + id)
            mag_db.set({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Updated Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value
            patient_status = form.patient_status

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn,patient_status)
            mag_db = root.child('bookings/' + id)
            mag_db.set({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })
        else:
            url = 'bookings/' + id
            eachpub = root.child(url).get()

            if eachpub['type'] == 'smag':
                magazine = Magazine(eachpub['title'], eachpub['publisher'], eachpub['status'], eachpub['created_by'],
                                    eachpub['category'], eachpub['type'], eachpub['frequency'])

                magazine.set_pubid(id)
                form.title.data = magazine.get_title()
                form.pubtype.data = magazine.get_type()
                form.category.data = magazine.get_category()
                form.publisher.data = magazine.get_publisher()
                form.status.data = magazine.get_status()
                form.frequency.data = magazine.get_frequency()
            elif eachpub['type'] == 'sbook':
                book = Book(eachpub['title'], eachpub['publisher'], eachpub['status'], eachpub['created_by'],
                            eachpub['category'], eachpub['type'],
                            eachpub['synopsis'], eachpub['author'], eachpub['isbn'],eachpub['patient_status'])
                book.set_pubid(id)
                form.title.data = book.get_title()
                form.pubtype.data = book.get_type()
                form.category.data = book.get_category()
                form.publisher.data = book.get_publisher()
                form.status.data = book.get_status()
                form.synopsis.data = book.get_synopsis()
                form.author.data = book.get_author()
                form.isbn.data = book.get_isbnno()
                form.patient_status.data = book.get_patient_status()

            return render_template('update_publication.html', form=form)

    flash('Book Updated Successfully.', 'success')

    return redirect(url_for('viewbookings'))


@app.route('/update/<string:id>/', methods=['GET', 'POST'])
def update_monitoring(id):
    form = MonitoringForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value
            mag = Magazine(title, publisher, status, created_by, category, type, frequency)
            # create the magazine object
            mag_db = root.child('bookings/' + id)
            mag_db.set({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Updated Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data

            created_by = "U0001"  # hardcoded value

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn,)
            mag_db = root.child('bookings/' + id)
            mag_db.set({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })
        else:
            url = 'bookings/' + id
            eachpub = root.child(url).get()

            if eachpub['type'] == 'smag':
                magazine = Magazine(eachpub['title'], eachpub['publisher'], eachpub['status'], eachpub['created_by'],
                                    eachpub['category'], eachpub['type'], eachpub['frequency'])

                magazine.set_pubid(id)
                form.title.data = magazine.get_title()
                form.pubtype.data = magazine.get_type()
                form.category.data = magazine.get_category()
                form.publisher.data = magazine.get_publisher()
                form.status.data = magazine.get_status()
                form.frequency.data = magazine.get_frequency()
            elif eachpub['type'] == 'sbook':
                book = Book(eachpub['title'], eachpub['publisher'], eachpub['status'], eachpub['created_by'],
                            eachpub['category'], eachpub['type'],
                            eachpub['synopsis'], eachpub['author'], eachpub['isbn'],)
                book.set_pubid(id)
                form.title.data = book.get_title()
                form.pubtype.data = book.get_type()
                form.category.data = book.get_category()
                form.publisher.data = book.get_publisher()
                form.status.data = book.get_status()
                form.synopsis.data = book.get_synopsis()
                form.author.data = book.get_author()
                form.isbn.data = book.get_isbnno()

                flash('Book Updated Successfully.', 'success')
                redirect(url_for('monitor'))

            return render_template('update_monitoring.html', form=form)

@app.route('/viewchat', methods=['GET', 'POST'])
def viewchat():
    form = SendMessage(request.form)
    if request.method == 'POST' and form.validate():
        username = session['username']
        print(username)
        chatnumber = 1
        message = form.message.data
        chatnumber = datetime.time(datetime.now())
        chatnumber = str(chatnumber)
        msg = Chat(message, 'Doctor', chatnumber)
        chatno = str(chatnumber)
        msg_db = root.child('chathistory' + username)
        print(username)
        msg_db.push({
            'message': msg.get_message(),
            'username': msg.get_username(),
            'chatnumber': msg.get_chatnumber()

        })

    print(id)
    username = request.args.get('id')
    print(username)
    timenow = datetime.time(datetime.now())
    chathist = root.child('chathistory' + username).get()
    list = []
    if chathist is not None:
        for chatid in chathist:
            eachmsg = chathist[chatid]
            msg = Chat(eachmsg['message'], eachmsg['username'], eachmsg['chatnumber'])
            msg.set_chatid(chatid)
            list.append(msg)
        print(chathist)

    return render_template('viewchat.html', form=form, chathist=list, username=username, timenow=timenow)



@app.route('/createmonitoring', methods=['GET', 'POST'])
def createmonitoring():
    form = MonitoringForm(request.form)
    if request.method == 'POST' and form.validate():
        if  form.pubtype.data == 'smag':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            frequency = form.frequency.data
            publisher = form.publisher.data
            created_by = "U0001" # hardcoded value

            mag = Magazine(title, publisher, status, created_by, category, type, frequency)

            mag_db = root.child('bookings')
            mag_db.push({
                    'title': mag.get_title(),
                    'type': mag.get_type(),
                    'category': mag.get_category(),
                    'status': mag.get_status(),
                    'frequency': mag.get_frequency(),
                    'publisher': mag.get_publisher(),
                    'created_by': mag.get_created_by(),
                    'create_date': mag.get_created_date()
            })

            flash('Magazine Inserted Sucessfully.', 'success')

        elif form.pubtype.data == 'sbook':
            title = form.title.data
            type = form.pubtype.data
            category = form.category.data
            status = form.status.data
            isbn = form.isbn.data
            author = form.author.data
            synopsis = form.synopsis.data
            publisher = form.publisher.data
            created_by = "U0001"  # hardcoded value

            book = Book(title, publisher, status, created_by, category, type, synopsis, author, isbn)
            book_db = root.child('bookings')
            book_db.push({
                'title': book.get_title(),
                'type': book.get_type(),
                'category': book.get_category(),
                'status': book.get_status(),
                'author': book.get_author(),
                'publisher': book.get_publisher(),
                'isbn': book.get_isbnno(),
                'synopsis': book.get_synopsis(),
                'created_by': book.get_created_by(),
                'create_date': book.get_created_date()
            })

            flash('Appointment Sucessfully Sent.', 'success')
            redirect(url_for('monitor'))

    return render_template('createmonitoring.html', form=form)



@app.route('/delete_booking/<string:id>', methods=['POST','GET'])
def delete_booking(id):
    book_db = root.child('bookings/' + id)
    book_db.delete()
    flash('booking Deleted', 'success')

    return redirect(url_for('viewbookings'))




























@app.route('/viewclinic')
def viewclinic():
    clinics = root.child('clinics').get()
    countNorth = 0
    countCentral = 0
    countEast = 0
    countWest = 0
    cliniclist = []  # create a list to store all the publication objects
    for clinicid in clinics:
        eachclinic = root.child('clinics/'+clinicid).get() #or eachpublication = publications[pubid]
        print(eachclinic)
        clinic = Clinic(eachclinic['title'],eachclinic['address'],eachclinic['phone'],
                            eachclinic['openingHour'],eachclinic['busNo'],eachclinic['mrtStation'],
                            eachclinic['hospital'],eachclinic['created_by'],eachclinic['rating'],
                            eachclinic['region'],eachclinic['photo'],eachclinic['created_date'])
        clinic.set_clinicid(clinicid)

        cliniclist.append(clinic)
        if clinic.get_region()=='North':
            countNorth += 1
        elif clinic.get_region()=='Central':
            countCentral += 1
        elif clinic.get_region()=='East':
            countEast += 1
        elif clinic.get_region()=='West':
            countWest += 1

    return render_template('viewclinic.html', clinics=cliniclist,countNorth = countNorth,countCentral=countCentral,countEast=countEast,countWest=countWest)


@app.route('/viewdisease')
def viewdisease():
    diseases = root.child('diseases').get()
    diseaselist = []  # create a list to store all the publication objects
    for diseaseid in diseases:
        eachdisease = root.child('diseases/'+diseaseid).get() #or eachpublication = publications[pubid]
        print(eachdisease)
        disease = Disease(eachdisease['title'],  eachdisease['cause'],
                          eachdisease['symptom'],
                          eachdisease['treatment'],
                          eachdisease['complication'], eachdisease['detail'],
                          eachdisease['created_by'],eachdisease['created_date'])
        disease.set_diseaseid(diseaseid)

        diseaselist.append(disease)

    return render_template('viewdisease.html', diseases=diseaselist)




class ClinicForm(FlaskForm):
    title = StringField('Name', [
        validators.Length(min=1, max=150,message='Sorry!, Please Enter A Valid Clinic Name!')])

    address = StringField('Address', [validators.Length(min=1, max=100,message='Sorry! Please Enter A Valid Address!')])
    phone = StringField('Phone No', [validators.Length(min=1, max=100,message='Sorry! Please Enter A Valid Phone No!' )])

    openingHour = StringField('Opening hours', [validators.Length(min=1, max=100,message='Sorry! Please Add Timing Of Clinic!')])
    busNo = StringField('Bus No', [validators.Length(min=1, max=100,message='Sorry! Please Add A Bus No!')])
    mrtStation = StringField('Nearest mrt', [validators.Length(min=1, max=100,message='Sorry! Please Add A MRT!' )])
    hospital = StringField('Nearest hospitals', [validators.Length(min=1, max=100,message='Sorry! Please Add A hospital!') ])
    rating = IntegerField('Rating of clinic(1 to 5)',(validators.InputRequired(),validators.NumberRange(min=1,max=5,message='Sorry! Rating of clinic must be between 1 to 5')))
    region = SelectField('Region',
        choices=[('North','North') , ('Central','Central'), ('East','East'),('West','West')] )
    photo = FileField('Enter image of clinic',validators=[FileRequired(),FileAllowed(photos, u'Sorry! Image only!')])



class DiseaseForm(Form):
    title = StringField('Name', [
        validators.Length(min=1, max=100,message='Sorry! Please Enter Disease Name!')])
    cause = StringField('Causes', [
        validators.Length(min=1, max=10000,message='Sorry! Please enter causes of this disease!')])
    symptom = StringField('Symptoms', [
        validators.Length(min=1, max=10000,message='Sorry! Please enter symptoms of this disease!')])
    treatment = StringField('Treatments', [
        validators.Length(min=1, max=10000,message='Sorry! Please enter treatment for this disease!')])
    complication = StringField('Complications', [
        validators.Length(min=1, max=10000,message='Sorry! Please enter complication for this disease!')])
    detail = StringField('What is this disease about?', [
        validators.Length(min=1, max=10000,message='Sorry! Please enter details about this disease!')])



@app.route('/createclinic',methods=['GET','POST'])
def upload_clinic():
    clinicform = ClinicForm() #(request.form)
    if clinicform.validate_on_submit(): #form.validate()
        title = clinicform.title.data
        address = clinicform.address.data
        phone = clinicform.phone.data
        openingHour = clinicform.openingHour.data
        busNo = clinicform.busNo.data
        mrtStation = clinicform.mrtStation.data
        hospital = clinicform.hospital.data
        rating = clinicform.rating.data
        region = clinicform.region.data
        filename = photos.save(clinicform.photo.data)
        file_url = photos.url(filename)
        created_by = "Admin"
        currentdatetime = datetime.datetime.now()
        created_date = str(currentdatetime.day) + "-" + str(currentdatetime.month) + "-" + str(
            currentdatetime.year)
        #mag = Magazine(title, publisher, status, created_by, category, type, frequency)
        cli = Clinic(title, address, phone, openingHour, busNo, mrtStation, hospital, created_by, rating, region,
                     filename,created_date)
        cli_db = root.child('clinics')
        cli_db.push({
                'title': cli.get_title(),
                'address': cli.get_address(),
                'phone': cli.get_phone(),
                'openingHour': cli.get_openingHour(),
                'busNo': cli.get_busNo(),
                'mrtStation': cli.get_mrtStation(),
                'hospital': cli.get_hospital(),
                'rating': cli.get_rating(),
                'region': cli.get_region(),
                'photo': cli.get_photo(),
                'created_by': cli.get_created_by(),
                'created_date': cli.get_created_date()
            })
        flash('Creation of clinic successful!', 'success')


        return redirect(url_for('viewclinic'))


    return render_template('createclinic.html',clinicform=clinicform)


@app.route('/createdisease',methods=['GET','POST'])
def createdisease():
    diseaseform = DiseaseForm(request.form) #(request.form)
    if request.method =='POST' and diseaseform.validate():
        title = diseaseform.title.data
        cause = diseaseform.cause.data
        symptom = diseaseform.symptom.data
        treatment = diseaseform.treatment.data
        complication = diseaseform.complication.data
        detail = diseaseform.detail.data
        created_by = "Admin"  # hardcoded value
        currentdatetime = datetime.datetime.now()
        created_date = str(currentdatetime.day) + "-" + str(currentdatetime.month) + "-" + str(
            currentdatetime.year)
        #mag = Magazine(title, publisher, status, created_by, category, type, frequency)
        dis = Disease(title, cause, symptom, treatment, complication, detail, created_by , created_date)
        dis_db = root.child('diseases')
        dis_db.push({
            'title': dis.get_title(),
            'cause': dis.get_cause(),
            'symptom': dis.get_symptom(),
            'treatment': dis.get_treatment(),
            'complication': dis.get_complication(),
            'detail': dis.get_detail(),
            'created_by': dis.get_created_by(),
            'created_date': dis.get_created_date()
        })

        flash('Creation of disease successful!', 'success')

        return redirect(url_for('viewdisease'))

    return render_template('createdisease.html',diseaseform=diseaseform)


@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory("static/images", filename)

@app.route('/update_clinic/<string:id>/', methods=['GET', 'POST'])
def update_clinic(id):
    clinicform = ClinicForm()
    if clinicform.validate_on_submit():
        title = clinicform.title.data
        address = clinicform.address.data
        phone = clinicform.phone.data
        openingHour = clinicform.openingHour.data
        busNo = clinicform.busNo.data
        mrtStation = clinicform.mrtStation.data
        hospital = clinicform.hospital.data
        rating = clinicform.rating.data
        region = clinicform.region.data
        filename = photos.save(clinicform.photo.data)
        file_url = photos.url(filename)
        created_by = "Admin"
        currentdatetime = datetime.datetime.now()
        created_date = str(currentdatetime.day) + "-" + str(currentdatetime.month) + "-" + str(
            currentdatetime.year)
        #             cli = Clinic(title,type,address,phone,openingHour,busNo,mrtStation,hospital,created_by,areaName,region,photo)
            # create the clinic object
        #             cli_db = root.child('publications/'+ id )
        cli = Clinic(title, address, phone, openingHour, busNo, mrtStation, hospital, created_by, rating,
                     region,filename,created_date)
        cli_db = root.child('clinics/'+id)
        cli_db.set({
            'title': cli.get_title(),
            'address': cli.get_address(),
            'phone': cli.get_phone(),
            'openingHour': cli.get_openingHour(),
            'busNo': cli.get_busNo(),
            'mrtStation': cli.get_mrtStation(),
            'hospital': cli.get_hospital(),
            'rating': cli.get_rating(),
            'region': cli.get_region(),
            'photo': cli.get_photo(),
            'created_by': cli.get_created_by(),
            'created_date':cli.get_created_date()
            })

        flash('Clinic Updated Sucessfully.', 'success')

        return redirect(url_for('viewclinic'))

    else:
        url = 'clinics/' + id
        eachcli = root.child(url).get()


        clinic = Clinic(eachcli['title'] , eachcli['address'],eachcli['phone'],
                         eachcli['openingHour'],eachcli['busNo'],eachcli['mrtStation'],eachcli['hospital'],
                            eachcli['created_by'],eachcli['rating'], eachcli['region'],eachcli['photo'],
                        eachcli['created_date'])

        clinic.set_clinicid(id)
        clinicform.title.data = clinic.get_title()
        clinicform.address.data = clinic.get_address()
        clinicform.phone.data = clinic.get_phone()
        clinicform.openingHour.data = clinic.get_openingHour()
        clinicform.busNo.data = clinic.get_busNo()
        clinicform.mrtStation.data = clinic.get_mrtStation()
        clinicform.hospital.data = clinic.get_hospital()
        clinicform.rating.data = clinic.get_rating()
        clinicform.region.data = clinic.get_region()
        clinicform.photo.data = clinic.get_photo()

        return render_template('update_clinic.html', clinicform=clinicform)


@app.route('/update_disease/<string:id>/', methods=['GET', 'POST'])
def update_disease(id):
    diseaseform = DiseaseForm(request.form)
    if request.method =='POST' and diseaseform.validate():
        title = diseaseform.title.data
        # this should be pubtype
        cause = diseaseform.cause.data
        symptom = diseaseform.symptom.data
        treatment = diseaseform.treatment.data
        complication = diseaseform.complication.data
        detail = diseaseform.detail.data
        created_by = "Admin"  # hardcoded value
        currentdatetime = datetime.datetime.now()
        created_date = str(currentdatetime.day) + "-" + str(currentdatetime.month) + "-" + str(
            currentdatetime.year)
        #             cli = Clinic(title,type,address,phone,openingHour,busNo,mrtStation,hospital,created_by,areaName,region,photo)
            # create the clinic object
        #             cli_db = root.child('publications/'+ id )
        dis = Disease(title, cause, symptom, treatment, complication, detail, created_by , created_date)
        dis_db = root.child('diseases/' + id)
        dis_db.set({
            'title': dis.get_title(),
            'cause': dis.get_cause(),
            'symptom': dis.get_symptom(),
            'treatment': dis.get_treatment(),
            'complication': dis.get_complication(),
            'detail': dis.get_detail(),
            'created_by': dis.get_created_by(),
            'created_date': dis.get_created_date()
        })

        flash('Disease Updated Sucessfully.', 'success')

        return redirect(url_for('viewdisease'))

    else:
        url = 'diseases/' + id
        eachdis = root.child(url).get()
        disease = Disease(eachdis['title'], eachdis['cause'], eachdis['symptom'],
                              eachdis['treatment'],
                              eachdis['complication'], eachdis['detail'],
                              eachdis['created_by'],eachdis['created_date'])
        disease.set_diseaseid(id)
        diseaseform.title.data = disease.get_title()
        diseaseform.cause.data = disease.get_cause()
        diseaseform.symptom.data = disease.get_symptom()
        diseaseform.treatment.data = disease.get_treatment()
        diseaseform.complication.data = disease.get_complication()
        diseaseform.detail.data = disease.get_detail()


        return render_template('update_disease.html', diseaseform=diseaseform)

@app.route('/delete_clinic/<string:id>', methods=['POST'])
def delete_clinic(id):
    cli_db = root.child('clinics/' + id)
    cli_db.delete()
    flash('Oh well, clinic is deleted!', 'success')
    return redirect(url_for('viewclinic'))

@app.route('/delete_disease/<string:id>', methods=['POST'])
def delete_disease(id):
    dis_db = root.child('diseases/'+id)
    dis_db.delete()
    flash('Oh well, disease is deleted!','success')
    return redirect(url_for('viewdisease'))



@app.route('/searchdisease')
def searchdisease():
    diseaselist = get_diseases()
    return render_template('searchdisease.html', specific_disease=diseaselist)

def get_clinics(): #get clinic_list from firebase
    clinics = root.child('clinics').get()
    cliniclist = []  # create a list to store all the publication objects

    for clinicid in clinics:

        eachclinic = clinics[clinicid]


        print(eachclinic)
        clinic = Clinic(eachclinic['title'],eachclinic['address'], eachclinic['phone'],
                            eachclinic['openingHour'], eachclinic['busNo'], eachclinic['mrtStation'],
                            eachclinic['hospital'], eachclinic['created_by'], eachclinic['rating'],
                            eachclinic['region'], eachclinic['photo'],eachclinic['created_date'])
        print(eachclinic)
        clinic.set_clinicid(clinicid)
        print(clinic.get_clinicid())
        cliniclist.append(clinic)

    return cliniclist


def get_diseases(): #get clinic_list from firebase
    diseases = root.child('diseases').get()
    diseaselist = []  # create a list to store all the publication objects

    for diseaseid in diseases:

        eachdisease = diseases[diseaseid]


        print(eachdisease)
        disease = Disease(eachdisease['title'], eachdisease['cause'],
                          eachdisease['symptom'],
                          eachdisease['treatment'], eachdisease['complication'],
                          eachdisease['detail'],
                          eachdisease['created_by'],eachdisease['created_date'])
        print(eachdisease)
        disease.set_diseaseid(eachdisease)
        print(disease.get_diseaseid())
        diseaselist.append(disease)

    return diseaselist

def get_clinic(keyword):
    cliniclist = get_clinics()
    specific_clinic = []
    for clinic in cliniclist:
        if clinic.get_title().find(keyword) >= 0:
            specific_clinic.append(clinic)
    return specific_clinic

def get_disease(keyword):
    diseaselist = get_diseases()
    specific_disease = []
    for disease in diseaselist:
        if disease.get_title().find(keyword) >= 0:
            specific_disease.append(disease)
    return specific_disease

def get_region(keyword):
    cliniclist = get_clinics()
    specific_region = []
    for clinic in cliniclist:
        if clinic.get_region().find(keyword) >= 0:
            specific_region.append(clinic)
    return specific_region


@app.route('/clinicinfo/<title>' , methods=['GET','POST'])
def get_clinic(title):
    cliniclist = get_clinics()    #get list of clinics from firebase
    clinicnames = get_clinicnames()  #get list of names of clinics
    print('Hellocliniclist from firebase')
    print(cliniclist)
    specific_clinic = []
    clinic_name = [] # list for clinic
    print('TESTING@@@@')
    for clinic in cliniclist:
        if clinic.get_title().find(title) >= 0:
            specific_clinic.append(clinic)
    display_specific_clinic = specific_clinic
    print(display_specific_clinic)

    print('Hello clinicnames')
    print(clinicnames)
    return render_template('/clinicinfo.html', display_clinic=display_specific_clinic)


@app.route('/searchclinic/<region>' , methods=['GET','POST'])
def searchclinics(region):
    cliniclist = get_clinics()    #get list of clinics from firebase
    clinicnames = get_clinicnames()  #get list of names of clinics
    print('Hellocliniclist from firebase')
    print(cliniclist)
    specific_north = []
    specific_east = []
    clinic_name = [] # list for clinic
    print('TESTING@@@@')
    for clinic in cliniclist:
        if clinic.get_region() == region:
            specific_north.append(clinic)
    display_specific_north = specific_north
    display_specific_east = specific_east
    print(display_specific_north)

    print('Hello clinicnames')
    print(clinicnames)
    print('SPECIFIC NORTH BELOW')
    print(specific_north)
    print('SPECIFIC EAST BELOW')
    print(specific_east)

    return render_template('/searchclinics.html', display_north=display_specific_north,display_east=display_specific_east)


@app.route('/diseaseinfo/<title>')
def get_disease(title):
    diseaselist = get_diseases()    #get list of clinics from firebase
    print('below is the diseaselisttttttts')
    print(diseaselist)
    specific_disease = []
    for disease in diseaselist:
        if disease.get_title() == title: # or if diseaes.get_title.find(title)>=0:
            specific_disease.append(disease)
    display_specific_disease = specific_disease
    print('below is teh list of specific one disease!')
    print(display_specific_disease)
    print(specific_disease)

    return render_template('/diseaseinfo.html', display_disease=display_specific_disease)

def get_clinicnames(): #get list of names of the clinics
    cliniclist = get_clinics()
    clinicnames = []  # create a list to store all the clinicnames objects
    for clinic in cliniclist:
        clinicnames.append(clinic.get_title())
    return clinicnames





@app.route('/searchclinic')
def searchclinic():
    cliniclist = get_clinics()
    countEast = 0
    countWest = 0
    countNorth = 0
    countCentral = 0
    for clinic in cliniclist:
        if clinic.get_region()=='East':
            countEast +=1
        elif clinic.get_region()=='West':
            countWest +=1
        elif clinic.get_region()=='North':
            countNorth +=1
        elif clinic.get_region()=='Central':
            countCentral +=1
    return render_template('searchclinic.html',specific_clinic=cliniclist,countEast=countEast,countWest=countWest,countNorth=countNorth,countCentral=countCentral)


@app.route('/clinichome')
def clinichome():
    cliniclist = get_clinics()
    diseaselist = get_diseases()
    print('clinichomeee')
    print(cliniclist)
    countclinic = len(cliniclist)
    print(countclinic)
    countdisease = len(diseaselist)
    print(countdisease)


    newinfo = root.child('newinfo').get()
    countarticles = len(newinfo)
    print(countarticles)
    tips = root.child('healthtips').get()
    counttips = len(tips)
    print(counttips)

    totalcount = countclinic + countdisease + countarticles + counttips

    clinicpercent = '{0:.1f}'.format((countclinic / totalcount * 100))

    diseasepercent = '{0:.1f}'.format((countdisease / totalcount * 100))

    articlepercent = '{0:.1f}'.format((countarticles / totalcount * 100))

    tippercent = '{0:.1f}'.format((counttips / totalcount * 100))
    print(totalcount)

    return render_template('clinichome.html', countclinic=countclinic,countdisease=countdisease,countarticles=countarticles,counttips=counttips
                           ,clinicpercent=clinicpercent,diseasepercent=diseasepercent,articlepercent=articlepercent,tippercent=tippercent)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(port='80')


