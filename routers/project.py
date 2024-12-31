
from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from models.ProjectModel import Project, ProjectRequest
from models.ProjectExtraFiledModel import ProjectExtraField
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
import json


project_collection = db.get_collection("projects")
project_collection.create_index([("id", ASCENDING)], unique=True)
project_extra_field_collection = db.get_collection("proejct_extra_fields")

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


""" Get Unique Product Id with combition of
    client lof process and series(1,2,3....) """


async def getUniqueProductId():
    try:
        projectUniqueId = ""
        project = await (project_collection.find()
                         .sort('created_at', -1)
                         .limit(1)
                         .to_list(1))

        if len(project) == 1:
            projectDBId = project[0]['id']
            projectDBId = projectDBId.split("-")
            count = str(int(projectDBId[1])+1).zfill(5)
            projectUniqueId = "PROJ-" + count
        elif len(project) == 0:
            projectUniqueId = "PROJ-" + "00001"

        return projectUniqueId
    except Exception as e:
        print(str(e))
        return ""


# Create project with their extra fields
@router.post(
    "/",
    response_description="Add new project",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(projectRequest: ProjectRequest = Body(...)):
    try:
        customFields = projectRequest.model_dump().get('customfields')
        project_data = projectRequest.model_dump(exclude="customfields")
        projectId = await getUniqueProductId()

        if projectId == "":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Product id"
            )

        new_project = await (project_collection
                             .insert_one(
                                 Project(**project_data, id=projectId)
                                 .model_dump()
                             ))

        new_project_data = await (project_collection
                                  .find_one(
                                      {"_id": new_project.inserted_id}
                                  ))

        for customeField in customFields:
            customeField['projectId'] = projectId
            await (project_extra_field_collection
                   .insert_one(
                       ProjectExtraField(**customeField).model_dump()
                   ))

        new_project_data = convert_objectid_to_str(new_project_data)

        del new_project_data["_id"]

        return {
            "success": True,
            "message": "Project created successfully",
            "data": new_project_data
        }

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Project is already exist."
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
async def list_pagination_project(
        page: int = 1,
        search: str = "[]"):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await project_collection.count_documents({})
        options = {}
        search = json.loads(search)
        if len(search) > 0:
            for searchKey in search:
                print("searchKey", searchKey)
                if searchKey['value'] and searchKey['value'] != "":
                    options[searchKey['field']] = {
                        "$regex": str(searchKey['value']),
                        '$options': 'i'
                    }

        results = await (project_collection
                         .find(options)
                         .skip(skip)
                         .limit(limit)
                         .to_list(limit)
                         )
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Project fetched successfully",
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
            customFields = (await project_extra_field_collection
                            .find({"projectId": project_id})
                            .to_list(None))
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
