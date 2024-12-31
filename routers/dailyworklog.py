
from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from models.ProjectModel import Project, ProjectRequest
from models.DailyWorkLogModel import DailyWorkLog
from database import invoice as db
from pymongo.errors import DuplicateKeyError


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
async def create(dailyworklok: DailyWorkLog = Body(...)):
    try:
        print("dailyworklok : ", dailyworklok)
        # customFields = dailyworklok.model_dump().get('customfields')
        # dailyworklok_data = dailyworklok.model_dump(exclude="customfields")
        new_project = await project_collection.insert_one(Project(**project_data, id=projectId).model_dump())
        new_project_data = await project_collection.find_one({"_id": new_project.inserted_id})
        for customeField in customFields:
            customeField['projectId'] = projectId
            await project_extra_field_collection.insert_one(ProjectExtraField(**customeField).model_dump())
        new_project_data = convert_objectid_to_str(new_project_data)
        del new_project_data["_id"]
        return {"success": True, "message": "Project created successfully", "data": new_project_data}
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project is already exist."
        )
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
        totalRecords = await project_collection.count_documents({})
        results = await project_collection.find().skip(skip).limit(limit).to_list(limit)
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Process fetched successfully",
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
            detail=f"An error occurred while fetching project: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_description="get a project"
)
async def get_project(project_id: str = ""):
    try:
        print("project_id  ", project_id, type(project_id))
        result = await project_collection.find_one({"id": project_id})
        if result:
            customFields = await project_extra_field_collection.find({"projectId": project_id}).to_list(None)
            print("customFields : ", customFields)
            del result["_id"]
            if customFields:
                for field in customFields:
                    del field["_id"]
            result["customeFields"] = customFields
            print("result : ", result)
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
