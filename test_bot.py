import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

async def test_connection():
    # Load variables from your .env file
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    channel_id = os.getenv("CHANNEL_ID")

    bot = Bot(token=token)
    
    try:
        print(f"Checking bot info...")
        me = await bot.get_me()
        print(f"Logged in as: @{me.username}")
        
        print(f"Sending test message to channel {channel_id}...")
        await bot.send_message(
            chat_id=channel_id, 
            text="🚀 Hello World! This is a test message from my LangGraph Agent."
        )
        print("✅ Success! Check your Telegram channel.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCommon fixes:")
        print("1. Ensure your bot is an ADMIN in the channel.")
        print("2. Ensure the CHANNEL_ID starts with -100.")
        print("3. Check if your TOKEN is correct in the .env file.")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_connection())