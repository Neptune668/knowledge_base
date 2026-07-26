import asyncio
import time


# 下面代码阻塞了
# async def sync_test(i: int):
#     start = time.time()
#     for i in range(1, i + 1):
#         print(f"开始下载...{i}")
#         time.sleep(1)
#         print(f"{i}下载完成!")
#     end = time.time()
#     print(f"下载文件总共用时间:{end - start}")

# async def download(i: int):
#     print(f"开始下载...{i}")
#     await asyncio.sleep(1)  # ✅ 释放控制权，让事件循环处理其他任务
#     print(f"{i}下载完成!")
#
#
# async def sync_test(i: int):
#     tasks = [download(d) for d in range(i,i+1)]
#     await asyncio.gather(*tasks)
#
#
# if __name__ == '__main__':
#     start = time.time()
#     asyncio.run(sync_test(3))
#     end = time.time()
#     print(f"下载文件总共用时间: {end - start:.2f}秒")

import asyncio
import time

async def download(i: int):
    print(f"开始下载...{i}")
    await asyncio.sleep(1)          # 模拟异步I/O
    print(f"{i}下载完成!")

async def sync_test(n: int):        # n 表示任务数量
    tasks = [download(i) for i in range(1, n + 1)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    start = time.time()
    asyncio.run(sync_test(3))       # 并发运行 3 个任务
    end = time.time()
    print(f"下载文件总共用时间: {end - start:.2f}秒")
#标准实例
# import asyncio
# import time
#
# async def download(i: int):
#     print(f"开始下载...{i}")
#     await asyncio.sleep(1)          # ✅ 释放控制权，让事件循环处理其他任务
#     print(f"{i}下载完成!")
#
# async def main():
#     tasks = [download(i) for i in range(1, 4)]
#     start = time.time()
#     await asyncio.gather(*tasks)    # 并发执行所有任务
#     end = time.time()
#     print(f"下载文件总共用时间: {end - start:.2f}秒")
#
# if __name__ == '__main__':
#     asyncio.run(main())