import time
import os
import datetime
import pandas as pd
import requests  # 新增：用于检测网页
from ping3 import ping
import matplotlib.pyplot as plt

# 1. 配置：检测目标（增加 URL 字段）
TARGETS = [
    {"name": "百度", "host": "www.baidu.com", "url": "https://www.baidu.com"},
    {"name": "阿里云", "host": "www.aliyun.com", "url": "https://www.aliyun.com"},
    {"name": "GitHub", "host": "github.com", "url": "https://github.com"},
    {"name": "学校官网", "host": "www.xxx.edu.cn", "url": "http://www.xxx.edu.cn"}
]

# 2. 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def check_availability(target):
    """检测网页可用性：返回 是否成功、响应时间、状态码"""
    name = target['name']
    url = target['url']
    print(f"正在深度巡检: {name}...", end="")

    try:
        start_time = time.time()
        # 模拟浏览器访问，timeout=5 防止卡死
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        end_time = time.time()

        # 计算响应时间（毫秒）
        duration = round((end_time - start_time) * 1000, 2)

        if response.status_code == 200:
            print(f" 成功! 响应码: 200, 耗时: {duration}ms")
            return True, duration, 200
        else:
            print(f" 异常! 响应码: {response.status_code}")
            return False, duration, response.status_code

    except Exception as e:
        print(f" 故障! 无法连接到网页: {str(e)[:20]}...")
        return False, 0, "Error"


def run_task():
    results = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for target in TARGETS:
        is_up, duration, code = check_availability(target)
        results.append({
            "时间": now_str,
            "目标": target['name'],
            "状态": "正常" if is_up else "故障",
            "响应耗时(ms)": duration,
            "HTTP状态码": code
        })

        # --- 新增告警触发逻辑 ---
        if not is_up:
            send_alert(target['name'], code, f"网页响应异常，请检查服务器状态")

    # 3. 数据保存
    df = pd.DataFrame(results)
    log_file = "web_inspection_log.csv"
    df.to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file), encoding='utf_8_sig')

    # 4. 绘图展示（展示响应耗时）
    plt.figure(figsize=(10, 6))
    colors = ['skyblue' if s == "正常" else 'salmon' for s in df['状态']]
    plt.bar(df['目标'], df['响应耗时(ms)'], color=colors)
    plt.title(f"Web 业务可用性巡检 ({now_str})")
    plt.ylabel("响应耗时 (ms)")

    # 在柱状图上方标注状态码
    for i, val in enumerate(df['HTTP状态码']):
        plt.text(i, df['响应耗时(ms)'][i], f"Code:{val}", ha='center', va='bottom')

    plt.savefig("web_report.png")
    print(f"\n--- 深度巡检完成 ---")
    print(f"新报告已生成: web_report.png")

    # 1. 这是一个“食谱”：告诉 Python 什么是 send_alert


def send_alert(name, status_code, msg=""):
    """向飞书机器人推送告警消息"""
    # ！！！请确保这里是你的飞书 Webhook 链接 ！！！
    webhook_url = "[https://open.feishu.cn/xxx/请替换为你自己的链接](https://open.feishu.cn/xxx/请替换为你自己的链接)"

    # 飞书必须要这个 "msg_type": "text" 标签
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"项目巡检告警\n"
                    f"检测目标: {name}\n"
                    f"状态代码: {status_code}\n"
                    f"详情描述: {msg}\n"
                    f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }

    try:
        print(f"--- 正在尝试发送告警到机器人... ---")
        # 发送请求并接住回执
        response = requests.post(webhook_url, json=payload, timeout=5)

        # 打印回执，方便我们观察
        print(f"--- 机器人返回的消息: {response.text} ---")

        if response.status_code == 200:
            print(f"--- 告警消息已推送至机器人 ---")
        else:
            print(f"--- 推送异常，HTTP状态码: {response.status_code} ---")

    except Exception as e:
        print(f"告警推送出现代码错误: {e}")

if __name__ == "__main__":
    run_task()
    # 到了这里，Python 已经读过上面的“食谱”了
    # 所以它现在认识 send_alert 是谁了，红线就会消失
    # ... 检测逻辑 ...
