import typing

from celery import shared_task


""" This is an example of a task that uses dependency injection
# import this
from dependency_injector.wiring import inject, Provide
@shared_task(
    name="ebapi_save_live_track",
    bind=True,
    retry_backoff=1,
    retry_kwargs={"max_retries": 3},
    autoretry_for=(exceptions.APIException, RetryError),
)
@inject
def ebapi_save_live_track(
    self,
    user_id: str,
    ebapi_handler: EBAPIHandler = Provide[Application.service.ebapi_handler],
) -> EBSchema.SaveAndCloseRoomResponse:
    response = ebapi_handler.save_live_track(user_id=user_id, body=payload)
    logger.info(f"EB API save live track response: {response}")
    return response

"""
""" This is an example of a task that turn async function to sync function
# import this
from asgiref.sync import async_to_sync

async def some_async_task(arg1: int, arg2: int):
    await asyncio.sleep(1)
    return arg1 + arg2

@shared_task()
@inject
def async_to_sync_task():
    t = async_to_sync(some_async_task)(arg1=1, arg2=2)
    # t is now a sync function

"""


@shared_task(
    name="health_check",
)
def health_check() -> typing.Dict[str, str]:
    return {"detail": "ok"}
