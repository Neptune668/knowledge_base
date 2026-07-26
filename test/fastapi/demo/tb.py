import time

#同步
def download(i: int):
    print(f"开始下载...{i}")
    time.sleep(1)  # 模拟异步I/O
    print(f"{i}下载完成!")


def run(i):
    for i in range(1, i + 1):
        download(i)


if __name__ == '__main__':
    start = time.time()
    run(3)  # 并发运行 3 个任务
    end = time.time()
    print(f"下载文件总共用时间: {end - start:.2f}秒")
# 这个写法不好
# def sync_test(i: int):
#     start = time.time()
#     for i in range(1, i + 1):
#         print(f"开始下载...{i}")
#         time.sleep(1)
#         print(f"{i}下载完成!")
#     end = time.time()
#     print(f"下载文件总共用时间:{end - start}")
#
#
# if __name__ == '__main__':
#     sync_test(3)

# import time
#
#
# def download_file(name):
#     print(f"开始{name}下载文件")
#     time.sleep(2)
#     print(f"下载{name}完成")
#
# time_begin = time.time()
#
# download_file("文件1")
# download_file("文件2")
# download_file("文件3")
#
# time_end = time.time()
#
# print(f"下载总耗时{time_end - time_begin}")
