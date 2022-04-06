from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, make_response, jsonify
from construct.models import User, Delay, Tasks, Contact_list, Img
from construct import app, db, date, timedelta, mail, Message
from construct.forms import RegisterForm, LoginForm,  DelayForm, TaskForm, ContactForm
from construct.email_send import *
from flask_login import login_user, logout_user, login_required, current_user
import time
import plotly.express as px
import pandas as pd
import plotly, json
import pytest
import pdfkit as pdfkit
from werkzeug.utils import secure_filename
import base64
from twilio.rest import Client
import os
import requests
#path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
#config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
#pdfkit.from_url("http://google.com", "out.pdf", configuration=config)


############ The Homepage and Dashboard ####################

#homepage route 
@app.route("/")
@app.route("/home")
@login_required
def homepage():
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
   # assert pending_delays== 3,"test failed"
    tasks = Tasks.query.all()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    pending_tasks= Tasks.query.filter(Tasks.status == "Pending").count()
    completed_tasks= Tasks.query.filter(Tasks.status == "Completed").count()
    inprogress_tasks= Tasks.query.filter(Tasks.status == "In Progress").count()
    delay_count = pending_delays+approved_delays
    data = {'Task' : 'Status', 'Pending' : pending_tasks, 'In Progress' : inprogress_tasks, 'Completed' : completed_tasks}
    
    return render_template('home.html', pending_delays=pending_delays, approved_delays=approved_delays, delay_count=delay_count, inprogress_tasks=inprogress_tasks,completed_tasks=completed_tasks, pending_tasks=pending_tasks, data=data, tasks=tasks)


############ All Functions related to Delays ####################

#Deleting Delays
@app.route("/deletedelay/<int:id>")
def delete(id):
    #pass delay id and remove the row from the DB
    delay_to_delete = Delay.query.get_or_404(id)
    db.session.delete(delay_to_delete)
    db.session.commit()
    #Send Email notification to Clients
    SendNotificationAsContractor("Delay Deletiion")
    flash(f'Record deleted!')
    return redirect(url_for('delaypage'))
    
    

#Approving EOT's
@app.route("/approveeot/<int:id>")
def approveEOT(id):
    eot_to_approve = Delay.query.get_or_404(id)
    eot_to_approve.status = "Approved"
      
    db.session.commit()
    SendNotificationAsClient("EOT Approval")
    return redirect(url_for('delaypage'))
    flash(f'EOT Approved!')

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
    gannt_data = delays
   
   


    if request.method == "GET":
        return render_template('delays.html', delays=delays, delayForm=delayForm, pending_delays=pending_delays, approved_delays=approved_delays, delay_count=delay_count, gannt_data=gannt_data)

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
        #    SendNotificationAsContractor("Delay")
            #flash(f'Delay Record Created!')     
            #flash(f'Email notification sent!')   
            #msg = Message('Project Delay Alert', sender = 'sdousmanflask@gmail.com', recipients = ['sdousman@gmail.com'])
            #msg.body = "A new Delay record was created by the contractor"
            #mail.send(msg)

    return redirect(url_for('delaypage'))
   
# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in delayForm.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')

############ All Functions related to Delay management end here ####################


############ All Functions related to Task management ####################



#Path to the Tasks Module
@app.route("/Tasks", methods=['GET', 'POST'])
@login_required
def Taskpage():
    #Query DB for objects to pass to table and cards
    taskform = TaskForm()
    tasks = Tasks.query.all()
    pending_tasks= Tasks.query.filter(Tasks.status == "Pending").count()
    completed_tasks= Tasks.query.filter(Tasks.status == "Completed").count()
    inprogress_tasks= Tasks.query.filter(Tasks.status == "In Progress").count()
    data = {'Task' : 'Status', 'Pending' : pending_tasks, 'In Progress' : inprogress_tasks, 'Completed' : completed_tasks}
    
    #Render the Task page if the request is of type GET
    if request.method == "GET":
        return render_template('Tasks.html', tasks=tasks, taskform=taskform, inprogress_tasks=inprogress_tasks,completed_tasks=completed_tasks, pending_tasks=pending_tasks, data=data)

    if request.method == "POST":
    #Grab the form values and perform the relevant DB queries if the request is of type POST
#Creating new Tasks
            start_date= taskform.start_date.data      
            end_date= taskform.end_date.data         
            total_days= (end_date-start_date).days  
            

            task_to_create = Tasks(Name=taskform.Name.data,
                              description=taskform.Description.data,
                              phase=taskform.phase.data,
                              Percentage=taskform.percentage.data,
                              start_date= taskform.start_date.data,
                              end_date= taskform.end_date.data,
                              total_estimated_cost= taskform.total_estimated_cost.data,
                              total_days= total_days )
            db.session.add(task_to_create)
            db.session.commit()
            SendNotificationAsContractor("Task Record")
            flash(f'Task Created!')
            #msg = Message('Project Task Update', sender = 'sdousmanflask@gmail.com', recipients = ['sdousman@gmail.com'])
            #msg.body = "A New Project task was updated by the contractor"
            #mail.send(msg)

    return redirect(url_for('Taskpage'))

# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in taskform.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')



#Delete Task Item
@app.route("/deleteTask/<int:id>")
def deleteTask(id):
    task_to_delete = Tasks.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    SendNotificationAsContractor("Task Item Deletion")
    return redirect(url_for('Taskpage'))

    
    flash(f'Task deleted!')

#Mark Task as In Progress
@app.route("/Taskinprogress/<int:id>")
def TaskInProgress(id):
    task_in_progress = Tasks.query.get_or_404(id)
    task_in_progress.status = "In Progress" 
    db.session.commit()
  
    return redirect(url_for('Taskpage'))
    flash(f'Task Updated!')

#Mark Task as Completed
@app.route("/TaskCompleted/<int:id>")
def TaskCompleted(id):
    task_completed = Tasks.query.get_or_404(id)
    task_completed.status = "Completed" 
    db.session.commit()
    SendNotificationAsContractor("Task Completion")
 
    return redirect(url_for('Taskpage'))
    
    flash(f'Task Updated!')

#Mark Task as Pending
@app.route("/TaskPending/<int:id>")
def TaskPending(id):
    task_pending = Tasks.query.get_or_404(id)
    task_pending.status = "Pending" 
    db.session.commit()
 
    return redirect(url_for('Taskpage'))

############ All Functions related to Task management end here ####################


############ All Functions related to Registration and Login ####################

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data,
                              role=form.role.data,
                              contact_number=form.contact_no.data)

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


@app.route("/Contacts", methods=['GET', 'POST'])
@login_required
def Contactspage():
    #contactform= ContactForm()
    #contacts = Contact_list.query.all()

    Users= User.query.all()

    

    if request.method == "GET":
        
        return render_template('contact_list.html', Users=Users)

    if request.method == "POST":
        #Grab the form values and perform the relevant DB queries if the request is of type POST
#Creating new Tasks
           
            

            contact_to_create = Contact_list(name=contactform.name.data,
                              Role=contactform.role.data,
                              email_address=contactform.email_address.data,
                              contact_number=contactform.contact_no.data)
            db.session.add(contact_to_create)
            db.session.commit()
            SendNotification("Contact Creation")
        #    flash(f'Contact Added!')
         #   msg = Message('Project Task Update', sender = 'sdousmanflask@gmail.com', recipients = ['sdousman@gmail.com'])
         #   msg.body = "A New Contact has been added"
         #  mail.send(msg)

    return redirect(url_for('Contactspage'))


@app.route("/PdfGeneration", methods=['GET', 'POST'])
@login_required
def PDFPage():

    #Query DB for objects to pass to table and cards
    delays = Delay.query.all()
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    today = date.today()
    rendered= render_template('pdf.html', pending_delays=pending_delays,approved_delays=approved_delays, delay_count=delay_count, today=today, delays=delays)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=pdfreport.pdf'
    #SendNotificationAsContractor("PDF Report Generation")
    return response

@app.route("/PdfEmail", methods=['GET', 'POST'])
@login_required
def PDFPageEmail():

      #Query DB for objects to pass to table and cards
    
    delayForm = DelayForm()
   
    

    #Query DB for objects to pass to table and cards
    delays = Delay.query.all()
    gannt_data = delays
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    today = date.today()
    #render the html page that will be converted into a pdf
    rendered= render_template('pdf.html', pending_delays=pending_delays,approved_delays=approved_delays, delay_count=delay_count, today=today, delays=delays)
    #generate the pdf and store it in the appropriate directory
    pdf = pdfkit.from_string(rendered, 'construct/newpdf.pdf')

    #call the imported function to send an email notification to the stakeholders with the attached pdf that is generated
    #SendDelayReport()
    Users=User.query.all()
    
    
    for user in Users:
            user_id="15896"
            api_key= "c977qWgaQfGYfZHoXJc1"
            sender_id="NotifyDEMO"
            message="A delay Report has been generated. Check ur fkn email"
         
            request_string="https://app.notify.lk/api/v1/send?"+"user_id="+user_id+"&api_key="+api_key+"&sender_id="+sender_id+"&to="+user.contact_number+"&message="+message
            print(request_string) #Test- to inspect the generated URL
            r = requests.get(request_string)
            
            print(r.text) #Test- to inspect the response from the SMS API
           


    return redirect('/delays', code=302)


@app.route("/UploadPage", methods=['GET', 'POST'])
@login_required
def Uploadpage():
    
    db.create_all()

    return render_template('UploadImage.html')

@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    flash(f'Image Uploaded')
    return redirect('/Tasks', code=302)
   
@app.route("/ImageGallery", methods=['GET', 'POST'])
@login_required
def ImageGallery():
        images = Img.query.all()
        base64_images = [base64.b64encode(image).decode("utf-8") for images.img in images]
        
        return render_template('TaskImagePage.html', images=base64_images)


