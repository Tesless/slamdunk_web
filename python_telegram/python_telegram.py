import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

# 토큰 불러오는부분
with open("./token.txt") as f:
    lines = f.readlines()
    token = lines[0].strip()

# chat id 불러오는부분
with open("./chat_id.txt") as f:
    lines = f.readlines()
    chat_id = lines[0].strip()

# 토큰과 chat id 불러왓는지 테스트
print(token, chat_id)

# 로그 부분
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="슬램덩크 봇에 온걸 환영한다!")


async def khj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="슬램덩크 김혜진 화이팅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
    # 텔레그램 봇 채팅방에서 /start 명령을 실행햇을때 이 함수 호출    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # 텔레그램 봇 채팅방에서 /khj 명령을 실행햇을때 이 함수 호출    
    khj_handler = CommandHandler('khj', khj)
    application.add_handler(khj_handler)
    
    # 채팅방 말을 그대로 따라하는 코드
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    
    application.run_polling()