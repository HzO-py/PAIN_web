from celery import shared_task
import time

def loop(msg,num):
    for i in range(num):
        time.sleep(1)
        print(msg*i)

@shared_task
def analyze_video(msg):
    # 在这里执行您的函数
    print('analyze_video-----------')
    loop(msg,3)
    # 使用 Django Channels 或其他实时通信库向前端发送结果