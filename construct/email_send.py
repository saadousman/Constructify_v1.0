#Module to send email to the list of Contacts 
from construct.models import User
from construct import mail, Message, app
import requests
from flask import redirect
 
def SendNotificationAsContractor(Type):
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        if user.role == "Client" or user.role == "Consultant":
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

def SendDelayReport():
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        contact_list.append(user.email_address)
   # print(contact_list) test print <---- prints the array of emails. works!
   # Opens and sends the pdf generated by the PDFEmail function that calls this function
    with app.open_resource("DelayReport.pdf") as fp:
        msg = Message('Project Delay Report', sender = 'sdousmanflask@gmail.com', recipients = contact_list)
        msg.body = "A new Delay Report was Created and Sent by the contractor"
        msg.attach("DelayReport.pdf", "application/pdf", fp.read()) 
        mail.send(msg)
        
def SendTaskReport():
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        contact_list.append(user.email_address)
   # print(contact_list) test print <---- prints the array of emails. works!
   # Opens and sends the pdf generated by the PDFEmail function that calls this function
    with app.open_resource("TaskReport.pdf") as fp:
        msg = Message('Project Task Report', sender = 'sdousmanflask@gmail.com', recipients = contact_list)
        msg.body = "A new Task Progress Report was Created and Sent by the contractor"
        msg.attach("TaskReport.pdf", "application/pdf", fp.read()) 
        mail.send(msg)

def SendMIRReport():
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        contact_list.append(user.email_address)
        
   # print(contact_list) test print <---- prints the array of emails. works!
   # Opens and sends the pdf generated by the PDFEmail function that calls this function
    with app.open_resource("MIRReport.pdf") as fp:
        msg = Message('Material Inspection Request Report', sender = 'sdousmanflask@gmail.com', recipients = contact_list)
        msg.body = "A new Material inspection Report was Created and Sent by the contractor"
        msg.attach("MIRReport.pdf", "application/pdf", fp.read()) 
        mail.send(msg)

def SendWIRReport():
    Users=User.query.all()
    contact_list = []
    
    for user in Users:
        contact_list.append(user.email_address)
        
   # print(contact_list) test print <---- prints the array of emails. works!
   # Opens and sends the pdf generated by the PDFEmail function that calls this function
    with app.open_resource("WIRReport.pdf") as fp:
        msg = Message('Work Inspection Request Report', sender = 'sdousmanflask@gmail.com', recipients = contact_list)
        msg.body = "A new Work inspection Report was Created and Sent by the contractor"
        msg.attach("WIRReport.pdf", "application/pdf", fp.read()) 
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

     