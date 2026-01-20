            


# CLOUDINARY FILE UPLOAD CODE

# try:
            #     result=await session.execute(select(model.email_metadata).where(model.email_metadata.uid==uid))
            #     result=result.scalars().first()
            #     if result is None or result.processed is True:
            #         continue
            #     filename=part.get_filename()
            #     if filename:
            #         filePath =os.path.join(file_download_path,filename)
            #         with open(filePath,'wb') as f:
            #             f.write(part.get_payload(decode=True))
            #         result=cloudinary.uploader.upload(filePath, 
            #         asset_folder = "AI Business Automation Assistant", 
            #         public_id = filename,
            #         overwrite = True, 
            #         resource_type = "raw")
            #         print("File uploaded successfully")
            #         url=result["url"]
            #         report_data=model.email_metadata(uid=uid,reportUrl=url,processed=True)
            #         session.add(report_data)
            #         await session.commit()
            #         print("Added to DB")
            # except Exception as E:
            #         print(E)



# SCHEDULER JOB ADD CODE

# try:
#     job=scheduler.add_job(get_mail,trigger='interval',seconds=30,id="Call_Fetch_mail_with_the_id_28",kwargs={"imap_uid":"28"})
#     print("Successfully added job in job store.")
# except Exception as err:
#     print("You have error scheduling jobs:    ",err)