from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from django.contrib.auth.decorators import login_required
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(300), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Объявление №{self.id}'


users = {
    "user1": generate_password_hash("zxcvbnbnmm1"),
    "user2": generate_password_hash("zxcvbnbnmm2"),
    "user3": generate_password_hash("zxcvbnbnmm3")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/create-advertisement', methods=['POST', 'GET'])
@auth.login_required
def create_advertisement():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        creator = auth.current_user()

        advertisement = Advertisement(title=title, description=description, creator=creator)

        try:
            db.session.add(advertisement)
            db.session.commit()
            return redirect('/advertisements')
        except:
            return 'При добавлении объявления произошла ошибка'
    else:
        return render_template('create-advertisement.html')


@app.route('/advertisements')
def advertisements():
    advertisements = Advertisement.query.order_by(Advertisement.date.desc()).all()
    return render_template('advertisements.html', advertisements=advertisements)


@app.route('/advertisements/<int:id>')
def advertisements_page(id):
    advertisement = Advertisement.query.get(id)
    return render_template('advertisement_page.html', advertisement=advertisement)


@app.route('/advertisements/<int:id>/delete')
@auth.login_required
def advertisement_delete(id):
    advertisement = Advertisement.query.get_or_404(id)

    if advertisement.creator == auth.current_user():
        try:
            db.session.delete(advertisement)
            db.session.commit()
            return redirect('/advertisements')
        except:
            return 'При удалении объявления произошла ошибка'
    else:
        return 'Удалять может только владелец объявления'


@app.route('/advertisements/<int:id>/update', methods=['GET', 'POST'])
@auth.login_required
def update_advertisement(id):
    advertisement = Advertisement.query.get(id)
    if request.method == 'POST':
        advertisement.title = request.form['title']
        advertisement.description = request.form['description']
        if advertisement.creator == auth.current_user():
            try:
                db.session.commit()
                return redirect('/advertisements')
            except:
                return 'При редактировании объявления произошла ошибка'
        else:
            return 'Редактировать может только владелец объявления'
    else:
        return render_template('update-advertisement.html', advertisement=advertisement)


if __name__ == "__main__":
    app.run(debug=True)
