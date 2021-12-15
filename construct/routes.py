from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from construct.models import User, Delay
from construct import app
from construct.forms import RegisterForm, LoginForm, PurchaseItemForm
from construct import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
@login_required
def homepage():
    return render_template('home.html')

@app.route("/delays", methods=['GET', 'POST'])
@login_required
def delaypage():

    delays = Delay.query.all()

 #   purchase_form = PurchaseItemForm()
  #  if request.method == "POST":
  #      purchased_item = request.form.get('purchased_item')
  #      purch_item_obj = Item.query.filter_by(name=purchased_item).first()
#
#        if purch_item_obj:
#            if current_user.can_purchase(purch_item_obj):
#                purch_item_obj.buy(current_user.id)
#              #  purch_item_obj.owner = current_user.id
#                current_user.update_budget(purch_item_obj.price)
#
#                flash(
#                    f'You have purchased the {purch_item_obj.name} for {purch_item_obj.price}')
#            else:
#                flash(
#                    f'you dont have enough money. Piss off')

 #       return render_template('delays.html', delays=delays)

    if request.method == "GET":
        

        return render_template('delays.html', delays=delays)






   


























#@app.route('/construct', methods=['GET', 'POST'])
#@login_required
#def constructpage():
#    items = Item.query.filter_by(owner=None)
#    owned_items = Item.query.filter_by(owner=current_user.id)
#    purchase_form = PurchaseItemForm()
###    if request.method == "POST":
#        purchased_item = request.form.get('purchased_item')
#        purch_item_obj = Item.query.filter_by(name=purchased_item).first()
#
#        if purch_item_obj:
#            if current_user.can_purchase(purch_item_obj):
#                purch_item_obj.buy(current_user.id)
#              #  purch_item_obj.owner = current_user.id
#                current_user.update_budget(purch_item_obj.price)
#
#                flash(
#                    f'You have purchased the {purch_item_obj.name} for {purch_item_obj.price}')
#            else:
#                flash(
#                    f'you dont have enough money. Piss off')
#
#        return render_template('construct.html', items=items, purchase_form=purchase_form, owned_items=owned_items)
#
#    if request.method == "GET":
#        owned_items = Item.query.filter_by(owner=current_user.id).first()
#
#        return render_template('construct.html', items=items, purchase_form=purchase_form, owned_items=owned_items)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)

        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}:  # if the errors in the form error dictionary is not empty
        for err_msg in form.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(
            username=form.username.data).first()
        attempted_password = form.login_password.data
        if attempted_user and attempted_user.check_password_correction(
                attempted_password):
            login_user(attempted_user)
            flash(
                f'You have Successully logged in as {attempted_user.username}', category='success')
            return redirect(url_for('homepage'))
        else:
            flash(f'Wrong Credentials. Re-enter the correct stuff',
                  category='danger')

    return render_template('loginpage.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash("you have been logged out")
    return redirect(url_for('homepage'))
