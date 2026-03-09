from pydantic import ValidationError
import websockets
import asyncio

from common.log import logger
from common.types import AgentMessage
from websockets.exceptions import ConnectionClosed


def _ws_is_open(ws) -> bool:
    if ws is None:
        return False
    try:
        return ws.state.name == "OPEN"
    except AttributeError:
        pass
    try:
        return ws.open
    except AttributeError:
        return ws is not None


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri, ping_timeout=None)
        except Exception as e:
            print(f"Websocket connection error: {e}")

    async def send_message(self, message: AgentMessage):
        max_retries = 3
        retries = 0

        while retries < max_retries:
            if _ws_is_open(self.websocket):
                try:
                    await self.websocket.send(message)
                    break

                except ConnectionClosed as e:
                    logger.error(e)
                    retries += 1
                    await asyncio.sleep(3)
                except (TypeError, Exception) as e:
                    raise
            else:
                retries += 1
                await asyncio.sleep(3)
                await self.connect()

        if retries >= max_retries:
            print("Failed to send message after several attempts.")

    async def receive_message(self) -> AgentMessage:
        max_retries = 3
        retries = 0

        while retries < max_retries:
            if _ws_is_open(self.websocket):
                try:
                    message = await self.websocket.recv()
                    message = AgentMessage.model_validate_json(message)
                    return message
                except (ConnectionClosed, RuntimeError) as e:
                    logger.error(e)
                    retries += 1
                    await asyncio.sleep(3)
                except (ValidationError, Exception) as e:
                    raise

            else:
                retries += 1
                await asyncio.sleep(3)
                await self.connect()
                print("reconnect succeed!")

        if retries >= max_retries:
            print("Failed to receive message after several attempts.")

    async def close(self):
        await self.websocket.close()
