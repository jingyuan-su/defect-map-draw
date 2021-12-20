import asyncio
import websockets
import json


async def echo(websocket):
    async for mymessage in websocket: 
        event = {
                "type": "error",
               "message": str('dfsdfsfs'),
            }
        await websocket.send(json.dumps(event)) 


async def main():
        async with websockets.serve(echo, 'localhost', 8765) as websocket:
            await asyncio.Future() # run forever


if __name__ == "__main__":
    #  mytest_path = os.path.join(os.path.expanduser('~'), 'Desktop\\test')
    #  detect_new_file(mytest_path)
    asyncio.run(main())
