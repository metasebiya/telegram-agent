# main.py
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from graph import get_agent_app

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()

@dp.message(Command("approve"))
async def cmd_approve(message: types.Message):
    thread_id = str(message.chat.id)
    config = {"configurable": {"thread_id": thread_id}}
    
    # Use 'async with' to get the compiled app correctly
    async with get_agent_app() as app:
        await app.aupdate_state(config, {"is_approved": True}, as_node="approval")
        state = await app.aget_state(config)
        draft = state.values.get("draft_content")
        
        if draft:
            await bot.send_message(os.getenv("CHANNEL_ID"), draft)
            await message.answer("🚀 Published!")

@dp.message(F.text & ~F.text.startswith('/'))
async def handle_topic(message: types.Message):
    thread_id = str(message.chat.id)
    config = {"configurable": {"thread_id": thread_id}}
    
    await message.answer("🤖 Brainstorming...")
    
    async with get_agent_app() as app:
        input_data = {"messages": [HumanMessage(content=message.text)]}
        final_draft = ""
        
        async for event in app.astream(input_data, config, stream_mode="values"):
            if "draft_content" in event:
                final_draft = event["draft_content"]
        
        await message.answer(f"📝 **DRAFT:**\n\n{final_draft}\n\nUse /approve to post.")
@dp.message(Command("history"))
async def cmd_history(message: types.Message):
    thread_id = str(message.chat.id)
    config = {"configurable": {"thread_id": thread_id}}
    
    async with get_agent_app() as app:
        # Fetch the last 5 snapshots of this conversation
        history = []
        async for state in app.aget_state_history(config, limit=5):
            # We look for states that have content in them
            content = state.values.get("draft_content", "No draft yet")
            # Truncate for the message
            summary = (content[:50] + '...') if len(content) > 50 else content
            history.append(f"🆔 `{state.config['configurable']['checkpoint_id']}`\n📝 {summary}")

        if not history:
            await message.answer("No history found for this thread.")
        else:
            await message.answer("🕒 **Recent Snapshots:**\n\n" + "\n\n".join(history))
@dp.message(Command("rewind"))
async def cmd_rewind(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Please provide a checkpoint ID.\nUsage: `/rewind <id>`")
        return

    target_checkpoint_id = args[1]
    thread_id = str(message.chat.id)
    
    # Configuration to find the SPECIFIC past moment
    past_config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_id": target_checkpoint_id
        }
    }

    async with get_agent_app() as app:
        # 1. Fetch the state from that specific point in time
        past_state = await app.aget_state(past_config)
        
        if not past_state.values:
            await message.answer("❌ Could not find that checkpoint.")
            return

        # 2. "Fork" the history: Update the CURRENT state with the PAST values
        # This creates a new checkpoint that is a copy of the old one
        current_config = {"configurable": {"thread_id": thread_id}}
        await app.aupdate_state(current_config, past_state.values)
        
        await message.answer(f"⏪ **Rewound!** State restored to:\n\n{past_state.values.get('draft_content')}")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())