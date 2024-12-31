
from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from models.ProcessModel import Process
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError


process_collection = db.get_collection("processes")
process_collection.create_index([("process", ASCENDING)], unique=True)

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new process",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(process: Process = Body(...)):
    try:
        new_process = await process_collection.insert_one(process.model_dump())
        new_process_data = await (process_collection
                                  .find_one(
                                      {"_id": new_process.inserted_id}
                                  ))
        new_process_data = convert_objectid_to_str(new_process_data)
        new_process_data["_id"] = str(new_process_data["_id"])
        return {
            "success": True,
            "message": "Process created successfully",
            "data": new_process_data
        }
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{process.dict().get('process')} already exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching process: {str(e)}"
        )


@router.get(
    "/get_pagination",
    response_description="List all process"
)
async def list_pagination_invoice(page: int = 1, search: str = ''):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await process_collection.count_documents({})
        options = {}
        if search != '':
            options['process'] = {"$regex": search, '$options': 'i'}
        results = await (process_collection
                         .find(options)
                         .skip(skip)
                         .limit(limit)
                         .to_list(limit)
                         )
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
            detail=f"An error occurred while fetching process: {str(e)}"
        )
