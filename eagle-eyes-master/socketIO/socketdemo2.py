import json
import websockets
import asyncio
import pandas as pd

'''
···
python websocket库官方文档
'''
async def socket_server(websocket,port):
    a = await websocket.recv()
    print(f"{a}")
    data = [['apple', 'egg', 'watermelon'],['red', 'yellow', 'green'],[30, 40, 50]]

    # df1 = pd.DataFrame(data)
    # df1 = df1.to_json
    data = json.dumps(data)
    await websocket.send(data)


start_server = websockets.serve(socket_server,'localhost',8766)
'''
摘自 官方文档
loop.run_until_complete(future)
Run until the future (an instance of Future) has completed.
If the argument is a coroutine object it is implicitly scheduled to run as a asyncio.Task.
Return the Future’s result or raise its exception.
'''
asyncio.get_event_loop().run_until_complete(start_server)
'''
开始接受连接，直到取消协程。取消serve_forever任务会导致服务器关闭。
This method can be called if the server is already accepting connections.
Only one serve_forever task can exist per one Server object.
'''
asyncio.get_event_loop().run_forever()
