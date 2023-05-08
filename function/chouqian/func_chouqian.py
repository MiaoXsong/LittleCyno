import asyncio

from get_qianwen_by_web import get_qianwen_by_web_main


def getQianwenByWeb():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_qianwen_by_web_main())
    loop.close()


getQianwenByWeb()
