import smtplib
from email.mime.text import MIMEText

subject = "Email Subject"
body = "This is the body of the text message"
sender = "patientconnect24@gmail.com"  #Sender Email Address
recipients = ["pgikonyo15@gmail.com"]  # Multiple email address can be given
password = "cjcj tlrs xcar alqp" # Gmail Application Password


# We will create a function to send mail .We will pass above values in funcion parameter.
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)   # Creating msg object using MIMEText class of email module
    msg['Subject'] = subject  # Assigning the subject
    msg['From'] = sender  # Assigning the sender email address
    msg['To'] = ', '.join(recipients)  # Assigning recepients email address.
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:   # Creating connection using context manager
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Email sent Successfully!")


# We will call the function and pass the parameter values defined in line no 4 to 8.
send_email(subject, body, sender, recipients, password)