from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from construct.models import User, Delay, Tasks
from construct import app
from construct.forms import RegisterForm, LoginForm,  DelayForm, TaskForm
from construct import db
from flask_login import login_user, logout_user, login_required, current_user
import time

#Deleting Delays
@app.route("/deletedelay/<int:id>")
def delete(id):
    delay_to_delete = Delay.query.get_or_404(id)
    

    db.session.delete(delay_to_delete)
    db.session.commit()
    time.sleep(1)
    return redirect(url_for('delaypage'))
    time.sleep(3)
    
    flash(f'record deleted!')



#Approving EOT's
@app.route("/approveeot/<int:id>")
def approveEOT(id):
    eot_to_approve = Delay.query.get_or_404(id)
    eot_to_approve.status = "Approved"
    

   
    db.session.commit()
    time.sleep(1)
    return redirect(url_for('delaypage'))
    flash(f'EOT Approved!')



#homepage route
@app.route("/")
@app.route("/home")
@login_required
def homepage():
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    return render_template('home.html', pending_delays=pending_delays, approved_delays=approved_delays, delay_count=delay_count)


#page to display Submmited EOTS
@app.route("/eotrecords")
@login_required
def eotrecord():
    return render_template('EOTRecords.html')

#page to display Approved EOTS
@app.route("/eotapprovals")
@login_required
def eotapprovals():
    return render_template('EOTApproved.html')


#Path to the Delays Module
@app.route("/delays", methods=['GET', 'POST'])
@login_required
def delaypage():
    #Query DB for objects to pass to table and cards
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    delayForm = DelayForm()
    delays = Delay.query.all()
    
    if request.method == "GET":
        return render_template('delays.html', delays=delays, delayForm=delayForm, pending_delays=pending_delays, approved_delays=approved_delays, delay_count=delay_count)

    if request.method == "POST":

#Creating new Delays
            delay_to_create = Delay(type=delayForm.type.data,
                              description=delayForm.description.data,
                              severity=delayForm.severity.data,
                              phase=delayForm.phase.data,
                              delayed_days=delayForm.extended_days.data,
                              date= delayForm.date.data)
            db.session.add(delay_to_create)
            db.session.commit()
            flash(f'Delay Record Created!')                

    return redirect(url_for('delaypage'))

# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in delayForm.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')






#Path to the Tasks Module
@app.route("/Tasks", methods=['GET', 'POST'])
@login_required
def Taskpage():
    #Query DB for objects to pass to table and cards
    taskform = TaskForm()
    
    tasks = Tasks.query.all()
    
    if request.method == "GET":
        return render_template('Tasks.html', tasks=tasks, taskform=taskform)

    if request.method == "POST":

#Creating new Delays
            task_to_create = Tasks(Name=taskform.Name.data,
                              description=taskform.Description.data,
                              phase=taskform.phase.data,
                              Percentage=taskform.percentage.data,
                              start_date= taskform.start_date.data,
                              end_date= taskform.end_date.data,
                              total_estimated_cost= taskform.total_estimated_cost.data,)
            db.session.add(task_to_create)
            db.session.commit()
            flash(f'Task Created!')                

    return redirect(url_for('Taskpage'))

# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in delayForm.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')





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