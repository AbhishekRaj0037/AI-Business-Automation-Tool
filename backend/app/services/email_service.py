from app.websockets.dashboard import set_task_status,get_task_status
from sqlalchemy import select,desc
from sqlalchemy.dialects.postgresql import insert
from app.db.models.email import email_metadata,email_attachments_metadata
from app.services.gmail_service import get_imap_connection
from app.utils.email_service import get_email_body,get_clean_body
from datetime import timezone
from email.utils import parsedate_to_datetime
from app.services.storage_service import s3
from app.websockets.dashboard import update_user_dashboard
from app.db.enums import StatusEnum
import uuid
from pathlib import Path
import asyncio
import email


async def process_dashboard(userId,username,session):
    print("Welcome ",username)
    await set_task_status(userId,"true")
    result=await session.execute(select(email_metadata).where(email_metadata.user_id==userId).order_by(desc(email_metadata.imap_uid)).limit(1))
    result=result.scalars().first()
    starting_uid_range=0
    if result is not None:
         starting_uid_range=result.imap_uid
    mail= await get_imap_connection(userId,session)
    if mail is None:
        await set_task_status(userId,"false")
        return 
    await asyncio.to_thread(mail.select, "inbox")
    uids = await asyncio.to_thread(mail.uid, 'search', None, f'UID {starting_uid_range + 1}:*')
    uid_list=uids[1][0].split()
    for uid in uid_list:
        status=await get_task_status(userId)
        if status != "true":
            print(f"Stopped fetching for {username}")
            break
        print(f"Fetching emails for {username}...")
        mail_data=await asyncio.to_thread(mail.fetch,uid,'RFC822')
        raw=mail_data[1][0][1]
        raw_message=email.message_from_bytes(raw)
        mail_from=raw_message["from"]
        subject=raw_message["Subject"]
        received_at=raw_message["Date"]
        body=get_email_body(raw_message)
        formatted_body = get_clean_body(body)
        aware = parsedate_to_datetime(received_at)
        received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)
        is_uid_already_synced=await session.execute(select(email_metadata).where(email_metadata.imap_uid==int(uid) and email_metadata.user_id==userId))
        is_uid_already_synced=is_uid_already_synced.scalars().first()
        if is_uid_already_synced is None:
            report_data=None
            stmt = insert(email_metadata).values(
                user_id=userId,
                imap_uid=int(uid),
                mail_from=mail_from,
                subject=subject,
                received_at=received_at,
                body=formatted_body
                ).on_conflict_do_nothing(
                index_elements=["imap_uid"]
                )
            await session.execute(stmt)
            await session.commit()
            for part in raw_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                filename = part.get_filename()
                if filename:
                    try:
                        file_bytes = part.get_payload(decode=True)
                        ext=Path(filename).suffix
                        unique_id=uuid.uuid4().hex
                        s3_key=f"uploads/{userId}/{unique_id}{ext}"
                        await asyncio.to_thread(
                        s3.put_object,
                        Bucket="amzn-s3-bucket-ai-business-automation-assistant",
                        Key=f"{s3_key}",
                        Body=file_bytes
                        )
                        print("File uploaded succesfully on aws bucket")
                        file_data=None
                        content_type = part.get_content_type()
                        file_data=email_attachments_metadata(user_id=userId,imap_uid=int(uid),file_name=filename,file_type=content_type,file_size=len(file_bytes),status=StatusEnum.incomplete,checksum_sha256="!231231231231!",s3_key=s3_key)
                        session.add(file_data)
                        await session.commit()
                    except Exception as e:
                        print("Error:  ",e)
            await update_user_dashboard(userId,stats_changes={
                "fetch_today":1
            })
            print("Added to DB")
    await set_task_status(userId,"false")
    mail.close()
    return