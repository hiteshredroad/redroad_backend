
from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, get_skip_and_limit
from models.DailyWorkLogModel import DailyWorkLog
from database import invoice as db


dailyworklog_collection = db.get_collection("daily_work_logs")

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new daily work log",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(dailyworklog: DailyWorkLog = Body(...)):
    try:
        new_dailywork_log = await (dailyworklog_collection
                                   .insert_one(dailyworklog.model_dump())
                                   )

        new_dailywork_log = await (dailyworklog_collection
                                   .find_one(
                                       {"_id": new_dailywork_log.inserted_id}
                                   ))
        del new_dailywork_log['_id']
        if (new_dailywork_log['customfields'] and
                len(new_dailywork_log['customfields']) > 0):
            for field in new_dailywork_log['customfields']:
                field["projectExtraFiled"] = str(field['projectExtraFiled'])

        return {
            "success": True,
            "message": "Daily work log created successfully",
            "data": new_dailywork_log
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching project: {str(e)}"
        )


@router.get(
    "/get_pagination",
    response_description="List all project"
)
async def list_pagination_project(page: int = 1):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await dailyworklog_collection.count_documents({})
        results = await (dailyworklog_collection
                         .find()
                         .skip(skip)
                         .limit(limit)
                         .to_list(limit)
                         )
        for result in results:
            del result["_id"]
            if result['customfields'] and len(result['customfields']) > 0:
                for field in result['customfields']:
                    field["projectExtraFiled"] = str(
                        field['projectExtraFiled'])
        return {
            "success": True,
            "message": "Daily Work log fetched successfully",
            "data": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalRecords": totalRecords,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching daily work log: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_description="get a daily work log"
)
async def get_project(project_id: str = ""):
    try:
        print("project_id  ", project_id, type(project_id))
        result = await dailyworklog_collection.find_one({"id": project_id})
        del result["_id"]
        return {
            "success": True,
            "message": "Process fetched successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching project: {str(e)}"
        )
