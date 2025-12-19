from dotenv import load_dotenv
from fastapi import FastAPI
import imaplib
import email
import os
import model

load_dotenv()

app=FastAPI()

imap_server=os.getenv("imap_server")
username=os.getenv("username")
password=os.getenv("password")
session=model.session

mail= imaplib.IMAP4_SSL(imap_server)

mail.login(username,password)



@app.get("/")
def read_root():
    mail.select("inbox")
    # status,messages=mail.search(None,"ALL")
    status,messages=mail.uid('search', None, 'UNSEEN')
    messages=messages[0].decode('utf-8')
    messages=messages.split()
    for ele in messages:
        msg=mail.fetch(ele,'RFC822')
        raw=msg[1][0][1]
        raw_message=email.message_from_bytes(raw)
        for part in raw_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename=part.get_filename()
            if bool(filename):
                filePath =os.path.join('/Users/abhishekraj/desktop/AI Business Automation Assistant/Downloaded Files',filename)
                with open(filePath,'wb') as f:
                    f.write(part.get_payload(decode=True))


   
