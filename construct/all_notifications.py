#Module to send email to the list of Contacts 
from construct.models import User
from construct import mail, Message, app
import requests
from flask import redirect
 
def SendNotificationAsContractor(Type):
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        if user.role == "Client" or user.role == "Consultant"or user.role == "Contractor":
            contact_list.append(user.email_address)
    
    msg = Message('Project Delay Alert', sender = 'sdousmanflask@gmail.com', recipients = contact_list)
    msg.body = "A new " +  Type + " was created by the Contractor"
    mail.send(msg)

def SendNotificationAsConsultant(Type):
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        if user.role == "Contractor" or user.role == "Client":
            contact_list.append(user.email_address)
    
    
    msg = Message('Project Alert', sender = 'sdousmanflask@gmail.com', recipients = [user.email_address])
    msg.body = "A new " +  Type + " was created by the Consultant"
    mail.send(msg)



def SendAllReports(pass_pdf_file_name,message_subject,message_body):
    Users=User.query.all()
    contact_list = []
    pdf_file_name=pass_pdf_file_name
    message_subject=message_subject
    message_body=message_body
    
    for user in Users:
        contact_list.append(user.email_address)
    #using the arguments passed from the different calling modules. DRY!!!
    with app.open_resource("pdf/"+pdf_file_name) as fp:
        msg = Message(message_subject, sender = 'sdousmanflask@gmail.com', recipients = contact_list)
        msg.body = message_body
        msg.attach(pass_pdf_file_name, "application/pdf", fp.read()) 
        mail.send(msg)


  

def send_sms(Message):
    Users=User.query.all()
    user_id="15896"     #credentials are currently hard-coded,should pass them as environmental variables
    api_key= "c977qWgaQfGYfZHoXJc1"
    sender_id="NotifyDEMO"
    message= Message  #Message is passed as a parameter to this function by the caller function

    for user in Users: #iterates through all users and obtains the contact numbers. Numbers cannot be passed as a list due to API limitations
                    
            request_string="https://app.notify.lk/api/v1/send?"+"user_id="+user_id+"&api_key="+api_key+"&sender_id="+sender_id+"&to="+user.contact_number+"&message="+message
            print(request_string) #Test- to inspect the generated URL
            r = requests.get(request_string) #Makes the GET request to the API and Gets JSON response 
            print(r.text) #Test- to inspect the response from the SMS API

     