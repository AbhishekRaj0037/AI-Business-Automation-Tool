# from app.websockets.dashboard import set_task_status,get_task_status
# from sqlalchemy import select,desc
# from sqlalchemy.dialects.postgresql import insert
# from app.db.models.email import email_metadata,email_attachments_metadata
# from app.services.gmail_service import get_imap_connection
# from app.utils.email_service import get_email_body,get_clean_body
# from datetime import timezone
# from email.utils import parsedate_to_datetime
# from app.services.storage_service import s3
# from app.websockets.dashboard import update_user_dashboard
# from app.db.enums import StatusEnum
# import uuid
# from pathlib import Path
# import asyncio
# import email


# async def process_dashboard(userId,username,session):
#     print("Welcome ",username)
#     await set_task_status(userId,"true")
#     result=await session.execute(select(email_metadata).where(email_metadata.user_id==userId).order_by(desc(email_metadata.imap_uid)).limit(1))
#     result=result.scalars().first()
#     starting_uid_range=0
#     if result is not None:
#          starting_uid_range=result.imap_uid
#     mail= await get_imap_connection(userId,session)
#     if mail is None:
#         await set_task_status(userId,"false")
#         return 
#     await asyncio.to_thread(mail.select, "inbox")
#     uids = await asyncio.to_thread(mail.uid, 'search', None, f'UID {starting_uid_range + 1}:*')
#     uid_list=uids[1][0].split()
#     for uid in uid_list:
#         status=await get_task_status(userId)
#         if status != "true":
#             print(f"Stopped fetching for {username}")
#             break
#         print(f"Fetching emails for {username}...")
#         mail_data=await asyncio.to_thread(mail.fetch,uid,'RFC822')
#         raw=mail_data[1][0][1]
#         raw_message=email.message_from_bytes(raw)
#         mail_from=raw_message["from"]
#         subject=raw_message["Subject"]
#         received_at=raw_message["Date"]
#         body=get_email_body(raw_message)
#         formatted_body = get_clean_body(body)
#         aware = parsedate_to_datetime(received_at)
#         received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)
#         is_uid_already_synced=await session.execute(select(email_metadata).where(email_metadata.imap_uid==int(uid) and email_metadata.user_id==userId))
#         is_uid_already_synced=is_uid_already_synced.scalars().first()
#         if is_uid_already_synced is None:
#             report_data=None
#             stmt = insert(email_metadata).values(
#                 user_id=userId,
#                 imap_uid=int(uid),
#                 mail_from=mail_from,
#                 subject=subject,
#                 received_at=received_at,
#                 body=formatted_body
#                 ).on_conflict_do_nothing(
#                 index_elements=["imap_uid"]
#                 )
#             await session.execute(stmt)
#             await session.commit()
#             for part in raw_message.walk():
#                 if part.get_content_maintype() == "multipart":
#                     continue
#                 filename = part.get_filename()
#                 if filename:
#                     try:
#                         file_bytes = part.get_payload(decode=True)
#                         ext=Path(filename).suffix
#                         unique_id=uuid.uuid4().hex
#                         s3_key=f"uploads/{userId}/{unique_id}{ext}"
#                         await asyncio.to_thread(
#                         s3.put_object,
#                         Bucket="amzn-s3-bucket-ai-business-automation-assistant",
#                         Key=f"{s3_key}",
#                         Body=file_bytes
#                         )
#                         print("File uploaded succesfully on aws bucket")
#                         file_data=None
#                         content_type = part.get_content_type()
#                         file_data=email_attachments_metadata(user_id=userId,imap_uid=int(uid),file_name=filename,file_type=content_type,file_size=len(file_bytes),status=StatusEnum.incomplete,checksum_sha256="!231231231231!",s3_key=s3_key)
#                         session.add(file_data)
#                         await session.commit()
#                     except Exception as e:
#                         print("Error:  ",e)
#             await update_user_dashboard(userId,stats_changes={
#                 "fetch_today":1
#             })
#             print("Added to DB")
#     await set_task_status(userId,"false")
#     mail.close()
#     return






from app.websockets.dashboard import set_task_status, get_task_status, update_user_dashboard
from sqlalchemy import select, desc, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db.models.email import email_metadata, email_attachments_metadata, failed_emails
from app.services.gmail_service import get_imap_connection
from app.utils.email_service import get_email_body, get_clean_body
from datetime import timezone, datetime
from email.utils import parsedate_to_datetime
from app.services.storage_service import s3
from app.db.enums import StatusEnum
from botocore.exceptions import ClientError
from pathlib import Path
import asyncio
import email as email_lib

BUCKET = "amzn-s3-bucket-ai-business-automation-assistant"
MAX_RETRIES = 5


def _categorize_error(e: Exception) -> str:
    msg = str(e).lower()
    if isinstance(e, (ConnectionError, OSError, TimeoutError)) or "imap" in msg or "socket" in msg:
        return "IMAP_FETCH"
    if isinstance(e, ClientError) or "s3" in msg or "bucket" in msg:
        return "S3_UPLOAD"
    if "sqlalchemy" in type(e).__module__ or "asyncpg" in type(e).__module__:
        return "DB_ERROR"
    return "PARSE_ERROR"


async def _s3_key_exists(s3_key: str) -> bool:
    def _check():
        try:
            s3.head_object(Bucket=BUCKET, Key=s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
    return await asyncio.to_thread(_check)


async def _record_failure(userId: str, uid_int: int, e: Exception, session) -> None:
    now = datetime.utcnow()
    stmt = (
        pg_insert(failed_emails)
        .values(
            user_id=userId,
            imap_uid=uid_int,
            retry_count=1,
            error_message=str(e)[:2000],
            error_category=_categorize_error(e),
            last_attempt_at=now,
            created_at=now,
        )
        .on_conflict_do_update(
            constraint="uq_failed_user_uid",
            set_={
                "retry_count": failed_emails.retry_count + 1,
                "error_message": str(e)[:2000],
                "error_category": _categorize_error(e),
                "last_attempt_at": now,
            },
        )
    )
    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as fe:
        await session.rollback()
        print(f"Could not record failure for UID {uid_int}: {fe}")


async def _fetch_and_store_email(userId: str, uid_int: int, uid_bytes: bytes, mail, session) -> bool:
    """
    Fetches one email from IMAP, uploads attachments to S3 (idempotent),
    commits email + all attachments atomically. Returns True on success.

    S3 keys are deterministic (uploads/{userId}/{uid_int}/{idx}{ext}) so a
    restart can detect already-uploaded files and skip them before retrying.
    """
    # Idempotency guard: already committed → clean up stale failed record and return
    existing = await session.execute(
        select(email_metadata).where(
            email_metadata.user_id == userId,
            email_metadata.imap_uid == uid_int,
        )
    )
    if existing.scalars().first() is not None:
        await session.execute(
            delete(failed_emails).where(
                failed_emails.user_id == userId,
                failed_emails.imap_uid == uid_int,
            )
        )
        await session.commit()
        return True

    try:
        mail_data = await asyncio.to_thread(mail.fetch, uid_bytes, "RFC822")
        raw = mail_data[1][0][1]
        raw_message = email_lib.message_from_bytes(raw)

        mail_from = raw_message["from"]
        subject = raw_message["Subject"]
        received_at_str = raw_message["Date"]
        body = get_email_body(raw_message)
        formatted_body = get_clean_body(body)
        aware = parsedate_to_datetime(received_at_str)
        received_at = aware.astimezone(timezone.utc).replace(tzinfo=None)

        email_row = email_metadata(
            user_id=userId,
            imap_uid=uid_int,
            mail_from=mail_from,
            subject=subject,
            received_at=received_at,
            body=formatted_body,
        )

        # Build all attachment rows — upload to S3 first, collect rows in memory
        attachment_rows = []
        for idx, part in enumerate(raw_message.walk()):
            if part.get_content_maintype() == "multipart":
                continue
            filename = part.get_filename()
            if not filename:
                continue

            ext = Path(filename).suffix
            # Deterministic key enables idempotent resume after a crash
            s3_key = f"uploads/{userId}/{uid_int}/{idx}{ext}"
            file_bytes = part.get_payload(decode=True)

            if not await _s3_key_exists(s3_key):
                await asyncio.to_thread(
                    s3.put_object,
                    Bucket=BUCKET,
                    Key=s3_key,
                    Body=file_bytes,
                )

            attachment_rows.append(
                email_attachments_metadata(
                    user_id=userId,
                    imap_uid=uid_int,
                    file_name=filename,
                    file_type=part.get_content_type(),
                    file_size=len(file_bytes),
                    status=StatusEnum.incomplete,
                    checksum_sha256="",
                    s3_key=s3_key,
                )
            )

        # Single atomic commit: email row + all attachment rows, or nothing
        session.add(email_row)
        session.add_all(attachment_rows)
        # Remove from failed_emails if this was a retry
        await session.execute(
            delete(failed_emails).where(
                failed_emails.user_id == userId,
                failed_emails.imap_uid == uid_int,
            )
        )
        await session.commit()

        await update_user_dashboard(userId, stats_changes={"fetch_today": 1})
        return True

    except Exception as e:
        await session.rollback()
        print(f"Failed to process UID {uid_int} for user {userId}: {e}")
        await _record_failure(userId, uid_int, e, session)
        return False


async def process_dashboard(userId: str, username: str, session):
    print("Welcome", username)
    await set_task_status(userId, "true")

    mail = await get_imap_connection(userId, session)
    if mail is None:
        await set_task_status(userId, "false")
        return

    await asyncio.to_thread(mail.select, "inbox")

    # Phase 1: Retry previously failed emails (retry_count < MAX_RETRIES)
    result = await session.execute(
        select(failed_emails)
        .where(
            failed_emails.user_id == userId,
            failed_emails.retry_count < MAX_RETRIES,
        )
        .order_by(failed_emails.retry_count, failed_emails.last_attempt_at)
    )
    retryable = result.scalars().all()

    for record in retryable:
        status = await get_task_status(userId)
        if status != "true":
            print(f"Stopped fetching during retries for {username}")
            break
        print(f"Retrying UID {record.imap_uid} (attempt {record.retry_count + 1}/{MAX_RETRIES}) for {username}")
        await _fetch_and_store_email(
            userId, record.imap_uid, str(record.imap_uid).encode(), mail, session
        )

    # Phase 2: Fetch new emails beyond the last successfully committed imap_uid
    status = await get_task_status(userId)
    if status != "true":
        await set_task_status(userId, "false")
        mail.close()
        return

    latest = await session.execute(
        select(email_metadata)
        .where(email_metadata.user_id == userId)
        .order_by(desc(email_metadata.imap_uid))
        .limit(1)
    )
    latest = latest.scalars().first()
    starting_uid = latest.imap_uid if latest is not None else 0

    uids = await asyncio.to_thread(mail.uid, "search", None, f"UID {starting_uid + 1}:*")
    uid_list = uids[1][0].split()

    for uid_bytes in uid_list:
        status = await get_task_status(userId)
        if status != "true":
            print(f"Stopped fetching for {username}")
            break
        uid_int = int(uid_bytes)
        print(f"Fetching UID {uid_int} for {username}...")
        await _fetch_and_store_email(userId, uid_int, uid_bytes, mail, session)

    await set_task_status(userId, "false")
    mail.close()