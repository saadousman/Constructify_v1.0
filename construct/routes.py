from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, make_response, jsonify, Response
from construct.models import User, Delay, Tasks, Contact_list, Img, TaskToImage
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
UPLOAD_FOLDER = 'construct/static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
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
            send_sms("A Task was Updated. Please Check your email man")
            SendNotificationAsContractor("Task Record")
            flash(f'Task Created!')
           

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
    #SendNotificationAsContractor("Task Item Deletion")
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




@app.route("/Contacts", methods=['GET'])
@login_required
def Contactspage():

    Users= User.query.all()
        
    return render_template('contact_list.html', Users=Users)

   


@app.route("/PdfGeneration", methods=['GET', 'POST'])
@login_required
def PDFPage():

    #Query DB for objects to pass to table and cards
    delays = Delay.query.all()
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    today = date.today()
    # Render the HTML page with the passed information. This will be converted into a PDF
    rendered= render_template('pdf.html', pending_delays=pending_delays,approved_delays=approved_delays, delay_count=delay_count, today=today, delays=delays)

    #Converts the saved HTML as a pdf document. Saved in memory
    pdf = pdfkit.from_string(rendered, False)
    #Builds the response with the pdf attached in the response content
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

    
    
    #send_sms()calls the send_sms function to send an sms to stakeholders. Message body is passed as a parameter
    #SendDelayReport() calls the imported function to send an email notification to the stakeholders with the attached pdf that is generated
    SendDelayReport()
    send_sms("Delay Report was printed. Please Check your email man")
           


    return redirect('/delays', code=302)


def saveimage(taskid,imagename):
        image_to_save = TaskToImage(task_id=taskid,img_name=imagename)
        db.session.add(image_to_save)
        db.session.commit()
        print("saved db record")
        print("image id is "+taskid)
        print("image name is " +imagename)


@app.route('/UploadImage', methods=['POST'])
def upload_image():

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        taskID= request.form['tasks']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash('The image has been  successfully uploaded ')
        
        saveimage(taskID, filename)
        
        return redirect('/Tasks', code=302)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)







@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/imguploadpage')
def imagepage():
    return render_template('UploadImage.html')
   
@app.route("/ImageGallery/<int:id>", methods=['GET', 'POST'])

def ImageGallery(id):
        tasks= TaskToImage.query.all()
        
        print(tasks)
        ident=str(id)
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ImageGallery.html', taskref=tasks, taskid=ident)


@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)