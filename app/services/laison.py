from fastapi import HTTPException, Path
from httpx import AsyncClient
from loguru import logger

from core.messages import PURCHASE_ERROR_MESSAGES, TOKEN_ERROR_MESSAGES
from core.config import settings
from services.encryption import PaymentEncryption

payment_encryption = PaymentEncryption(root_key=settings.root_key)


async def parse_query_response(res: str) -> dict:
    pairs = res.split("&")
    result = {
        pair.split("=")[0]: pair.split("=")[1] for pair in pairs if pair.split("=")[0]
    }
    return result


async def parse_token_list(token_list: str) -> str:
    left = 0
    right = 4
    res = []
    while left < 20:
        res.append(token_list[left:right])
        left += 4
        right += 4

    return " ".join(res)


async def get_customer_by_meter_number(meter_number: str = Path(..., min_length=13)):
    logger.info(f"Fetching customer data for meter number: {meter_number}")
    headers = {"Connection": settings.connection}
    params = {
        "function": "querycustomerbymeternumber",
        "meternumber": meter_number,
        "platformid": 1783072172428754944,
    }
    try:
        async with AsyncClient() as client:
            res = await client.get(
                url=settings.laison_url,
                params=params,
                headers=headers,
            )
        data = await parse_query_response(res.text)
        error_code = data.get("errorcode")

        if error_code == "0":
            logger.info(f"Customer found: {data['customername']}")
            return f"You have requested to top up {meter_number} {data['customername'].upper()}. \n\nEnter top up amount:"

        if PURCHASE_ERROR_MESSAGES.get(error_code):
            logger.error(f"Query error: {PURCHASE_ERROR_MESSAGES.get(error_code)}")
            raise HTTPException(
                status_code=400,  # Client error
                detail=PURCHASE_ERROR_MESSAGES.get(error_code),
            )
        else:
            logger.error(f"Unknown error occurred: {data}")
            raise HTTPException(
                status_code=500, detail=f"Unknown error occurred: {data}"
            )

    except HTTPException as hx:
        logger.error(f"HTTP error: {hx.detail}")
        raise HTTPException(
            status_code=hx.status_code,
            detail=f"{hx.detail}",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        )


async def get_payment_token(
    payment: float,
    transaction_id: str,
    meter_number: str,
):
    logger.info(
        f"Generating payment token for meter: {meter_number}, transaction: {transaction_id}, payment: {payment}"
    )
    try:
        purchase_param = payment_encryption.generate_purchase_string(
            transaction_id=transaction_id, payment=payment
        )

        headers = {"Connection": settings.connection}
        body = {
            "operatetype": "purchasebytransid",
            "transid": transaction_id,
            "meternumber": meter_number,
            "platformid": 1783072172428754944,
            "purchaseparam": purchase_param,
        }

        async with AsyncClient() as client:
            res = await client.post(
                url=settings.laison_url,
                data=body,
                headers=headers,
            )
        data = await parse_query_response(res.text)
        status = "success"

        error_code = data.get("errorcode")
        if error_code == "0":
            token_list = await parse_token_list(data.get("tokenlist"))
            logger.info(f"Payment successful for transaction ID: {transaction_id}")
            message = (
                f"Thank you for your purchase!\n"
                f"Transaction ID: {transaction_id}\n"
                f"Recharge Amount: GHC{data.get('rechargeamount')}\n"
                f"Recharge Volume: {data.get('rechargevolume')} \n"
                f"Token: {token_list}\n\n"
                f"For more information, please contact: {settings.customer_care}\n"
                "Thank you for choosing our service!"
            )
            return status, message

        if int(error_code) < 19:
            status = "failed"
        logger.error(f"Payment error: {TOKEN_ERROR_MESSAGES[error_code]}")

        message = (
            f"Thank you for your purchase! An Error occured while processing you transaction.\n"
            f"Transaction ID: {transaction_id}\n"
            f"Error Message: {TOKEN_ERROR_MESSAGES[error_code]}.\n"
            f"Please contact customer care at {settings.customer_care} for assistance.\n"
        )
        return status, message

    except HTTPException as hx:
        logger.error(f"HTTP error: {hx.detail}")
        raise HTTPException(
            status_code=hx.status_code,
            detail=f"{hx.detail}.",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        )
