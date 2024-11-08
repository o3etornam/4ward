from fastapi import HTTPException
from httpx import (
    AsyncClient,
    TimeoutException,
    HTTPStatusError,
    ConnectError,
    RequestError,
)
from loguru import logger

from core.config import settings
from core.schema import HubtelCallBackRequest


async def send_customer_sms(
    message: str,
    customer_number: str,
    session_id: str,
    order_id: str,
    meter_number: str,
):
    logger.info(
        f"Initiating Hubtel SMS request for Session: {session_id}, Order: {order_id}, meter_number: {meter_number}\n"
        f"URL: {settings.hubtel_sms}\n"
    )

    params = {
        "clientid": settings.client_id,
        "clientsecret": settings.client_secret,
        "from": "NUMA",
        "to": customer_number,
        "content": message,
    }

    try:
        logger.info(f"Sending SMS to {customer_number} with message: {message}")

        async with AsyncClient() as client:
            res = await client.get(
                url=settings.hubtel_sms,
                params=params,
            )

        # Check if the response status is not 2xx
        if not 200 <= res.status_code < 300:
            logger.error(
                f"Failed to send SMS. Status Code: {res.status_code}, Response: {res.text}"
            )
            raise HTTPException(
                status_code=res.status_code, detail="Failed to send SMS."
            )

        logger.info(
            f"SMS sent successfully. Status Code: {res.status_code}, Response: {res.json()}"
        )

    except TimeoutException:
        logger.error("Timeout occurred while trying to send the SMS.")
        raise HTTPException(status_code=504, detail="Timeout while sending SMS.")
    except ConnectError:
        logger.error("Connection error occurred while sending SMS.")
        raise HTTPException(status_code=503, detail="Failed to connect to SMS service.")
    except HTTPStatusError as e:
        logger.error(
            f"HTTP status error: {e.response.status_code}, Response: {e.response.text}"
        )
        raise HTTPException(
            status_code=e.response.status_code, detail="Error in SMS service response."
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"{e.detail}",
        )
    except RequestError as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to send SMS request.")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


async def hubtel_confirmation(session_id: str, order_id: str, status: str):
    headers = {
        "Connection": settings.connection,
        "Authorization": f"Basic endjeOBiZHhza250fT3={settings.hubtel_api_key}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }

    body = HubtelCallBackRequest(
        SessionId=session_id, OrderId=order_id, ServiceStatus=status
    )

    try:
        logger.info(
            f"Initiating Hubtel confirmation request for Session: {session_id}, Order: {order_id}, Status: {status}\n"
            f"URL: {settings.hubtel_fulfillment}\n"
            f"Headers: {headers}\n"
            f"Request Body: {body.model_dump()}"
        )

        async with AsyncClient() as client:
            res = await client.post(
                url=settings.hubtel_fulfillment,
                data=body.model_dump(),
                headers=headers,
            )

        # Check if the response status is not 2xx
        if not 200 <= res.status_code < 300:
            logger.error(
                f"Failed to confirm transaction. Status Code: {res.status_code}, Response: {res.text}"
            )
            raise HTTPException(
                status_code=res.status_code, detail="Failed to confirm transaction."
            )

        logger.info(
            f"Transaction confirmed successfully. Status Code: {res.status_code}, Response: {res.text}"
        )

    except TimeoutException:
        logger.error("Timeout occurred during Hubtel confirmation.")
        raise HTTPException(
            status_code=504, detail="Timeout while confirming with Hubtel."
        )
    except ConnectError:
        logger.error("Connection error occurred during Hubtel confirmation.")
        raise HTTPException(
            status_code=503, detail="Failed to connect to Hubtel service."
        )
    except HTTPStatusError as e:
        logger.error(
            f"HTTP status error during confirmation: {e.response.status_code}, Response: {e.response.text}"
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Error in Hubtel service response.",
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"{e.detail}",
        )
    except RequestError as e:
        logger.error(f"Request error during Hubtel confirmation: {str(e)}")
        raise HTTPException(
            status_code=400, detail="Failed to send confirmation request."
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred during Hubtel confirmation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )
