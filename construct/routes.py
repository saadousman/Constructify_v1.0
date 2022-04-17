from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, make_response, jsonify, Response, send_from_directory
from construct.models import User, Delay, Tasks,  TaskToImage, WorkInspectionRequests, WIRDocument, MaterialInspectionRequests, MIRDocument, MIRConsultantDocument,WIRConsultantDocument, EOTDocument, EOTConsultantDocument
from construct import app, db, date, timedelta, mail, Message
from construct.forms import RegisterForm, LoginForm,  DelayForm, TaskForm, ContactForm,WIRForm, MIRForm
from construct.email_send import *
from flask_login import login_user, logout_user, login_required, current_user
import time
import pytest
import pdfkit as pdfkit
from werkzeug.utils import secure_filename
import base64
from twilio.rest import Client
import os
import requests, random



UPLOAD_FOLDER = 'construct/static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


############ The Homepage and Dashboard ####################

#homepage route
@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def DashBoard():
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
   # assert pending_delays== 3,"test failed"
    tasks = Tasks.query.all()
    wir_count= len(WorkInspectionRequests.query.all())
    #Pending MIR and WIR
    submitted_wir= WorkInspectionRequests.query.filter(WorkInspectionRequests.status == "Submitted").count()
    submitted_mir= MaterialInspectionRequests.query.filter(WorkInspectionRequests.status == "Submitted").count()
    mir_wir_pending_inspection = submitted_wir+submitted_mir
    #Pending ends
    approved_wir= WorkInspectionRequests.query.filter(WorkInspectionRequests.status == "Approved").count()
    approved_wir_as_noted= WorkInspectionRequests.query.filter(WorkInspectionRequests.status == "Approved-As-Noted").count()
    approved_wir_as_rejected= WorkInspectionRequests.query.filter(WorkInspectionRequests.status == "Rejected").count()
    approved_wir_as_revise= WorkInspectionRequests.query.filter(WorkInspectionRequests.status == "Revise-and-ReSubmit").count()

    mir_count= len(MaterialInspectionRequests.query.all())
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    pending_tasks= Tasks.query.filter(Tasks.status == "Pending").count()
    completed_tasks= Tasks.query.filter(Tasks.status == "Completed").count()
    inprogress_tasks= Tasks.query.filter(Tasks.status == "In Progress").count()
    task_count = pending_tasks + completed_tasks + inprogress_tasks
    delay_count = pending_delays+approved_delays
    data = {'Task' : 'Status', 'Pending' : pending_tasks, 'In Progress' : inprogress_tasks, 'Completed' : completed_tasks}
    page_message="Project Management DashBoard"
    page_name="Dashboard"
    return render_template('index.html', pending_delays=pending_delays,
     approved_delays=approved_delays, delay_count=delay_count, 
     inprogress_tasks=inprogress_tasks,completed_tasks=completed_tasks, 
     pending_tasks=pending_tasks, data=data, tasks=tasks,
     task_count=task_count,mir_wir_pending_inspection=mir_wir_pending_inspection,
     submitted_wir=submitted_wir,submitted_mir=submitted_mir,page_message=page_message,page_name=page_name)



############ All Functions related to Delays ####################

#Deleting Delays
@app.route("/deletedelay/<int:passed_id>")
def deleteDelay(passed_id):
    #pass delay id and remove the row from the DB
    delay_to_delete = Delay.query.get_or_404(passed_id)
    db.session.delete(delay_to_delete)
    db.session.commit()
    #Send Email notification to Clients
    #SendNotificationAsContractor("Delay Deletion")
    flash(f'Record deleted!')
    return redirect(url_for('delaypage'))
    
    
#Path to the Delays Module
@app.route("/delays", methods=['GET', 'POST'])
@login_required
def delaypage():

    #Query DB for objects to pass to table and cards
     #Use the following status types in forms: Submitted,Approved, Approved-As-Noted, Revise-and-ReSubmit, Rejected
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved!").count()
    Approved_As_Noted_delays= Delay.query.filter(Delay.status == "Approved-As-Noted").count()
    ReviseandReSubmit_delays= Delay.query.filter(Delay.status == "Revise-and-ReSubmit").count()
    Rejected_delays= Delay.query.filter(Delay.status == "Rejected").count()
    delayForm = DelayForm()
    delays = Delay.query.all()
    
   
   

    page_message=("Project Delay and EOT Management")
    if request.method == "GET":
        return render_template('DelayManagementpage.html', delays=delays, delayForm=delayForm,pending_delays=pending_delays, 
        approved_delays=approved_delays,Approved_As_Noted_delays=Approved_As_Noted_delays,
        ReviseandReSubmit_delays=ReviseandReSubmit_delays, Rejected_delays=Rejected_delays,page_message=page_message)

   

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
    task_count = pending_tasks + completed_tasks + inprogress_tasks
    page_name= "Tasks"
    page_message="Project Task Management"
    #Render the Task page if the request is of type GET
    if request.method == "GET":
        page_message="Project Task Management"
    
    return render_template('TaskManagementpage.html', tasks=tasks, taskform=taskform, inprogress_tasks=inprogress_tasks,completed_tasks=completed_tasks, pending_tasks=pending_tasks, data=data,page_message=page_message, task_count=task_count,page_name=page_name)

    if request.method == "POST":
    #Grab the form values and perform the relevant DB queries if the request is of type POST

#Creating new Tasks test new gui
            start_date= taskform.start_date.data      
            end_date= taskform.end_date.data         
            total_days= (end_date-start_date).days  
            print(start_date)
            print(end_date)

            task_to_create = Tasks(Name=taskform.Name.data,
                              description=taskform.Description.data,
                              phase=taskform.phase.data,
                              Percentage=taskform.percentage.data,
                              start_date= taskform.start_date.data,
                              end_date= taskform.end_date.data,
                              total_estimated_cost= taskform.total_estimated_cost.data,
                              total_days= total_days )
            print(start_date)
            print(end_date)
            db.session.add(task_to_create)
            db.session.commit()
            send_sms("A Task was Updated. Please Check your email man")
           # SendNotificationAsContractor("Task Record")
            flash(f'Task Created!')
            print(start_date)
            print(end_date)

    return redirect(url_for('delaypage'))

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
    flash(f'Task deleted!')
    return redirect(url_for('Taskpage'))

    
############  Functions related to Task management end here ####################


############   Work Inspection Request module STARTS here ####################

@app.route("/WorkInspectionReqs", methods=['GET', 'POST'])
@login_required
def wir_page():
    delays = Delay.query.all()
    wir_list = WorkInspectionRequests.query.all()
    wirform= WIRForm()
    today = date.today()
    
    
    

 #Render the Task page if the request is of type GET
    if request.method == "GET":
        return render_template('WorkInspectionRequest.html', delays=delays,wir_list=wir_list, wirform=wirform)

    if request.method == "POST":
    #Grab the form values and perform the relevant DB queries if the request is of type POST
#Creating new Tasks
             
            

            wir_to_create = WorkInspectionRequests(name=wirform.Name.data,
                              description=wirform.Description.data,
                              submitted_date=today)
            db.session.add(wir_to_create)
            db.session.commit()
            
            
            flash(f'WIR Created!')
           

    return redirect(url_for('wir_page'))
############   Work Inspection Request module ENDs here ####################


############   MATERIAL Inspection Request module STARTS here ####################


@app.route("/MaterialInspectReqs", methods=['GET', 'POST'])
@login_required
def material_inspection_page():
    db.create_all()
    pending_mirs= MaterialInspectionRequests.query.filter(MaterialInspectionRequests.status == "Submitted").count()
    approved_mirs= MaterialInspectionRequests.query.filter(MaterialInspectionRequests.status == "Approved!").count()
    Approved_As_Noted_mirs= MaterialInspectionRequests.query.filter(MaterialInspectionRequests.status == "Approved-As-Noted").count()
    ReviseandReSubmit_mirs= MaterialInspectionRequests.query.filter(MaterialInspectionRequests.status == "Revise-and-ReSubmit").count()
    Rejected_mirs= MaterialInspectionRequests.query.filter(MaterialInspectionRequests.status == "Rejected").count()
    mir_list = MaterialInspectionRequests.query.all()
    
#Render the MIR page if the request is of type GET
    if request.method == "GET":
        return render_template('MaterialInspectionManagementPage.html',pending_mirs=pending_mirs,approved_mirs=approved_mirs,Approved_As_Noted_mirs=Approved_As_Noted_mirs,
        ReviseandReSubmit_mirs=ReviseandReSubmit_mirs,Rejected_mirs=Rejected_mirs,mir_list=mir_list )

    if request.method == "POST":
    #Grab the form values and perform the relevant DB queries if the request is of type POST
#Creating new Tasks
             
            

            mir_to_create = MaterialInspectionRequests(name=mirform.Name.data,
                              description=mirform.Description.data,
                              submitted_date=today)
            db.session.add(mir_to_create)
            db.session.commit()
            
            
            flash(f'MIR Created!')
           

    return redirect(url_for('material_inspection_page'))


############   MATERIAL Inspection Request module ENDS here ####################






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
        flash(f'Please Sign in')
        return redirect(url_for('login_page'))
    if form.errors != {}:  # if the errors in the form error dictionary is not empty
        for err_msg in form.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')
    return render_template('sign-up.html', form=form)

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
            return redirect(url_for('DashBoard'))
        else:
            flash(f'Wrong Credentials. Re-enter the correct stuff',
                  category='danger')
    random_quote_number = random.randint(0,3)
    construction_author= ["– Winston Churchill","– Jeremy Renner","– Louis Kahn","– Charles Dickens"]
    construction_quotes = ["We shape our buildings- thereafter, they shape us.","Building is about getting around the obstacles that are presented to you.","A great building must begin with the immeasurable, must go through measurable means when it is being designed, and in the end must be unmeasured.","The whole difference between construction and creation is exactly this. That a thing constructed can only be loved after it is constructed- but a thing created is loved before it exists."]
    passed_quote_author=construction_author[random_quote_number]
    passed_quote=construction_quotes[random_quote_number]
   
    return render_template('sign-in.html', form=form, passed_quote_author=passed_quote_author,passed_quote=passed_quote)

@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash("you have been logged out")
    return redirect(url_for('login_page'))

############ All Functions related to Registration and Login END HERE ####################








   
# PDF GENERATION MODULES START HERE

@app.route("/DelayPdfGeneration", methods=['GET', 'POST'])
@login_required
def DelayPDFPage():

    #Query DB for objects to pass to table and cards
    delays = Delay.query.all()
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved!").count()
    Approved_As_Noted_delays= Delay.query.filter(Delay.status == "Approved-As-Noted").count()
    ReviseandReSubmit_delays= Delay.query.filter(Delay.status == "Revise-and-ReSubmit").count()
    Rejected_delays= Delay.query.filter(Delay.status == "Rejected").count()
    delay_count = pending_delays+approved_delays+Approved_As_Noted_delays+ReviseandReSubmit_delays+Rejected_delays
    today = date.today()
    # Render the HTML page with the passed information. This will be converted into a PDF
    #Use the following status types in forms: Submitted,Approved, Approved-As-Noted, Revise-and-ReSubmit, Rejected
    rendered= render_template('Delaypdf.html', pending_delays=pending_delays,approved_delays=approved_delays,
                        Approved_As_Noted_delays=Approved_As_Noted_delays,ReviseandReSubmit_delays=ReviseandReSubmit_delays,
                         Rejected_delays=Rejected_delays,delay_count=delay_count, today=today, delays=delays)

    #Converts the saved HTML as a pdf document. Saved in memory
    pdf = pdfkit.from_string(rendered, False)
    #Builds the response with the pdf attached in the response content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Delaypdfreport.pdf'
    #SendNotificationAsContractor("PDF Report Generation")
    return response

@app.route("/TaskPdfGeneration", methods=['GET', 'POST'])
@login_required
def TaskPDFPage():
    
    #Query DB for objects to pass to table and cards
    tasks = Tasks.query.all()
    pending_tasks= Tasks.query.filter(Tasks.status == "Pending").count()
    completed_tasks= Tasks.query.filter(Tasks.status == "Completed").count()
    inprogress_tasks= Tasks.query.filter(Tasks.status == "In Progress").count()
    data = {'Task' : 'Status', 'Pending' : pending_tasks, 'In Progress' : inprogress_tasks, 'Completed' : completed_tasks}
    today = date.today()
    # Render the HTML page with the passed information. This will be converted into a PDF
    rendered= render_template('taskpdf.html', pending_tasks=pending_tasks, completed_tasks=completed_tasks,inprogress_tasks=inprogress_tasks, data=data, today=today, tasks=tasks )

    #Converts the saved HTML as a pdf document. Saved in memory
    pdf = pdfkit.from_string(rendered, False)
    #Builds the response with the pdf attached in the response content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=taskpdfreport.pdf'
    #SendNotificationAsContractor("PDF Report Generation")
    return response

# PDF GENERATION MODULES END HERE



















#EMAIL NOTIFICATION MODULES START HERE

@app.route("/TaskPdfEmail", methods=['GET', 'POST'])
@login_required
def TaskPDFPageEmail():

      #Query DB for objects to pass to table and cards
    tasks = Tasks.query.all()
    pending_tasks= Tasks.query.filter(Tasks.status == "Pending").count()
    completed_tasks= Tasks.query.filter(Tasks.status == "Completed").count()
    inprogress_tasks= Tasks.query.filter(Tasks.status == "In Progress").count()
    data = {'Task' : 'Status', 'Pending' : pending_tasks, 'In Progress' : inprogress_tasks, 'Completed' : completed_tasks}
    today = date.today()
    # Render the HTML page with the passed information. This will be converted into a PDF
    rendered= render_template('taskpdf.html', pending_tasks=pending_tasks, completed_tasks=completed_tasks,inprogress_tasks=inprogress_tasks, data=data, today=today, tasks=tasks )
    #generate the pdf and store it in the appropriate directory
    pdf = pdfkit.from_string(rendered, 'construct/newtaskpdf.pdf')

    
    
    #send_sms()calls the send_sms function to send an sms to stakeholders. Message body is passed as a parameter
    #SendDelayReport() calls the imported function to send an email notification to the stakeholders with the attached pdf that is generated
    SendTaskReport()
    send_sms("A Task Progress Report was generated and to your email")
           


    return redirect('/Tasks', code=302)

@app.route("/DelayPdfEmail", methods=['GET', 'POST'])
@login_required
def DelayPDFPageEmail():

     
   
    

    #Query DB for objects to pass to table and cards
    delays = Delay.query.all()
    gannt_data = delays
    pending_delays= Delay.query.filter(Delay.status == "Submitted").count()
    approved_delays= Delay.query.filter(Delay.status == "Approved").count()
    delay_count = pending_delays+approved_delays
    today = date.today()
    #render the html page that will be converted into a pdf
    rendered= render_template('Delaypdf.html', pending_delays=pending_delays,approved_delays=approved_delays, delay_count=delay_count, today=today, delays=delays)
    #generate the pdf and store it in the appropriate directory
    pdf = pdfkit.from_string(rendered, 'construct/newdelaypdf.pdf')

    
    
    #send_sms()calls the send_sms function to send an sms to stakeholders. Message body is passed as a parameter
    #SendDelayReport() calls the imported function to send an email notification to the stakeholders with the attached pdf that is generated
    SendDelayReport()
    send_sms("Delay Report was printed. Please Check your email man")
           


    return redirect('/delays', code=302)


#EMAIL NOTIFICATION MODULES END HERE


#ALL IMAGE AND DOCUMENT UPLOADING MODULES START HERE


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
        
        #Save image reference
        today = date.today()
        image_to_save = TaskToImage(task_id=taskID,img_name=filename,uploaded_date=today )
        db.session.add(image_to_save)
        db.session.commit()
        
        
        return redirect('/Tasks', code=302)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/UploadWIR', methods=['POST'])
def upload_wir():
    status="Submitted"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        wir_ID= request.form['wir']
        file.save(os.path.join(app.root_path, "static/wir", filename))
        
        flash('The document has been  successfully uploaded!!!! ')
        today = date.today()
        #Entering the document reference record to the database
        wir_reference_to_save = WIRDocument(wir_id=wir_ID,wir_file_name=filename, status=status,submitted_date=today)
        db.session.add(wir_reference_to_save)
        db.session.commit()

        return redirect('/WorkInspectionReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)

@app.route('/UploadMIR', methods=['POST'])
def upload_mir():

    status="Submitted"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mir_ID= request.form['mir']
        file.save(os.path.join(app.root_path, "static/mir", filename))
        
        today = date.today()
        #Entering the document reference record to the database
        mir_reference_to_save = MIRDocument(mir_id=mir_ID,mir_file_name=filename, status=status,submitted_date=today)
        db.session.add(mir_reference_to_save)
        db.session.commit()

        flash('The document has been  successfully uploaded!!!   ')
        return redirect('/MaterialInspectReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)

@app.route('/UploadEOT', methods=['POST'])
def upload_eot():
    status="Submitted"
    db.create_all()
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        eot_ID= request.form['delay']
        file.save(os.path.join(app.root_path, "static/eot", filename))
        
        submitted_user= current_user.username
        today = date.today()
        #Entering the document reference record to the database
        eot_reference_to_save = EOTDocument(eot_id=eot_ID,eot_file_name=filename, status=status,submitted_date=today,submitted_by=submitted_user)
        db.session.add(eot_reference_to_save)
        db.session.commit()
        flash('The document has been  successfully uploaded!!!! ')
        return redirect('/delays', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)

#ALL UPLOADS AS CONSULTANT START HERE

@app.route('/UploadConsultantMIR', methods=['POST'])
def upload_mir_consultant():
    db.create_all()
    status="Submitted"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mir_ID= request.form['mir']
        file.save(os.path.join(app.root_path, "static/consultant_mir", filename))
        
        flash('The document has been  successfully uploaded!!!! ')
        
        #Entering the document reference record to the database
        today = date.today()
        consultant_reference_to_save = MIRConsultantDocument(mir_id=mir_ID,mir_file_name=filename, status=status,submitted_date=today)
        db.session.add(consultant_reference_to_save)
        db.session.commit()

        return redirect('/MaterialInspectReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)


@app.route('/UploadConsultantWIR', methods=['POST'])
def upload_wir_consultant():
    db.create_all()
    status="Submitted"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mir_ID= request.form['wir']
        file.save(os.path.join(app.root_path, "static/consultant_wir", filename))
        
        flash('The document has been  successfully uploaded!!!! ')
        
        #Entering the document reference record to the database
        today = date.today()
        consultant_reference_to_save = WIRConsultantDocument(wir_id=mir_ID,wir_file_name=filename, status=status,submitted_date=today)
        db.session.add(consultant_reference_to_save)
        db.session.commit()

        return redirect('/WorkInspectionReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)

@app.route('/UploadConsultantEOT', methods=['POST'])
def upload_eot_consultant():
    db.create_all()
    status="Submitted"
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No document selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mir_ID= request.form['delay']
        file.save(os.path.join(app.root_path, "static/consultant_eot", filename))
        
        flash('The document has been  successfully uploaded!!!! ')
        submitted_user= current_user.username
        #Entering the document reference record to the database
        today = date.today()
        consultant_reference_to_save = EOTConsultantDocument(eot_id=mir_ID,eot_file_name=filename, status=status,submitted_date=today,submitted_by=submitted_user)
        db.session.add(consultant_reference_to_save)
        db.session.commit()

        return redirect('/delays', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)


#ALL UPLOADS AS CONSULTANT END HERE


#ALL GALLERIES FOR IMAGES AND DOCUMENTS START HERE
   
@app.route("/ImageGallery/<int:id>", methods=['GET', 'POST'])
def ImageGallery(id):
        tasks= TaskToImage.query.all()
        
        print(tasks)
        ident=str(id)
        page_message="Image Gallery for Task"
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ImageGallery.html', taskref=tasks, taskid=ident, page_message=page_message)

@app.route("/WIRSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def wir_submitted_page(passed_id):
        wir_list=[]
        submitted_wir= WIRDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('WIRSubmittedPage.html', fileNamelist=submitted_wir, passed_wir=str(passed_id))

@app.route("/MIRSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def mir_submitted_page(passed_id):
        
        submitted_mir= MIRDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('MIRSubmittedPage.html', fileNamelist=submitted_mir, passed_mir_id=str(passed_id))


@app.route("/EOTSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def eot_submitted_page(passed_id):

        submitted_eot= EOTDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('SubmittedEOTGallery.html', submited_eot_refs=submitted_eot, passed_eot_id=str(passed_id))

@app.route("/EOTSubmittedConsultant/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def eot_submitted_page_consultant(passed_id):

        submitted_eot= EOTConsultantDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('SubmittedEOTGalleryConsultant.html', submited_eot_refs=submitted_eot, passed_eot_id=str(passed_id))

@app.route("/ConsultantMIRSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def consultant_mir_submitted_page(passed_id):
        
        submitted_mir_document= MIRConsultantDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ConsultantMIRSubmittedPage.html', fileNamelist=submitted_mir_document, passed_mir_id=str(passed_id))

@app.route("/ConsultantWIRSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def consultant_Wir_submitted_page(passed_id):
        
        submitted_Wir_document= WIRConsultantDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ConsultantWIRSubmittedPage.html', fileNamelist=submitted_Wir_document, passed_wir_id=str(passed_id))
 
#ALL IMAGE GALLERY AND SUBMITTED DOCUMENT DISPLAY PAGES END HERE






#ALL ENDPOINTS FOR IMAGE AND DOCUMENT DOWNLOADS START HERE

@app.route('/downloadwir/<wir_name>,', methods=['GET', 'POST'])
def downloadwir(wir_name):

    uploads = os.path.join(app.root_path, "static/wir")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=wir_name, as_attachment=True)

@app.route('/downloadmir/<mir_name>,', methods=['GET', 'POST'])
def downloadmir(mir_name):

    uploads = os.path.join(app.root_path, "static/mir")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=mir_name, as_attachment=True)

@app.route('/downloadeot/<eot_name>,', methods=['GET', 'POST'])
def downloadeot(eot_name):

    uploads = os.path.join(app.root_path, "static/eot")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=eot_name, as_attachment=True)


#ENDPOINTS FOR CONSULTANT DOWNLOADS


@app.route('/downloadconsultantmir/<mir_name>,', methods=['GET', 'POST'])
def downloadconsultantmir(mir_name):

    uploads = os.path.join(app.root_path, "static/consultant_mir")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=mir_name, as_attachment=True)

@app.route('/downloadconsultantwir/<wir_name>,', methods=['GET', 'POST'])
def downloadconsultantwir(wir_name):

    uploads = os.path.join(app.root_path, "static/consultant_wir")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=wir_name, as_attachment=True)

@app.route('/downloadconsultanteot/<eot_name>,', methods=['GET', 'POST'])
def downloadconsultanteot(eot_name):

    uploads = os.path.join(app.root_path, "static/consultant_eot")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=eot_name, as_attachment=True)

#ALL ENDPOINTS FOR DOCUMENT AND IMAGE DOWNLOADS END HERE



    


#ENDPOINTS FOR UPDATING THE STATUS OF RECORDS START HERE

#Updating Work Inspection Request Records
@app.route("/WIRStatusUpdate/<string:passed_id>")
def WIRStatusUpdate(passed_id):
    print("The ID passed from the page is: "+ passed_id)
    print("The WIR Status Query parameter passed from the page is:  "+ request.args.get('status'))
    #Set Status as Approved
    #Use the following status types in forms: Submitted,Approved, Approved-As-Noted, Revise-and-ReSubmit, Rejected
    wir_Status = request.args.get('status')
    if wir_Status == 'Approved!':
        wir_to_approve = WorkInspectionRequests.query.get_or_404(passed_id)
        wir_to_approve.status = "Approved!"
        db.session.commit()



        print("Status set as Approved! in the DB")
        flash(f'WIR Approved!')

    if wir_Status == 'Approved-As-Noted':
        wir_to_approved_as_noted = WorkInspectionRequests.query.get_or_404(passed_id)
        wir_to_approved_as_noted.status = "Approved-As-Noted"
        db.session.commit()
        print("Status set as Approved-As-Noted in the DB")
        flash(f'WIR Approved-As-Noted!')
    
    if wir_Status == 'Revise-and-ReSubmit':
        wir_to_revise_and_resubmit = WorkInspectionRequests.query.get_or_404(passed_id)
        wir_to_revise_and_resubmit.status = "Revise-and-ReSubmit"
        db.session.commit()
        print("Status set as Revise-and-ReSubmit in the DB")
        flash(f'WIR set as Revise-and-ReSubmit!')

    if wir_Status == 'Rejected':
        wir_to_revise_and_resubmit = WorkInspectionRequests.query.get_or_404(passed_id)
        wir_to_revise_and_resubmit.status = "Rejected"
        db.session.commit()
        print("Status set as Rejected in the DB")
        flash(f'WIR set as Rejected!')

    return redirect(url_for('wir_page'))

#Updating Task Records
@app.route("/TaskStatusUpdate/<string:passed_id>")
def TaskStatusUpdate(passed_id):
    print("The Task ID passed from the page is: "+ passed_id)
    print("The Task Status Query parameter passed from the page is:  "+ request.args.get('status'))

    task_Status = request.args.get('status')
    if task_Status == 'Completed':
        task_to_complete = Tasks.query.get_or_404(passed_id)
        task_to_complete.status = "Completed"
        db.session.commit()
        send_sms("A Project Task Has been completed by the Contractor")
        print("Task Status set as Completed in the DB")
        flash(f'Task Completed!')

    if task_Status == 'Pending':
        task_is_pending = Tasks.query.get_or_404(passed_id)
        task_is_pending.status = "Pending"
        db.session.commit()
        print("Task Status set as Pending in the DB")
        flash(f'Task set as Pending!')

    if task_Status == 'In Progress':
        task_in_progress = Tasks.query.get_or_404(passed_id)
        task_in_progress.status = "In Progress"
        db.session.commit()
        send_sms("A Project Task Has been set as In Progress by the Contractor")
        print("Task Status set as In Progress in the DB")
        flash(f'Task In Progress!')

    return redirect(url_for('Taskpage'))



#updating the status of Material Inspection Requests
@app.route("/MIRStatusUpdate/<string:passed_id>")
def MIRStatusUpdate(passed_id):
    print("The ID passed from the page is: "+ passed_id)
    print("The MIR Status Query parameter passed from the page is:  "+ request.args.get('status'))
    #Set Status as Approved
    #Use the following status types in forms: Submitted,Approved, Approved-As-Noted, Revise-and-ReSubmit, Rejected
    mir_Status = request.args.get('status')
    mir_doc = MIRDocument.query.all()


    if mir_Status == 'Approved!':
        mir_to_approve = MaterialInspectionRequests.query.get_or_404(passed_id)
        mir_to_approve.status = "Approved!"
        for mir in mir_doc:
            if mir.mir_id == str(passed_id):
                mir.status = "Approved!"
        db.session.commit()
        print("Status set as Approved! in the DB")
        flash(f'MIR Approved!')

    if mir_Status == 'Approved-As-Noted':
        mir_to_approved_as_noted = MaterialInspectionRequests.query.get_or_404(passed_id)
        mir_to_approved_as_noted.status = "Approved-As-Noted"
        db.session.commit()
        print("Status set as Approved-As-Noted in the DB")
        flash(f'MIR Approved-As-Noted!')
    
    if mir_Status == 'Revise-and-ReSubmit':
        mir_to_revise_and_resubmit = MaterialInspectionRequests.query.get_or_404(passed_id)
        mir_to_revise_and_resubmit.status = "Revise-and-ReSubmit"
        db.session.commit()
        print("Status set as Revise-and-ReSubmit in the DB")
        flash(f'MIR set as Revise-and-ReSubmit!')

    if mir_Status == 'Rejected':
        mir_to_revise_and_resubmit = MaterialInspectionRequests.query.get_or_404(passed_id)
        mir_to_revise_and_resubmit.status = "Rejected"
        db.session.commit()
        print("Status set as Rejected in the DB")
        flash(f'MIR set as Rejected!')

    return redirect(url_for('material_inspection_page'))

#Updating Work Inspection Request Records
@app.route("/DelayStatusUpdate/<string:passed_id>")
def EOTStatusUpdate(passed_id):
    print("The EOT ID passed from the page is: "+ passed_id)
    print("The EOT Status Query parameter passed from the page is:  "+ request.args.get('status'))
    #Set Status as Approved
    #Use the following status types in forms: Submitted,Approved, Approved-As-Noted, Revise-and-ReSubmit, Rejected
    eot_Status = request.args.get('status')
    if eot_Status == 'Approved!':
        eot_to_approve = Delay.query.get_or_404(passed_id)
        eot_to_approve.status = "Approved!"
        db.session.commit()



        print("Status set as Approved! in the DB")
        flash(f'EOT Approved!')

    if eot_Status == 'Approved-As-Noted':
        eot_to_approved_as_noted = Delay.query.get_or_404(passed_id)
        eot_to_approved_as_noted.status = "Approved-As-Noted"
        db.session.commit()
        print("Status set as Approved-As-Noted in the DB")
        flash(f'EOT Approved-As-Noted!')
    
    if eot_Status == 'Revise-and-ReSubmit':
        eot_to_revise_and_resubmit = Delay.query.get_or_404(passed_id)
        eot_to_revise_and_resubmit.status = "Revise-and-ReSubmit"
        db.session.commit()
        print("Status set as Revise-and-ReSubmit in the DB")
        flash(f'EOT set as Revise-and-ReSubmit!')

    if eot_Status == 'Rejected':
        eot_to_revise_and_resubmit = Delay.query.get_or_404(passed_id)
        eot_to_revise_and_resubmit.status = "Rejected"
        db.session.commit()
        print("Status set as Rejected in the DB")
        flash(f'EOT set as Rejected!')

    return redirect(url_for('delaypage'))

#ENDPOINTS FOR UPDATING THE STATUS OF RECORDS END HERE

  


#ALL FORMS FOR CREATING RECORDS START HERE
@app.route("/TaskCreateForm", methods=['GET', 'POST'])
@login_required
def TaskCreate():
    taskform = TaskForm()
    if request.method == "GET":
        
    
        return render_template('TastCreateForm.html', taskform=taskform)

    if request.method == "POST":
    #Grab the form values and perform the relevant DB queries if the request is of type POST

#Creating new Tasks test new gui
            start_date= taskform.start_date.data      
            end_date= taskform.end_date.data         
            total_days= (end_date-start_date).days  
            print(start_date)
            print(end_date)

            task_to_create = Tasks(Name=taskform.Name.data,
                              description=taskform.Description.data,
                              phase=taskform.phase.data,
                              Percentage=taskform.percentage.data,
                              start_date= taskform.start_date.data,
                              end_date= taskform.end_date.data,
                              total_estimated_cost= taskform.total_estimated_cost.data,
                              total_days= total_days )
            print(start_date)
            print(end_date)
            db.session.add(task_to_create)
            db.session.commit()
            send_sms("A Task was Updated. Please Check your email man")
           # SendNotificationAsContractor("Task Record")
            flash(f'Task Created!')
            print(start_date)
            print(end_date)

    return redirect(url_for('Taskpage'))

# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in taskform.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')

@app.route("/DelayCreateForm", methods=['GET', 'POST'])
@login_required
def DelayCreate():
    delayForm = DelayForm()
    if request.method == "GET":
        return render_template('DelayCreateForm.html', delayForm=delayForm)

    if request.method == "POST":

#Creating new Delays
            delay_to_create = Delay(type=delayForm.type_of.data,
                              description=delayForm.description.data,
                              severity=delayForm.severity.data,
                              phase=delayForm.phase.data,
                              delayed_days=delayForm.extended_days.data,
                              date= delayForm.date.data)
           
            db.session.add(delay_to_create)
            db.session.commit()
            SendNotificationAsContractor("EOT Submission")
            send_sms("A Delay EOT Was Submitted by the Contractor")
            flash(f'Delay Record Created!')     
            
           
    
    return redirect(url_for('delaypage'))

# if the errors in the form error dictionary is not empty

    if form.errors != {}:  
        for err_msg in taskform.errors.values():
            flash(f'There has been an exception thrown ==> {err_msg}  <==')




#ALL FORM PAGES FOR IMAGE AND DOCUMENT UPLOADS START HERE
@app.route("/TaskImageUpload", methods=['GET', 'POST'])
@login_required
def TaskImageUpload():

     tasks = Tasks.query.all()
     

     return render_template('TaskImageupload.html', tasks=tasks)

@app.route("/DelayEOTUploadPage", methods=['GET', 'POST'])
@login_required
def delayEOTUploadPage():

     delays = Delay.query.all()
     

     return render_template('EOTDocumentUpload.html', delays=delays)

@app.route("/ConsultantDelayEOTUploadPage", methods=['GET', 'POST'])
@login_required
def delayEOTUploadPageConsultant():

     delays = Delay.query.all()
     

     return render_template('EOTDocumentUploadConsultant.html', delays=delays)

    #ALL FORM PAGES FOR IMAGE AND DOCUMENT UPLOADS END HERE