import time

from telethon import TelegramClient

API_HASH = "???????"
API_ID = 00000000
CHAN = "?????"
PROXY = ("http", "127.0.0.1", 7890)
SESSION_NAME = "?????????????"


async def chat_cleanup(chat):
    """cleanup all messages in a chat"""
    # good to use get_input_entity if you will reuse username a lot...
    chat = await client.get_entity(chat)
    # chat = await client.get_input_entity(chat)
    messages = await client.get_messages(chat, 1000)
    await client.delete_messages(chat, messages)


async def chat_forward(chat_src, chat_dst):
    """forward all messages from chat_src to chat_dst"""
    chat_src = await client.get_entity(chat_src)
    chat_dst = await client.get_entity(chat_dst)

    # forward_messages has this limit (get_messages api do chunk itself...)
    chunk_size = 100
    messages = await client.get_messages(chat_src, 1000)
    messages = messages[::-1]
    message_chunks = [messages[i : i + chunk_size] for i in range(0, len(messages), chunk_size)]
    for message_chunk in message_chunks:
        await client.forward_messages(chat_dst, message_chunk)
    time.sleep(30)


async def chat_count(chat):
    print(len(await client.get_message(chat, 1000)))


client = TelegramClient(SESSION_NAME, API_ID, API_HASH, proxy=PROXY)
client.start()

with client:
    # client.loop.run_until_complete(chat_cleanup(CHAN))
    client.loop.run_until_complete(chat_forward("me", CHAN))
