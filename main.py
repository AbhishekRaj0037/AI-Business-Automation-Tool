from fastapi import FastAPI
import imaplib
import email

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
    msg=mail.fetch('28777','RFC822')
    
    raw=msg[1][0][1]
    raw_message=raw.decode('utf-8')
    result=email.message_from_string(raw_message)
    if result.is_multipart():
        print("YES")
    else:
        print("No")
    breakpoint()
    for part in finalMsg.walk():
        if part.get_content_maintype() == 'application/pdf':
            print("Yes this part is pdf")


   
