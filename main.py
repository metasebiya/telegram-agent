import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from langchain_core.messages import HumanMessage

# Import your graph and state from the other files
from graph import app
from state import AgentState

load_dotenv()

# Configuration
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") # The ID of your public channel

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! Send me a topic, and I'll draft a post for your channel. "
                         "You'll need to /approve it before it goes live.")

@dp.message(Command("approve"))
async def cmd_approve(message: types.Message):
    """
    This is the HUMAN-IN-THE-LOOP trigger.
    It resumes the graph after the 'approval' interrupt.
    """
    thread_id = str(message.from_user.id)
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if the graph is actually waiting for us
    state = await app.aget_state(config)
    if not state.next:
        return await message.answer("No pending posts to approve.")

    # RESUME the graph: 
    # We update the state to 'approved=True' and tell it to continue
    await app.aupdate_state(config, {"is_approved": True}, as_node="approval")
    
    # Kick the graph back into action
    async for event in app.astream(None, config):
        if "publisher" in event:
            content = event["publisher"]["draft_content"]
            # Actually post to the public channel
            await bot.send_message(chat_id=CHANNEL_ID, text=content)
            await message.answer("✅ Post published to the channel!")

@dp.message(F.text)
async def handle_topic(message: types.Message):
    """
    Accepts a topic and starts the 'Content Creator' node.
    """
    thread_id = str(message.from_user.id)
    config = {"configurable": {"thread_id": thread_id}}
    
    await message.answer("🤖 Brainstorming your post... please wait.")
    
    # Start the graph
    inputs = {"messages": [HumanMessage(content=message.text)], "is_approved": False}
    
    async for event in app.astream(inputs, config):
        if "creator" in event:
            draft = event["creator"]["draft_content"]
            await message.answer(
                f"📝 **DRAFT GENERATED:**\n\n{draft}\n\n"
                f"Type /approve to post it, or send a new message to revise it."
            )

# --- MAIN LOOP ---

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())