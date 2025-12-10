from fastapi import FastAPI
import imaplib
import email
import os

app=FastAPI()

imap_server="imap.gmail.com"
username="mabhishek.tethered@gmail.com"
password="sobu ofoa gqxm cqjt"

mail= imaplib.IMAP4_SSL(imap_server)

mail.login(username,password)



@app.get("/")
def read_root():
    mail.select("inbox")
    status,messages=mail.search(None,"ALL")
    messages=messages[0].decode('utf-8')
    messages=messages.split()
    for ele in messages:
        msg=mail.fetch(ele,'RFC822')
        raw=msg[1][0][1]
        raw_message=email.message_from_bytes(raw)
        # result=email.message_from_string(raw_message)
        # if result.is_multipart():
        #     print("YES")
        # else:
        #     print("No")
        for part in raw_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename=part.get_filename()
            if bool(filename):
                filePath =os.path.join('/Users/abhishekraj/desktop/AI Business Automation Assistant/Downloaded Files',filename)
                with open(filePath,'wb') as f:
                    f.write(part.get_payload(decode=True))
                break


   
