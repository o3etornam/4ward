import socket
from cachetools import TTLCache
from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from core.config import settings
from core.messages import MESSAGES
from core.schema import HubtelRequest, HubtelResponse, PayementRequest
from services.laison import (
    get_customer_by_meter_number,
    get_payment_token,
)
from services.hubtel import hubtel_confirmation, send_customer_sms

cache = TTLCache(maxsize=100, ttl=300)
router = APIRouter(prefix="/api/v1")

CUSTOMER_CARE_NUMBER = settings.customer_care


@router.get("/service-ip", tags=["Health"])
async def get_service_ip(request: Request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    server_ip = s.getsockname()[0]
    s.close()

    return {"server_ip": server_ip}


@router.post("/callback", response_model=HubtelResponse, tags=["Service Interaction"])
async def service_interaction(request: HubtelRequest):
    response = MESSAGES[request.Sequence]
    response["SessionId"] = request.SessionId
    try:
        logger.info(
            f"Processing callback for Sequence: {request.Sequence}, SessionId: {request.SessionId}"
        )

        if request.Sequence == 2:
            response["Message"] = await get_customer_by_meter_number(request.Message)
            cache[request.SessionId] = request.Message
            logger.info(
                f"Customer data retrieved for SessionId {request.SessionId}: {response['Message']}"
            )

        if request.Sequence == 3:
            response["Item"]["Price"] = request.Message
            logger.info(
                f"Price updated for SessionId {request.SessionId}: {request.Message}"
            )

        return response

    except HTTPException as e:
        logger.error(
            f"HTTP error while processing request for SessionId {request.SessionId}: {e.detail}"
        )
        response["Message"] = (
            f"An error occurred while processing your request. \nDetails: {e.detail}"
        )
        response["Type"] = "release"
        response["DataType"] = "display"
        response["FieldType"] = "text"
        if cache.get(request.SessionId):
            cache.pop(request.SessionId)
        return response

    except Exception as e:
        logger.error(
            f"Unexpected error while processing request for SessionId {request.SessionId}: {str(e)}"
        )
        response["Message"] = (
            f"An unexpected error occurred. Please contact customer care at {CUSTOMER_CARE_NUMBER} for assistance. Details: {str(e)}"
        )
        response["Type"] = "release"
        response["DataType"] = "display"
        response["FieldType"] = "text"
        if cache.get(request.SessionId):
            cache.pop(request.SessionId)
        return response


@router.post("/payment", tags=["Service Fulfilment"])
async def service_fulfilment(request: PayementRequest):
    logger.info(
        f"Processing payment for OrderId: {request.OrderId}, SessionId: {request.SessionId}"
    )

    if request.OrderInfo.Payment.IsSuccessful:
        logger.info(f"Payment successful for OrderId: {request.OrderId}")
        try:
            # Retrieve payment token after successful payment
            status, message = await get_payment_token(
                transaction_id=request.OrderId[:16],
                meter_number=cache.get(request.SessionId),
                payment=request.OrderInfo.Items[0].UnitPrice,
            )

            # Send SMS to customer with payment details
            logger.info(
                f"Payment token generated successfully for OrderId: {request.OrderId}"
            )
            await send_customer_sms(
                message=message,
                customer_number=request.OrderInfo.CustomerMobileNumber,
                session_id=request.SessionId,
                order_id=request.OrderId,
                meter_number=cache.get(request.SessionId),
            )

            # Confirm the transaction with Hubtel
            await hubtel_confirmation(
                session_id=request.SessionId, order_id=request.OrderId, status=status
            )

            return {"messages": "Payment processed succesfully"}

        except HTTPException as e:
            logger.error(
                f"HTTP error during payment processing for OrderId {request.OrderId}: {e.detail}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"HTTP error during payment processing for OrderId {request.OrderId}: {e.detail}",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during payment processing for OrderId {request.OrderId}: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during payment processing for OrderId {request.OrderId}: {str(e)}",
            )

    else:
        logger.warning(f"Payment unsuccessful for OrderId: {request.OrderId}")
        return {"Message": "Payment was not successful."}
