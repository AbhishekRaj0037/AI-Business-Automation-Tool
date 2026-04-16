from fastapi import APIRouter,Depends,Request,HTTPException,Query,HTTPException,Depends,Request
from app.db.models import email,report as reportModel
from sqlalchemy import select,update,desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
import  app.websockets.dashboard as wbsckdashboard
from app.services.parse_files import parse_file
from app.services.ai_service import splitter,vectorstore,llm
from app.services.storage_service import s3
from datetime import datetime
from app.db import enums
import asyncio
import json


router=APIRouter()

@router.get("/get-all-reports")
async def get_all_reports(request:Request,page:int=Query(1),limit:int=Query(5),session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
    offset=(page-1)*limit
    result=await session.execute(select(email.email_metadata).where(email.email_metadata.user_id==request.state.userId).offset(offset).order_by(desc(email.email_metadata.imap_uid)).limit(limit))
    result=result.scalars().all()
    return result
   
@router.get("/get-reports-by-id")
async def get_report_by_id(request:Request,imap_uid:int=Query(1),page:int=Query(1),limit:int=Query(4),session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
    mail_result=await session.execute(select(email.email_metadata).where(email.email_metadata.imap_uid==int(imap_uid) and email.email_metadata.user_id==request.state.userId))
    mail_result=mail_result.scalars().first()
    offset=(page-1)*limit
    attachment_result=await session.execute(select(email.email_attachments_metadata).offset(offset).where(email.email_attachments_metadata.imap_uid==int(imap_uid) and email.email_attachments_metadata.user_id==request.state.userId).limit(limit))
    attachment_result=attachment_result.scalars().all()
    list_of_file_url=[]
    for result in attachment_result:
        url = await asyncio.to_thread(
        s3.generate_presigned_url,
        ClientMethod='get_object',
        Params={
        'Bucket': "amzn-s3-bucket-ai-business-automation-assistant",
        'Key': result.s3_key,
        'ResponseContentDisposition': 'inline',
        'ResponseContentType': result.file_type
    },
    ExpiresIn=300
    )
        list_of_file_url.append(url)
    result={"mail_result":mail_result,"attachment_result":attachment_result,"list_of_file_presigned_url":list_of_file_url}
    return result




@router.get("/get-all-ai-reports")
async def get_all_ai_reports(request:Request,page:int=Query(1),limit:int=Query(5),session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
    offset=(page-1)*limit
    result=await session.execute(select(reportModel.reports).where(reportModel.reports.user_id==request.state.userId).offset(offset).order_by(desc(reportModel.reports.id)).limit(limit))
    result=result.scalars().all()
    return result





@router.post("/analyse-report")
async def analyse_report(request:Request,session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
    body=await request.json()
    file_name=body["file_name"]
    s3_key=body["s3_key"]
    report_id=body["report_id"]
    report_result=await session.execute(select(email.email_attachments_metadata).where(email.email_attachments_metadata.id==int(report_id) and email.email_attachments_metadata.user_id==request.state.userId))
    report_result=report_result.scalars().first()
    if report_result.status==enums.StatusEnum.completed:
        return {"status":"Report already analysed"}
    try:
        await wbsckdashboard.update_user_dashboard(request.state.userId,queue_changes={
                    "pending":1,
                })
        response=await asyncio.to_thread(s3.get_object,Bucket="amzn-s3-bucket-ai-business-automation-assistant",
            Key=s3_key)
        file_bytes = await asyncio.to_thread(response["Body"].read)
        loaded_docs=await asyncio.to_thread(parse_file,file_bytes,file_name,s3_key)
        doc_chunks=await asyncio.to_thread(splitter.split_documents,loaded_docs)
        await asyncio.to_thread(vectorstore.add_documents,doc_chunks)
        result=update(email.email_attachments_metadata).where(email.email_attachments_metadata.id == report_id and email.email_attachments_metadata.user_id==request.state.userId).values(status=enums.StatusEnum.completed)
        await session.execute(result)
        await session.commit()
        await wbsckdashboard.update_user_dashboard(request.state.userId,queue_changes={
                    "pending":-1,
                })
        await wbsckdashboard.update_user_dashboard(request.state.userId,stats_changes={
                    "completed":1,
                })
    except Exception as err:
        await wbsckdashboard.update_user_dashboard(request.state.userId,queue_changes={
                    "pending":-1,
                })
        raise HTTPException(status_code=500, detail=str(err))
    return {"status": "done", "chunks": len(doc_chunks)}


@router.post("/query-document")
async def search_document(request:Request,session:AsyncSession= Depends(get_session)):
    print("Welcome ",request.state.username)
    body=await request.json()
    query=body["query"]
    try:
        retriever = await asyncio.to_thread(
        vectorstore.as_retriever,
        search_type="similarity",
        search_kwargs={"k": 10}
        )
        retrieved_docs = await asyncio.to_thread(retriever.invoke, query)
        context_parts = []
        source_map = {}
        for i, doc in enumerate(retrieved_docs):
            chunk_id = f"chunk_{i}"
            context_parts.append(f"[SOURCE:{chunk_id}]\n{doc.page_content}")
            file_type = doc.metadata.get("file_type", "")
            source = {
                "s3_key": doc.metadata.get("s3_key", ""),
                "file_name": doc.metadata.get("file_name", "unknown"),
                "file_type": file_type,
            }
            if file_type == "pdf":
                source["page"] = doc.metadata.get("page", None)

            elif file_type == "excel":
                source["sheet"] = doc.metadata.get("sheet", None)
                source["row_count"] = doc.metadata.get("row_count", None)

            elif file_type == "docx":
                source["section"] = doc.metadata.get("section", None)

            source_map[chunk_id] = source
        context = "\n\n".join(context_parts)
        system_prompt = """You are a report generator. Given context from source documents,
    generate a structured report. Respond ONLY with valid JSON, no markdown, no backticks.

    The JSON must have this exact structure:
    {
    "report_name": "short descriptive filename like food_order_analysis.pdf",
    "report_type": "one of: order_report, policy_report, financial_report, general_report",
    "report_summary": "2-3 sentence summary of what this report contains",
    "tiptap_json": {
        "type": "doc",
        "content": [
        {
            "type": "heading",
            "attrs": {"level": 2, "sources": ["chunk_0"]},
            "content": [{"type": "text", "text": "Your heading here"}]
        },
        {
            "type": "paragraph",
            "attrs": {"sources": ["chunk_0", "chunk_1"]},
            "content": [{"type": "text", "text": "Your paragraph here"}]
        },
        {
            "type": "table",
            "attrs": {"sources": ["chunk_2"]},
            "content": [
            {
                "type": "tableRow",
                "content": [
                {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Column Name"}]}]}
                ]
            },
            {
                "type": "tableRow",
                "content": [
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Cell value"}]}]}
                ]
            }
            ]
        }
        ]
    }
    }

    RULES:
    - Every node (heading, paragraph, table) MUST have attrs.sources with the chunk IDs used
    - Tables MUST wrap text inside paragraph nodes within cells
    - Use the SOURCE IDs provided in the context (like chunk_0, chunk_1)
    - report_name should be a clean filename with no spaces (use underscores)
    """

        response = await llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nGenerate a report for: {query}"}
        ])
        result = json.loads(response.content)
        report_data=reportModel.reports(
            user_id=request.state.userId,
            report_name=result["report_name"],
            report_type=result["report_type"],
            report_summary=result["report_summary"],
            tiptap_json=result["tiptap_json"],
            source_map=source_map,
            generated_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(report_data)
        await session.commit()
        print("Added to DB")
        print(response)
    except Exception as e:
        print("Error occured: ",e)
        return 
    return {
        "report_id": report_data.id,
        "report_name": report_data.report_name,
        "report_type": report_data.report_type,
        "report_summary": report_data.report_summary,
        "tiptap_json": report_data.tiptap_json,
        "source_map": report_data.source_map,
    }


@router.get("/get-report/{report_id}")
async def get_report(report_id: int, request: Request,session:AsyncSession= Depends(get_session)):
    result = await session.execute(
        select(reportModel.reports).where(
            reportModel.reports.id == report_id,
            reportModel.reports.user_id == request.state.userId
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "title": report.report_name,
        "report_summary": report.report_summary,
        "tiptap_json": report.tiptap_json,
        "source_map": report.source_map,
        "report_type": report.report_type,
        "generated_at": report.generated_at,
        "updated_at": report.updated_at,
    }


@router.put("/update-report/{report_id}")
async def update_report(report_id: int, request: Request,session:AsyncSession= Depends(get_session)):
    body = await request.json()

    result = await session.execute(
        select(reportModel.reports).where(
            reportModel.reports.id == report_id,
            reportModel.reports.user_id == request.state.userId
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.tiptap_json = body["tiptap_json"]
    report.updated_at = datetime.now()

    await session.flush()
    await session.commit()

    return {"status": "saved", "report_id": report.id}

