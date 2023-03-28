import asyncio
import telegram

async def main(): #실행시킬 함수명 임의지정
    token = "6007372301:AAEZWipCHU_oaQV7a1Kh_0Ig-ZARlPHjHjs" 
    bot = telegram.Bot(token = token)
    await bot.send_message(chat_id='6102779631',text='창민님 성공했습니다')

asyncio.run(main()) #봇 실행하는 코드
