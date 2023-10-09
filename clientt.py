# import asyncio
import requests


class Client:

    def __init__(self, server_host="127.0.0.1", server_port=8000):
        self._server_host = server_host
        self._server_port = server_port

    def send(self, message=""):
        pass


# import logging
# import sys
# import asyncio
# from asyncio.streams import StreamReader, StreamWriter
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler(stream=sys.stdout))
#
#
# async def client_connected(reader: StreamReader, writer: StreamWriter):
#     address = writer.get_extra_info('peername')
#     logger.info('Start serving %s', address)
#
#     while True:
#         data = await reader.read(1024)
#         if not data:
#             break
#         print("data: {}".format(data.decode('utf8')))
#         writer.write(data)
#         await writer.drain()
#
#     logger.info('Stop serving %s', address)
#     writer.close()
#
#
# async def main(host: str, port: int):
#     srv = await asyncio.start_server(
#         client_connected, host, port)
#
#     async with srv:
#         await srv.serve_forever()
#
#
# if __name__ == '__main__':
#     asyncio.run(main('127.0.0.1', 8000))

# import asyncio
#
# async def send_message():
#     reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
#     while True:
#         message = input("Введите сообщение (или 'q' для выхода): ")
#         if message.lower() == 'q':
#             break
#         writer.write(message.encode())
#         await writer.drain()
#         response = await reader.read(100)
#         print(f"Ответ сервера: {response.decode()}")
#
#     print("Закрыто соединение")
#     writer.close()
#     await writer.wait_closed()
#
# async def main():
#     await send_message()
#
if __name__ == "__main__":
    response = requests.get("http://localhost:8000/test")
    print(response)
