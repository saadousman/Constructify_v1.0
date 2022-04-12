from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, make_response, jsonify, Response, send_from_directory
from construct.models import User, Delay, Tasks,  TaskToImage, WorkInspectionRequests, WIRDocument, MaterialInspectionRequests, MIRDocument, MIRConsultantDocument
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
import requests

STORAGE_CONNECTION_STRING = 'BlobEndpoint=https://constructify.blob.core.windows.net/;QueueEndpoint=https://constructify.queue.core.windows.net/;FileEndpoint=https://constructify.file.core.windows.net/;TableEndpoint=https://constructify.table.core.windows.net/;SharedAccessSignature=sv=2020-08-04&ss=f&srt=sco&sp=rwdlc&se=2023-04-10T03:23:17Z&st=2022-04-09T19:23:17Z&spr=https,http&sig=s7GEen6scx0kjjH2GeRCJODr8C59u8jCRv%2FmBcHS%2FaE%3D'
UPLOAD_FOLDER = 'construct/static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'])
 
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
    flash(f'Task deleted!')
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
        
        #Save image reference
        image_to_save = TaskToImage(task_id=taskID,img_name=filename)
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
        
        #Entering the document reference record to the database
        wir_reference_to_save = WIRDocument(wir_id=wir_ID,wir_file_name=filename, status=status)
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
        
        
        #Entering the document reference record to the database
        mir_reference_to_save = MIRDocument(mir_id=mir_ID,mir_file_name=filename, status=status)
        db.session.add(mir_reference_to_save)
        db.session.commit()

        flash('The document has been  successfully uploaded!!!   ')
        return redirect('/MaterialInspectReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)

   
@app.route("/ImageGallery/<int:id>", methods=['GET', 'POST'])
def ImageGallery(id):
        tasks= TaskToImage.query.all()
        
        print(tasks)
        ident=str(id)
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ImageGallery.html', taskref=tasks, taskid=ident)
 

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
        
        submitted_wir= MIRDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('MIRSubmittedPage.html', fileNamelist=submitted_wir, passed_mir_id=str(passed_id))

@app.route("/ConsultantMIRSubmitted/<string:passed_id>", methods=['GET', 'POST'])
@login_required
def consultant_mir_submitted_page(passed_id):
        
        submitted_mir_document= MIRConsultantDocument.query.all()
        
        
        
      #  return Response(images=images, mimetype=img.mimetype)
        return render_template('ConsultantMIRSubmittedPage.html', fileNamelist=submitted_mir_document, passed_mir_id=str(passed_id))

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

@app.route('/downloadconsultantmir/<mir_name>,', methods=['GET', 'POST'])
def downloadconsultantmir(mir_name):

    uploads = os.path.join(app.root_path, "static/consultant_mir")
    print("The path to the downloaded file is: "+uploads)
    return send_from_directory(directory=uploads, path=mir_name, as_attachment=True)




@app.route("/MaterialInspectReqs", methods=['GET', 'POST'])
@login_required
def material_inspection_page():
    db.create_all()
    mirform= MIRForm()
    mir_list = MaterialInspectionRequests.query.all()
    today = date.today()
    print(mirform)
    print(mir_list)
#Render the MIR page if the request is of type GET
    if request.method == "GET":
        return render_template('MaterialInspectionRequest.html',mirform=mirform,mir_list=mir_list)

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
        print("Task Status set as In Progress in the DB")
        flash(f'Task In Progress!')

    return redirect(url_for('Taskpage'))



#
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
        consultant_reference_to_save = MIRConsultantDocument(mir_id=mir_ID,mir_file_name=filename, status=status)
        db.session.add(consultant_reference_to_save)
        db.session.commit()

        return redirect('/MaterialInspectReqs', code=302)
    else:
        print("sum shit wrong with the file extensions")
        flash("Allowed file types are 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip' ")
        return redirect(request.url)