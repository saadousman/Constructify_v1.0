#Module to send email to the list of Contacts 
from construct.models import Contact_list
from construct import mail, Message
 
def SendNotification(Type):
    contacts=Contact_list.query.all()
 
    for contact in contacts:
        if contact.Role == "Client":
            msg = Message('Project Delay Alert', sender = 'sdousmanflask@gmail.com', recipients = [contact.email_address])
            msg.body = "A new " +  Type + " was created by the contractor"
            mail.send(msg)