
from fastapi import APIRouter, Body, HTTPException, status, Depends
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from bson import ObjectId
from models.ClientModel import Client
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError




client_collection = db.get_collection("clients")
client_collection.create_index([("client", ASCENDING)], unique=True)

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new client",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(client: Client = Body(...)):
    try:
        new_client = await client_collection.insert_one(client.model_dump())
        new_client_data = await client_collection.find_one({"_id": new_client.inserted_id})
        new_client_data = convert_objectid_to_str(new_client_data)
        new_client_data["_id"] = str(new_client_data["_id"])
        return {"success": True, "message": "Client created successfully", "data": new_client_data}
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{client.dict().get('client')} already exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching Client: {str(e)}"
        )


@router.get(
    "/get_pagination",
    response_description="List all client"
)
async def list_pagination_invoice(page: int = 1):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await client_collection.count_documents({})
        results = await client_collection.find().skip(skip).limit(limit).to_list(limit)
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Client fetched successfully",
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
            detail=f"An error occurred while fetching client: {str(e)}"
        )
