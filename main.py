import time
import os
import datetime
import pandas as pd
from ping3 import ping
import matplotlib.pyplot as plt

# 1. 配置：你想检测谁？
TARGETS = {
    "百度": "www.baidu.com",
    "阿里云": "www.aliyun.com",
    "GitHub": "github.com",
    "本地网关": "192.168.1.1"  # 请确保这个地址在你环境能通，或者换成常用网站
}

# 2. 解决中文显示问题（针对 Windows PyCharm）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def check_service(name, host):
    """连续检测3次，只有全部失败才报警"""
    print(f"正在检查: {name} ({host})...", end="")
    for i in range(3):
        delay = ping(host, unit='ms', timeout=2)
        if delay is not None:
            print(f" 成功! 延迟: {delay:.2f}ms")
            return True, round(delay, 2)
        time.sleep(1)
    print(" 失败! (三次重试均无响应)")
    return False, 0


def run_task():
    results = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 开始遍历检测
    for name, host in TARGETS.items():
        is_up, delay = check_service(name, host)
        results.append({
            "时间": now_str,
            "目标": name,
            "状态": "正常" if is_up else "故障",
            "延迟(ms)": delay
        })

    # 3. 数据处理与保存
    df = pd.DataFrame(results)
    log_file = "inspection_log.csv"
    # 如果文件不存在则写入表头，存在则追加
    df.to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file), encoding='utf_8_sig')

    # 4. 绘图展示
    plt.figure(figsize=(10, 6))
    colors = ['green' if s == "正常" else 'red' for s in df['状态']]
    plt.bar(df['目标'], df['延迟(ms)'], color=colors)
    plt.title(f"网络巡检日报 ({now_str})")
    plt.ylabel("延迟 (ms)")
    plt.savefig("daily_report.png")
    print(f"\n--- 巡检完成 ---")
    print(f"日志已更新: {log_file}")
    print(f"图表已生成: daily_report.png")


if __name__ == "__main__":
    run_task()