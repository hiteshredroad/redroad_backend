from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from models.DepartmentModel import Department
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError


department_collection = db.get_collection("departments")
department_collection.create_index([("department", ASCENDING)], unique=True)

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new department",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(department: Department = Body(...)):
    try:
        new_department = await (department_collection
                                .insert_one(department.model_dump()))
        new_department_data = await (department_collection
                                     .find_one(
                                         {"_id": new_department.inserted_id}
                                     ))
        new_department_data = convert_objectid_to_str(new_department_data)
        new_department_data["_id"] = str(new_department_data["_id"])
        return {
            "success": True,
            "message": "Department created successfully",
            "data": new_department_data
        }
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{department.dict().get('department')} already exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching department: {str(e)}"
        )


@router.get(
    "/get_pagination",
    response_description="List all department"
)
async def list_pagination_invoice(page: int = 1, search: str = ''):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await department_collection.count_documents({})
        options = {}
        if search != '':
            options['department'] = {"$regex": search, '$options': 'i'}
        results = await (department_collection
                         .find(options)
                         .skip(skip)
                         .limit(limit)
                         .to_list(limit)
                         )
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Department fetched successfully",
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
            detail=f"An error occurred while fetching department: {str(e)}"
        )
