import asyncio
import concurrent.futures

from core.client import Client

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    thread_pool = concurrent.futures.ThreadPoolExecutor()
    client = Client()
    loop.run_in_executor(thread_pool, client.connect())
    loop.create_task(client.get_message_from_chat())
    loop.create_task(client.check_limit_messages())
    loop.create_task(client.check_status())
    pending_tasks = asyncio.all_tasks(loop)
    group_tasks = asyncio.gather(*pending_tasks)
    thread_pool.shutdown()
    loop.run_until_complete(group_tasks)
    loop.close()
