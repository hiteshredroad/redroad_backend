
import os
from fastapi import APIRouter, Body, HTTPException, status, Response, Cookie, Depends, BackgroundTasks, Request
from utils import get_current_user, convert_objectid_to_str, get_skip_and_limit
from bson import ObjectId
from models.BillingTypesModel import BillingType, BillingTypesCollection
from datetime import datetime, timedelta, timezone
from database import invoice as db
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError




billingType_collection = db.get_collection("billingTypes")
billingType_collection.create_index([("department", ASCENDING)], unique=True)

router = APIRouter(dependencies=[
    Depends(get_current_user)
])


@router.post(
    "/",
    response_description="Add new billing",
    # response_model=BillingType,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create(billingType: BillingType = Body(...)):
    try:
        new_billingType = await billingType_collection.insert_one(billingType.model_dump(exclude=[id]))
        new_billingType_data = await billingType_collection.find_one({"_id": new_billingType.inserted_id})
        new_billingType_data = convert_objectid_to_str(new_billingType_data)
        new_billingType_data["_id"] = str(new_billingType_data["_id"])
        return {"success": True, "message": "Billing Types created successfully", "data": new_billingType_data}
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{billingType.dict().get('billingType')} already exist."
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
async def list_pagination_invoice(page: int = 1):
    try:
        skip, limit = get_skip_and_limit(page)
        totalRecords = await billingType_collection.count_documents({})
        results = await billingType_collection.find().skip(skip).limit(limit).to_list(limit)
        for result in results:
            result["_id"] = str(result["_id"])
        return {
            "success": True,
            "message": "Billing Types fetched successfully",
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
