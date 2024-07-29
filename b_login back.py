import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, send_file, redirect, url_for, request
from flask_socketio import SocketIO
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import io
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 设置你的密钥
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 假设有一个简单的用户数据库
users = {'admin': {'password': 'xxx'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f'<User: {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return 'Bad login'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/plot.png')
@login_required
def plot_png():
    update_plot()
    buf = io.BytesIO()
    try:
        fig.canvas.draw()  # 强制重新绘制图表
    except Exception as e:
        print(f"Error during drawing: {e}")
    fig.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def update_data():
    while True:
        socketio.sleep(1)  # 调整为1秒，减少更新频率
        socketio.emit('update', {'time': datetime.now().isoformat()})

@socketio.on('start')
def handle_start():
    socketio.start_background_task(update_data)

# 初始化图表
fig, ax = plt.subplots(figsize=(10, 5.5))
line, = ax.plot([], [], marker='o')
hline = ax.axhline(y=0, color='r', linestyle='--')
mean_line, = ax.plot([], [], color='orange', linestyle='--', marker='o')
vline_1min = ax.axvline(x=datetime.now() - timedelta(minutes=1), color='green', linestyle='--')
vline_2min = ax.axvline(x=datetime.now() - timedelta(minutes=2), color='green', linestyle='--')
text = ax.text(0.5, 0.95, '', transform=ax.transAxes, color='red', fontsize=14, weight='bold', va='top', ha='center')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.set_title('Value over Time (Past 3 Minutes)')
plt.xticks(rotation=45)
plt.tight_layout()
ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

def init_plot():
    ax.set_xlim(datetime.now() - timedelta(minutes=3), datetime.now())
    ax.set_ylim(-10, 10)  # 初始Y轴范围

def update_plot():
    now = datetime.now()
    three_minutes_ago = now - timedelta(minutes=3)
    one_minute_ago = now - timedelta(minutes=1)
    two_minutes_ago = now - timedelta(minutes=2)

    # 更新DataFrame
    try:
        df = pd.read_csv('tboxmn.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['time', 'value'])

    df = df.drop_duplicates(subset=['time'], keep='last')
    df['time'] = pd.to_datetime(df['time'])
    df = df[df['time'] >= three_minutes_ago]

    line.set_data(df['time'], df['value'])
    ax.set_xlim(three_minutes_ago, now)

    if not df.empty:
        y_min = df['value'].min() - 5
        y_max = df['value'].max() + 5
        if pd.notna(y_min) and pd.notna(y_max):
            ax.set_ylim(y_min, y_max)

        latest_value = df['value'].iloc[-1]
        hline.set_ydata([latest_value])
        text.set_text(f'{latest_value:.2f}')

        # 计算过去3分钟的移动平均值
        df['mean_value'] = df['value'].rolling(window=30, min_periods=1).mean()
        mean_line.set_data(df['time'], df['mean_value'])

    # 更新竖线位置
    vline_1min.set_xdata([one_minute_ago])
    vline_2min.set_xdata([two_minutes_ago])

init_plot()  # 在应用启动时初始化图表

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Starting SocketIO...")
    socketio.run(app, host='0.0.0.0', debug=True)
    print("Application running.")