from flask import Flask, render_template, request, flash, redirect, url_for, session
from pubmotd import booking
from chat import Chat
import firebase_admin
from firebase_admin import credentials, db
from wtforms import Form, StringField, TextAreaField, RadioField, SelectField, validators, PasswordField
import random



app = Flask(__name__)


@app.route('/home')
def home():
    return render_template('motdhome.html')


@app.route('/motdpage')
def motd():
    bookings = root.child('bookings').get()
    list = []  # create a list to store all the booking objects
    for pubid in bookings:
        eachpub = bookings[pubid]
        print(eachpub)
        pub = booking(eachpub['title'], eachpub['description'])
        pub.set_pubid(pubid)
        print(pub.get_pubid())
        list.append(pub)
    rndmsg = random.choice(list)
    print(rndmsg.get_title())

    return render_template('MOTD.html', rndmsg=rndmsg)

@app.route('/viewbookings')
def viewbookings():
    bookings = root.child('bookings').get()
    list = []  # create a list to store all the booking objects
    for pubid in bookings:
        eachpub = bookings[pubid]
        print(eachpub)
        pub = booking(eachpub['title'], eachpub['description'])
        pub.set_pubid(pubid)
        print(pub.get_pubid())
        list.append(pub)
    print(list)
    return render_template('view_all_motd.html', bookings=list)


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


class SendMessage(Form):
    message = TextAreaField('Message', [
        validators.Length(min=1),
        validators.DataRequired()
    ])


@app.route('/chatroom', methods=['GET', 'POST'])
def msgs():
    form = SendMessage(request.form)
    if request.method == 'POST' and form.validate():
        message = form.message.data
        msg = Chat(message)
        msg_db = root.child('chathistory')
        msg_db.push({
            'message': msg.get_message()
        })

        flash('Message Sent', 'success')

    chathist = root.child('chathistory').get()
    list = []
    for chatid in chathist:
        eachmsg = chathist[chatid]
        print(eachmsg)
        msg = Chat(eachmsg['message'])
        msg.set_chatid(chatid)
        print(msg.get_chatid())
        list.append(msg)
    print(list)
    print(chathist)

    return render_template('chat.html', form=form, chathist=list)

# @app.route('/viewbookings')
# def viewbookings():
#     bookings = root.child('bookings').get()
#     list = []  # create a list to store all the booking objects
#     for pubid in bookings:
#         eachpub = bookings[pubid]
#         print(eachpub)
#         pub = booking(eachpub['title'], eachpub['description'])
#         pub.set_pubid(pubid)
#         print(pub.get_pubid())
#         list.append(pub)
#     print(list)
#     return render_template('view_all_motd.html', bookings=list)


class bookingForm(Form):
    title = StringField('Title', [
        validators.Length(min=1, max=150),
        validators.DataRequired()])
    description = TextAreaField('Description')


@app.route('/newbooking', methods=['GET', 'POST'])
def new():
    form = bookingForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        pub = booking(title, description)
        pub_db = root.child('bookings')
        pub_db.push({
            'title': pub.get_title(),
            'description': pub.get_description()
        })

        flash('Message Inserted Successfully.', 'success')

        return redirect(url_for('viewbookings'))

    return render_template('create_motd.html', form=form)


@app.route('/update/<string:id>/', methods=['GET', 'POST'])
def update_booking(id):
    form = bookingForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        pub = booking(title, description)

        pub_db = root.child('bookings/' + id)
        pub_db.set({
            'title': pub.get_title(),
            'description': pub.get_description()
            })

        flash('Magazine Updated Sucessfully.', 'success')

        return redirect(url_for('viewbookings'))
    else:
        url = 'bookings/' + id
        eachpub = root.child(url).get()
        pub = booking(eachpub['title'], eachpub['description'])
        pub.set_pubid(id)

        return render_template('update_motd.html', form=form)


@app.route('/delete_booking/<string:id>', methods=['POST'])
def delete_booking(id):
    pub_db = root.child('bookings/' + id)
    pub_db.delete()
    flash('booking Deleted', 'success')

    return redirect(url_for('viewbookings'))


@app.route('/delete_msg/<string:id>', methods=['POST'])
def delete_msg(id):
    msg_db = root.child('chathistory/' + id)
    msg_db.delete()
    flash('Message Deleted', 'success')

    return redirect(url_for('msgs'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        if username == 'admin' and password == 'P@ssw0rd':  # harcoded username and password=
            session['logged_in'] = True  # this is to set a session to indicate the user is login into the system.
            return redirect(url_for('viewbookings'))
        else:
            error = 'Invalid login'
            flash(error, 'danger')
            return render_template('motdlogin.html', form=form)

    return render_template('motdlogin.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


if __name__ == '__main__':
    app.secret_key = 'sekret123'
    app.run()

