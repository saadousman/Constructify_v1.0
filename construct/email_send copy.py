#Module to send email to the list of Contacts 
from construct.models import Contact_list, User
from construct import mail, Message, app
 
def SendNotificationAsContractor(Type):
    Users=User.query.all()
    
    for user in Users:
        if user.role == "Client" or user.role == "Consultant":
            msg = Message('Project Delay Alert', sender = 'sdousmanflask@gmail.com', recipients = [user.email_address])
            msg.body = "A new " +  Type + " was created by the contractor"
            mail.send(msg)

def SendNotificationAsClient(Type):
    Users=User.query.all()
    
    for user in Users:
        if user.role == "Contractor" or user.role == "Client":
            msg = Message('Project Delay Alert', sender = 'sdousmanflask@gmail.com', recipients = [user.email_address])
            msg.body = "A new " +  Type + " was created by the Consultant/Client"
            mail.send(msg)

def SendDelayReport():
    Users=User.query.all()
    
    for user in Users:
        with app.open_resource("newpdf.pdf") as fp:
            msg = Message('Project Delay Report', sender = 'sdousmanflask@gmail.com', recipients = [user.email_address])
            msg.body = "A new Delay Report was Created and Sent by the contractor"
            msg.attach("newpdf.pdf", "application/pdf", fp.read()) 
            mail.send(msg)


     