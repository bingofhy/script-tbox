import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# 读取 CSV 文件
df = pd.read_csv('tboxmn.csv')
df = df.drop_duplicates(subset=['time'], keep='last')

# 将time列转换为datetime类型
df['time'] = pd.to_datetime(df['time'])

# 初始化图表
fig, ax = plt.subplots()
line, = ax.plot([], [], marker='o')
hline = ax.axhline(y=df['value'].iloc[-1], color='r', linestyle='--')
mean_line, = ax.plot([], [], color='orange', linestyle='--', marker='o')

# 添加绿色竖线
vline_1min = ax.axvline(x=datetime.now() - timedelta(minutes=1), color='green', linestyle='--')
vline_2min = ax.axvline(x=datetime.now() - timedelta(minutes=2), color='green', linestyle='--')

# 将当前值放在图标的中间最上方
text = ax.text(0.5, 0.95, '', transform=ax.transAxes, color='red', fontsize=14, weight='bold', va='top', ha='center')

ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.set_title('Value over Time (Past 3 Minutes)')
plt.xticks(rotation=45)
plt.tight_layout()

# 设置横轴刻度间隔为10秒
ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))


def init():
    ax.set_xlim(datetime.now() - timedelta(minutes=3), datetime.now())
    ax.set_ylim(df['value'].min() - 5, df['value'].max() + 5)

    return line, hline, mean_line, text, vline_1min, vline_2min


def update(frame):
    now = datetime.now()
    three_minutes_ago = now - timedelta(minutes=3)
    one_minute_ago = now - timedelta(minutes=1)
    two_minutes_ago = now - timedelta(minutes=2)
    
    # 更新DataFrame
    global df
    df = pd.read_csv('tboxmn.csv')
    df = df.drop_duplicates(subset=['time'], keep='last')
    df['time'] = pd.to_datetime(df['time'])
    df = df[df['time'] >= three_minutes_ago]
    
    line.set_data(df['time'], df['value'])
    ax.set_xlim(three_minutes_ago, now)
    ax.set_ylim(df['value'].min() - 5, df['value'].max() + 5)

    # 更新竖线位置
    vline_1min.set_xdata([one_minute_ago])
    vline_2min.set_xdata([two_minutes_ago])
    
    if not df.empty:
        latest_value = df['value'].iloc[-1]
        hline.set_ydata([latest_value])
        text.set_text(f'{latest_value:.2f}')
        
        # 计算过去3分钟的移动平均值
        df['mean_value'] = df['value'].rolling(window=30, min_periods=1).mean()
        mean_line.set_data(df['time'], df['mean_value'])
    
    return line, hline, mean_line, text, vline_1min, vline_2min


ani = FuncAnimation(fig, update, frames=None, init_func=init, blit=True, interval=500, cache_frame_data=False)

plt.show()