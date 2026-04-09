from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextMessage, TextSendMessage
import datetime
import os

app = Flask(__name__)

# 設定鑰匙
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 簡單的資料紀錄
user_data = {
    "streak": 0,
    "last_check_in": None
}

# 考試日期（請根據你的考試日期調整，這裡預設為 2026 社工師考試大概日期）
EXAM_DATE = datetime.date(2026, 7, 25)

@app.route("/", methods=['GET'])
def index():
    return '情勒馬鈴薯 2.0 運作中...'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# --- 處理照片（驗收筆記） ---
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    today = datetime.date.today()
    days_left = (EXAM_DATE - today).days
    
    if user_data["last_check_in"] != today:
        user_data["streak"] += 1
        user_data["last_check_in"] = today
        streak = user_data["streak"]
        
        # 基礎回應
        reply_msg = f"算你識相，今天的筆記我收到了。\n\n🔥 目前連勝：{streak} 天\n📅 距離考試：還有 {days_left} 天"
        
        # 每 10 的倍數天給予鼓勵
        if streak > 0 and streak % 10 == 0:
            reply_msg += f"\n\n🎊 居然連勝 {streak} 天了！看來你還沒廢掉，繼續保持，這幾天可以給自己加個蛋！加油！"
        else:
            reply_msg += "\n\n明天 22:00 前要是沒交照片，你就死定了。😊"
    else:
        reply_msg = "今天已經交過筆記了，快去多寫兩題考古題，別想賴在手機上！"
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

# --- 處理文字（聊天與查詢） ---
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    today = datetime.date.today()
    days_left = (EXAM_DATE - today).days
    streak = user_data["streak"]

    if "倒數" in user_msg or "還有幾天" in user_msg:
        reply_msg = f"現在是 {today}，距離考試還有 {days_left} 天。\n別再算日子了，趕快去讀書比較實在！"
    
    elif "連勝" in user_msg or "幾天了" in user_msg:
        if streak == 0:
            reply_msg = "你目前連勝 0 天。你要不要看看自己在說什麼？快傳筆記照片給我！"
        else:
            reply_msg = f"你已經連勝 {streak} 天了。想要我誇獎你嗎？考上再說吧！"
            
    elif "累" in user_msg or "不想讀" in user_msg:
        reply_msg = "累什麼累？個案比你更累！考上之前你沒有喊累的資格，快去翻開第 50 頁。"
    
    else:
        reply_msg = f"你跟我說「{user_msg}」能幫你拿證照嗎？不能就去讀書，或者傳筆記給我驗收。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    app.run()
