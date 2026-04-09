from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
import datetime
import os

app = Flask(__name__)

# --- 已經從環境變數填入你的鑰匙，保護隱私 ---
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    print("錯誤：找不到 LINE 鑰匙 (Secret/Token) 環境變數。請在 Render 設定中確認。")
    app.stop() # 終止程式

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 模擬簡單的資料庫（因為是免費平台，重啟後紀錄會歸零。要永久儲存需連結資料庫，這步先簡化）
user_data = {
    "streak": 0,
    "last_check_in": None
}

@app.route("/", methods=['GET'])
def index():
    return '情勒馬鈴薯運作中...'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 當你傳送照片（ImageMessage）時執行的邏輯
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    today = datetime.date.today()
    
    # 判斷是否為今天第一次傳照片
    if user_data["last_check_in"] != today:
        user_data["streak"] += 1
        user_data["last_check_in"] = today
        reply_msg = f"算你識相，今天的筆記我收到了。\n連勝天數：{user_data['streak']} 天。\n明天 22:00 前要是沒交照片，你就死定了。😊"
    else:
        reply_msg = "今天已經交過筆記了，別想拿舊圖唬弄我，快去多讀一點書！"
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    app.run()