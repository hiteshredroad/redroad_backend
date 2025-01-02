from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from models.LofBuisnessModel import LofBuisness
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError


lofBuisness_collection = db.get_collection("lofBuisnesses")
lofBuisness_collection.create_index([("lofBuisness", ASCENDING)], unique=True)

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new LofBuisness",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(lofBuisness: LofBuisness = Body(...)):
    try:
        print(lofBuisness.model_dump(exclude=[id]))
        new_lofBuisness = (await lofBuisness_collection
                           .insert_one(lofBuisness
                                       .model_dump(exclude=[id])
                                       ))
        new_lofBuisness_data = (await lofBuisness_collection
                                .find_one({"_id": new_lofBuisness.inserted_id}
                                          ))
        new_lofBuisness_data = convert_objectid_to_str(new_lofBuisness_data)
        new_lofBuisness_data["_id"] = str(new_lofBuisness_data["_id"])
        return {
            "success": True,
            "message": "Billing Types created successfully",
            "data": new_lofBuisness_data
        }
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{lofBuisness.dict().get('lofBuisness')} already exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching billing type: {str(e)}"
        )


@router.get(
    "/get_pagination",
    response_description="List all billing types"
)
async def list_pagination_invoice(page: int = 1, search: str = ''):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await lofBuisness_collection.count_documents({})
        options = {}
        if search != '':
            options['lofbuisness'] = {"$regex": search, '$options': 'i'}
        results = await lofBuisness_collection.find(options).skip(skip).limit(limit).to_list(limit)
                   
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Lof Buisness fetched successfully",
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
            detail=f"An error occurred while fetching billing type: {str(e)}"
        )
