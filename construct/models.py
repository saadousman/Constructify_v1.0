from construct import db, login_manager
from construct import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50),
                              nullable=False, unique=True)
    password_hash = db.Column(db.String(length=50),
                              nullable=False, unique=True)
    role = db.Column(db.String(length=30), nullable=False, unique=False)
    contact_number = db.Column(db.String(length=30), nullable=False, unique=False)
   
     
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_pwd):
        self.password_hash = bcrypt.generate_password_hash(
            plain_text_pwd).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

   

    

#class Item(db.Model):
#    id = db.Column(db.Integer(), nullable=False, primary_key=True)
#    name = db.Column(db.String(length=30), nullable=False, unique=True)
#    price = db.Column(db.Integer(), nullable=False)
#    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
#    description = db.Column(db.String(length=1024),
#                            nullable=False, unique=True)
#    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
#
#    def __repr__(self):
#        return f'Item {self.name}'
#
#    def buy(self, userid):
#        self.owner = userid
#        db.session.commit()
class Delay(db.Model):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    type = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=30), nullable=False)
    severity = db.Column(db.String(length=30), nullable=False)
    phase = db.Column(db.String(length=30), nullable=False)
    delayed_days = db.Column(db.Integer(), nullable=True)
    date = db.Column(db.String(length=30), nullable=False)
    status = db.Column(db.String(length=30), nullable=True, default="Submitted")


class Tasks(db.Model):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    Name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=30), nullable=False)
    phase = db.Column(db.String(length=30), nullable=False)
    Percentage = db.Column(db.Integer(), nullable=False)
    start_date = db.Column(db.String(length=30), nullable=False)
    end_date = db.Column(db.String(length=30), nullable=False)
    status = db.Column(db.String(length=30), nullable=True, default="Pending")
    total_estimated_cost = db.Column(db.String(length=30), nullable=False)
    total_days = db.Column(db.Integer(), nullable=False)
    
class Contact_list(db.Model):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    Role = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=30), nullable=False)
    contact_number = db.Column(db.String(), nullable=False)
    
class Img(db.Model):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    img = db.Column(db.Text, unique=False, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

class TaskToImage(db.Model):
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    img_name = db.Column(db.String(length=30), nullable=False)
    task_id = db.Column(db.String(length=30), nullable=False)
    

    
