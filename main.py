import asyncio
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import sqlite3


load_dotenv()

config = {
    'prefix': '!',
    'channel_id': 879019933957255208
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

# Глобальные переменные для хранения ID сообщений
message_id = None
start_message_idm = None
start_message_idt = None
completed_count = 0

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    send_message.start()  # Запускаем задачу отправки сообщения


@tasks.loop(minutes=1)  # Проверяем время каждую минуту
async def send_message():
    global message_id  # Используем глобальную переменную
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    if moscow_time.hour == 17:  # Отправляем сообщение в 11:57 МСК
        channel = bot.get_channel(config['channel_id'])
        if channel:
            embed = await create_initial_embed()
            view = MyView()
            message = f'<@&879192631060606998>'  # Добавляем пинг роли в начало сообщения
            sent_message = await channel.send(message, embed=embed, view=view)
            global message_id
            message_id = sent_message.id  # Сохраняем ID отправленного сообщения
        else:
            print(f"Не удалось найти канал с ID {config['channel_id']}")


async def create_initial_embed():
    # Подключаемся к базе данных и получаем время отката для каждого контракта
    conn = sqlite3.connect('escdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT Rollback FROM Meet WHERE ROWID = (SELECT MAX(ROWID) FROM Meet)')
    meat_rollback_row = cursor.fetchone()
    meat_rollback_time = meat_rollback_row[0] if meat_rollback_row and meat_rollback_row[0] else 'Активен'

    cursor.execute('SELECT Rollback FROM Trash WHERE ROWID = (SELECT MAX(ROWID) FROM Trash)')
    trash_rollback_row = cursor.fetchone()
    trash_rollback_time = trash_rollback_row[0] if trash_rollback_row and trash_rollback_row[0] else 'Активен'

    cursor.execute('SELECT Rollback FROM Circuits WHERE ROWID = (SELECT MAX(ROWID) FROM Circuits)')
    circuits_rollback_row = cursor.fetchone()
    circuits_rollback_time = circuits_rollback_row[0] if circuits_rollback_row and circuits_rollback_row[0] else 'Активен'

    cursor.execute('SELECT Rollback FROM BNB WHERE ROWID = (SELECT MAX(ROWID) FROM BNB)')
    bnb_rollback_row = cursor.fetchone()
    bnb_rollback_time = bnb_rollback_row[0] if bnb_rollback_row and bnb_rollback_row[0] else 'Активен'

    conn.close()

    # Определяем текущие даты для сравнения
    current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')

    # Функция для проверки времени отката
    def check_rollback(rollback_time):
        if rollback_time == 'Активен':
            return rollback_time
        try:
            rollback_dt = datetime.strptime(rollback_time, '%Y-%d-%m %H:%M')
            rollback_dt = pytz.timezone('Europe/Moscow').localize(rollback_dt)
            if rollback_dt <= datetime.now(pytz.timezone('Europe/Moscow')):
                return 'Доступно'
            else:
                return rollback_time
        except ValueError:
            return 'Активен'

    # Проверяем время отката
    meat_status = check_rollback(meat_rollback_time)
    trash_status = check_rollback(trash_rollback_time)
    circuits_status = check_rollback(circuits_rollback_time)
    bnb_status = check_rollback(bnb_rollback_time)

    # Создаем embed-сообщение с информацией о времени отката
    embed = discord.Embed(
        description=f"# КОНТРАКТЫ \n## 🥩 Мясо - \n🥩 Откатится - {meat_status}\n## ♻️ Мусор - \n♻️ Откатится - {trash_status}\n## 💾 Схемы - {circuits_status} \n## ⚒️ ЛНС - {bnb_status}\n",
        color=0x50FFBC)
    return embed

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None

    @discord.ui.button(label="МЯСО", style=discord.ButtonStyle.secondary)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_embed = discord.Embed(title="МЯСО", description="Записаться на контракт?", color=0x50FFBC)
        new_view = MeatView()
        await interaction.response.send_message(embed=new_embed, view=new_view, ephemeral=True)

    @discord.ui.button(label="МУСОР", style=discord.ButtonStyle.secondary)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_embed = discord.Embed(title="МУСОР", description="Записаться на контракт?", color=0x50FFBC)
        new_view = TrashView()
        await interaction.response.send_message(embed=new_embed, view=new_view, ephemeral=True)

    @discord.ui.button(label="СХЕМЫ", style=discord.ButtonStyle.secondary)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_embed = discord.Embed(title="СХЕМЫ", description="Запустить сбор?", color=0x50FFBC)
        new_view = CircuitsView()
        await interaction.response.send_message(embed=new_embed, view=new_view, ephemeral=True)

    @discord.ui.button(label="ЛНС", style=discord.ButtonStyle.secondary)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_embed = discord.Embed(title="ЛНС", description="Запустить контракт?", color=0x50FFBC)
        new_view = BNBView()
        await interaction.response.send_message(embed=new_embed, view=new_view, ephemeral=True)

class CircuitsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None

    @discord.ui.button(label="Запустить", style=discord.ButtonStyle.secondary)
    async def Circuitsoption(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = bot.get_channel(config['channel_id'])
        embed = discord.Embed(description="# 💾 Схемы \nРаботники - ", color=0x50FFBC)
        message = f'<@&879192631060606998>\n'  # Добавляем пинг роли в начало сообщения
        await channel.send(message, embed=embed, view=CircuitsView2())



class CircuitsView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.user_count = 0
        self.max_users = 2

    @discord.ui.button(label="Записаться", style=discord.ButtonStyle.secondary)
    async def Circuitsoption(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        original_message = interaction.message
        user_mention = interaction.user.mention

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        # Проверяем, записан ли уже пользователь
        cursor.execute('SELECT Worker FROM Circuits WHERE ContractID = ?', (message_id,))
        existing_users = {row[0] for row in cursor.fetchall()}

        if user_mention in existing_users:
            await interaction.followup.send("Вы уже записаны на контракт.", ephemeral=True)
            return

        if self.user_count < self.max_users:
            # Add the new user mention to the database
            cursor.execute("INSERT INTO Circuits (Worker, ContractID) VALUES (?, ?)", (user_mention, message_id))
            conn.commit()

            # Find the current "Работники - " line and append the new user mention
            new_description = original_message.embeds[0].description + f" {user_mention}"
            new_embed = discord.Embed(title=original_message.embeds[0].title, description=new_description, color=0x50FFBC)

            # Increment the user count
            self.user_count += 1

            # Edit the message with the new embed
            await original_message.edit(embed=new_embed)

            # Check if the max user limit is reached
            if self.user_count >= self.max_users:
                # Create a new view with the "Запустить" button
                new_view = StartCircuitsView(message_id=message_id)
                await original_message.edit(view=new_view)
        else:
            await interaction.followup.send("Все места уже заняты.", ephemeral=True)

class StartCircuitsView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)  # Set timeout to None
        self.message_id = message_id

    @discord.ui.button(label="Запустить", style=discord.ButtonStyle.secondary)
    async def start_circuits(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_mention = interaction.user.mention
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        # Проверяем, записан ли уже пользователь
        cursor.execute('SELECT Worker FROM Circuits WHERE ContractID = ?', (self.message_id,))
        existing_users = {row[0] for row in cursor.fetchall()}

        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')
        end_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=4)).strftime('%Y-%d-%m %H:%M')

        if user_mention not in existing_users:
            await interaction.response.send_message("Вы не записаны на контракт и не можете его запустить.", ephemeral=True)
            return

        # Update the database with the formatted start and end times
        cursor.execute('UPDATE Circuits SET Start = ?, End = ? WHERE ContractID = ?', (current_time, end_time, self.message_id))
        conn.commit()
        conn.close()

        # Delete the original message
        await interaction.message.delete()

        # Send the new message
        channel = bot.get_channel(config['channel_id'])
        workers_mention = " ".join(existing_users)
        new_message_content = f"Выполняют: {workers_mention}"
        end_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=4)).strftime('%m-%d %H:%M')
        new_embed = discord.Embed(description=f"# 💾 Схемы \n## Контракт запущен\n## Выполнить до: {end_time} ", color=0x50FFBC)
        new_view = EndCircuitsView(message_id=self.message_id)
        await channel.send(new_message_content, embed=new_embed, view=new_view)

class EndCircuitsView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.completed_users = set()

    @discord.ui.button(label="Завершил", style=discord.ButtonStyle.secondary)
    async def end_circuits(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_mention = interaction.user.mention
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        # Проверяем, записан ли уже пользователь
        cursor.execute('SELECT Worker FROM Circuits WHERE ContractID = ?', (self.message_id,))
        existing_users = {row[0] for row in cursor.fetchall()}

        if user_mention not in existing_users:
            await interaction.response.send_message("Вы не записаны на контракт и не можете его завершить.", ephemeral=True)
            return

        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')

        # Update the end time for the user
        cursor.execute('UPDATE Circuits SET End = ? WHERE ContractID = ? AND Worker = ?', (current_time, self.message_id, user_mention))
        conn.commit()

        self.completed_users.add(user_mention)
        channel = bot.get_channel(config['channel_id'])

        if len(self.completed_users) == len(existing_users):
            # Set the rollback time when the last user completes the contract
            rollback_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=20)).strftime('%Y-%d-%m %H:%M')
            cursor.execute('UPDATE Circuits SET Rollback = ? WHERE ContractID = ?', (rollback_time, self.message_id))
            conn.commit()

            original_message = await channel.fetch_message(self.message_id)  # Получаем сообщение по ID
            original_embed = original_message.embeds[0]
            original_description_lines = original_embed.description.split('\n')

            # Обновляем строку с "## 💾 Схемы -"
            for i, line in enumerate(original_description_lines):
                if line.startswith("## 💾 Схемы -"):
                    original_description_lines[i] = f"{line.split(' - ')[0]} - Контракт откатится - {rollback_time}"
                    break

            # Собираем обновленное описание
            original_embed.description = '\n'.join(original_description_lines)
            await original_message.edit(embed=original_embed)

            # Increment the Circuits count in the Stat table
            current_month = datetime.now().strftime('%Y-%m')
            for user in existing_users:
                cursor.execute('SELECT Сircuits FROM Stat WHERE Worker = ? AND Month = ?', (user, current_month))
                circuits_row = cursor.fetchone()

                current_value = (circuits_row[0] if circuits_row and circuits_row[0] is not None else 0) + 1

                if circuits_row:
                    cursor.execute('UPDATE Stat SET Сircuits = ? WHERE Worker = ? AND Month = ?', (current_value, user, current_month))
                else:
                    cursor.execute('INSERT INTO Stat (Worker, Month, Сircuits) VALUES (?, ?, ?)', (user, current_month, 1))
                conn.commit()

            # Update or insert into Contracts table
            cursor.execute('SELECT Count FROM Сontracts WHERE Name = "Circuits" AND Month = ?', (current_month,))
            count_row = cursor.fetchone()
            if count_row:
                count = count_row[0] + 1
                cursor.execute('UPDATE Сontracts SET Count = ? WHERE Name = "Circuits" AND Month = ?', (count, current_month))
            else:
                cursor.execute('INSERT INTO Сontracts (Name, Month, Count) VALUES ("Circuits", ?, 1)', (current_month,))
            conn.commit()

            await interaction.message.delete()
            await interaction.response.send_message("Контракт завершён!", ephemeral=True)
        else:
            await interaction.response.send_message("Вы завершили контракт. Ожидание остальных участников...", ephemeral=True)

        conn.close()


class MeatView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None

    @discord.ui.button(label="Записаться", style=discord.ButtonStyle.secondary)
    async def meat_option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        # Проверяем, записан ли уже пользователь
        cursor.execute('SELECT Worker FROM Meet WHERE ContractID = ?', (message_id,))
        existing_users = {row[0] for row in cursor.fetchall()}

        if len(existing_users) < 2:
            if user_ping not in existing_users:
                cursor.execute("INSERT INTO Meet (Worker, ContractID) VALUES (?, ?)", (user_ping, message_id))
                conn.commit()

                # Обновляем изначальное сообщение
                channel = bot.get_channel(config['channel_id'])
                if message_id:
                    message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                    updated_embed = message.embeds[0]
                    description_lines = updated_embed.description.split('\n')

                    # Обновляем только строку с "🥩 Мясо -"
                    for i, line in enumerate(description_lines):
                        if line.startswith("## 🥩 Мясо -"):
                            updated_description = f"{line.split(' - ')[0]} - {', '.join(sorted(existing_users.union({user_ping}))) or 'здесь'}"
                            description_lines[i] = updated_description
                            break

                    # Собираем обновленное описание
                    updated_embed.description = '\n'.join(description_lines)
                    await message.edit(embed=updated_embed)
            else:
                await interaction.response.send_message("Вы уже записаны на контракт.", ephemeral=True)
        else:
            await interaction.response.send_message("Все места уже заняты.", ephemeral=True)

    @discord.ui.button(label="Запустить", style=discord.ButtonStyle.secondary)
    async def meat_option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и проверяем, записан ли пользователь
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Meet WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}
        conn.close()

        # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            current_time = datetime.now(pytz.timezone('Europe/Moscow'))
            end_time = current_time + timedelta(hours=24)

            # Format end_time to string format
            end_time_str = end_time.strftime('%Y-%d-%m %H:%M')

            # Обновляем изначальное сообщение с временем окончания
            channel = bot.get_channel(config['channel_id'])
            if message_id:
                message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                updated_embed = message.embeds[0]
                description_lines = updated_embed.description.split('\n')

                # Удаляем строку с "Откатится" и обновляем строку с "🥩 Мясо -" для добавления времени окончания
                new_description_lines = []
                for line in description_lines:
                    if not line.startswith("🥩 Откатится -"):
                        new_description_lines.append(line)

                for i, line in enumerate(new_description_lines):
                    if line.startswith("## 🥩 Мясо -"):
                        parts = line.split(' - ')
                        if len(parts) > 1:
                            participants = parts[1].strip()
                            updated_description = f"{parts[0]} - {participants} | Контракт закончится - {end_time_str}"
                            new_description_lines[i] = updated_description
                        break

                # Update the embed description with the new lines
                updated_embed.description = '\n'.join(new_description_lines)
                await message.edit(embed=updated_embed)
                # Собираем обновленное описание
                updated_embed.description = '\n'.join(new_description_lines)
                await message.edit(embed=updated_embed)

            # Обновляем время начала и окончания в базе данных
            conn = sqlite3.connect('escdb.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE Meet SET Start = ?, End = ? WHERE ContractID = ?',
                           (current_time, end_time, message_id))
            conn.commit()
            conn.close()

            # Создаем новую embed-сообщение с кнопками
            embed2 = discord.Embed(description="# 🥩 МЯСО \n## КОНТРАКТ ЗАПУЩЕН", color=0x50FFBC)
            view2 = ContractControlView()
            sent_message = await channel.send(embed=embed2, view=view2)
            global start_message_idm
            start_message_idm = sent_message.id  # Сохраняем ID сообщения о запуске контракта


class TrashView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Записаться", style=discord.ButtonStyle.secondary)
    async def trash_option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        # Проверяем, записан ли уже пользователь
        cursor.execute('SELECT Worker FROM Trash WHERE ContractID = ?', (message_id,))
        existing_users = {row[0] for row in cursor.fetchall()}

        if len(existing_users) < 2:
            if user_ping not in existing_users:
                cursor.execute("INSERT INTO Trash (Worker, ContractID) VALUES (?, ?)", (user_ping, message_id))
                conn.commit()

                # Обновляем изначальное сообщение
                channel = bot.get_channel(config['channel_id'])
                if message_id:
                    message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                    updated_embed = message.embeds[0]
                    description_lines = updated_embed.description.split('\n')

                    # Обновляем только строку с "♻️ Мусор -"
                    for i, line in enumerate(description_lines):
                        if line.startswith("## ♻️ Мусор -"):
                            updated_description = f"{line.split(' - ')[0]} - {', '.join(sorted(existing_users.union({user_ping}))) or 'здесь'}"
                            description_lines[i] = updated_description
                            break

                    # Собираем обновленное описание
                    updated_embed.description = '\n'.join(description_lines)
                    await message.edit(embed=updated_embed)
            else:
                await interaction.response.send_message("Вы уже записаны на контракт.", ephemeral=True)
        else:
            await interaction.response.send_message("Все места уже заняты.", ephemeral=True)

    @discord.ui.button(label="Запустить", style=discord.ButtonStyle.secondary)
    async def trash_option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и проверяем, записан ли пользователь
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Trash WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}
        conn.close()

        # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')
            end_time = current_time

            # Обновляем изначальное сообщение с временем окончания
            channel = bot.get_channel(config['channel_id'])
            if message_id:
                message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                updated_embed = message.embeds[0]
                description_lines = updated_embed.description.split('\n')

                # Удаляем строку с "Откатится" и обновляем строку с "♻️ Мусор -" для добавления времени окончания
                new_description_lines = []
                for line in description_lines:
                    if not line.startswith("♻️ Откатится -"):
                        new_description_lines.append(line)

                for i, line in enumerate(new_description_lines):
                    if line.startswith("## ♻️ Мусор -"):
                        parts = line.split(' - ')
                        if len(parts) > 1:
                            participants = parts[1].strip()
                            updated_description = f"{parts[0]} - {participants} | Контракт закончится - {end_time}"
                            new_description_lines[i] = updated_description
                        break

                # Собираем обновленное описание
                updated_embed.description = '\n'.join(new_description_lines)
                await message.edit(embed=updated_embed)

            # Обновляем время начала и окончания в базе данных
            conn = sqlite3.connect('escdb.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE Trash SET Start = ?, End = ? WHERE ContractID = ?',
                           (current_time, end_time, message_id))
            conn.commit()
            conn.close()

            # Создаем новую embed-сообщение с кнопками
            embed2 = discord.Embed(description="# ♻️ МУСОР \n## КОНТРАКТ ЗАПУЩЕН", color=0x50FFBC)
            view2 = View2()
            sent_message = await channel.send(embed=embed2, view=view2)
            global start_message_idt
            start_message_idt = sent_message.id  # Сохраняем ID сообщения о запуске контракта


class SOSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Взять", style=discord.ButtonStyle.secondary)
    async def take_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Meet (Worker, ContractID) VALUES (?, ?)", (user_ping, message_id))
        conn.commit()

        # Обновляем сообщение "SOS"
        embed = interaction.message.embeds[0]
        description = embed.description
        embed.description = f"# 🥩 МЯСО \nОткликнулся(ась) на помощь: {user_ping}"
        await interaction.message.edit(embed=embed, view=None)

class SOSViewT(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Взять", style=discord.ButtonStyle.secondary)
    async def take_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Trash (Worker, ContractID) VALUES (?, ?)", (user_ping, message_id))
        conn.commit()

        # Обновляем сообщение "SOS"
        embed = interaction.message.embeds[0]
        description = embed.description
        embed.description = f"# ♻️ МУСОР \nОткликнулся(ась) на помощь: {user_ping}"
        await interaction.message.edit(embed=embed, view=None)

class ContractControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Завершить", style=discord.ButtonStyle.secondary)
    async def end_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        # Подключаемся к базе данных и проверяем, записан ли пользователь
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Meet WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}

        # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            end_time = datetime.now(pytz.timezone('Europe/Moscow'))

            # Обновляем время завершения в базе данных
            cursor.execute('UPDATE Meet SET End = ? WHERE ContractID = ?',
                           (end_time.strftime('%Y-%d-%m %H:%M'), message_id))
            conn.commit()

            # Обновляем время отката в базе данных
            rollback_time = end_time + timedelta(hours=26)
            cursor.execute('UPDATE Meet SET Rollback = ? WHERE ContractID = ?',
                           (rollback_time.strftime('%Y-%d-%m %H:%M'), message_id))

            # Обновляем изначальное сообщение с новым временем и участниками
            channel = bot.get_channel(config['channel_id'])
            if message_id:
                message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                updated_embed = message.embeds[0]
                description_lines = updated_embed.description.split('\n')

                # Обновляем строку с "🥩 Мясо -" для добавления времени окончания
                new_description_lines = []
                for line in description_lines:
                    if line.startswith("## 🥩 Мясо -"):
                        parts = line.split(' - ')
                        if len(parts) > 1:
                            updated_description = f"{parts[0]} - Контракт откатится - {rollback_time.strftime('%Y-%d-%m %H:%M')}"
                            new_description_lines.append(updated_description)
                    else:
                        new_description_lines.append(line)

                # Собираем обновленное описание
                updated_embed.description = '\n'.join(new_description_lines)
                await message.edit(embed=updated_embed)

            # Удаляем сообщение о запуске контракта
            if start_message_idm:
                start_message = await channel.fetch_message(start_message_idm)
                await start_message.delete()
            current_month = datetime.now().strftime('%Y-%m')
            # Обновление таблицы Contracts
            cursor.execute('SELECT Count FROM Сontracts WHERE Name = "Meet" AND Month = ?', (current_month,))
            count_row = cursor.fetchone()
            if count_row:
                count = count_row[0] + 1
                cursor.execute('UPDATE Сontracts SET Count = ? WHERE Name = "Meet" AND Month = ?',
                               (count, current_month))
            else:
                cursor.execute('INSERT INTO Сontracts (Name, Month, Count) VALUES ("Meet", ?, 1)', (current_month,))
            conn.commit()

            # Обновление таблицы Stat
            num_registered_users = len(registered_users)
            add_value = 1 / num_registered_users if num_registered_users > 0 else 0

            for user in registered_users:
                cursor.execute('SELECT Meet FROM Stat WHERE Worker = ? AND Month = ?', (user, current_month))
                meet_row = cursor.fetchone()
                if meet_row:
                    current_value = (int(meet_row[0]) if meet_row and meet_row[0] is not None else 0) + 1
                    cursor.execute('UPDATE Stat SET Meet = ? WHERE Worker = ? AND Month = ?',
                                   (current_value, user, current_month))
                else:
                    cursor.execute('INSERT INTO Stat (Worker, Month, Meet) VALUES (?, ?, ?)',
                                   (user, current_month, add_value))
                conn.commit()

            conn.close()

            await interaction.followup.send("Контракт успешно завершен.", ephemeral=True)
        else:
            await interaction.followup.send("Вы не записаны на контракт и не можете его завершить.", ephemeral=True)

    @discord.ui.button(label="Помощь", style=discord.ButtonStyle.secondary)
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Meet WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}

        # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            channel = bot.get_channel(config['channel_id'])
            embed = discord.Embed(title="SOS", description="# 🥩 МЯСО \nТребуется помощь!", color=0xFF0000)
            message = f'<@&879192631060606998>\n'  # Добавляем пинг роли в начало сообщения
            sent_message = await channel.send(message, embed=embed, view=SOSView())

class View2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Завершить", style=discord.ButtonStyle.secondary)
    async def end_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention

        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Trash WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}

            # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            end_time = datetime.now(pytz.timezone('Europe/Moscow'))

            # Обновляем время завершения в базе данных
            cursor.execute('UPDATE Trash SET End = ? WHERE ContractID = ?',
                            (end_time.strftime('%Y-%d-%m %H:%M'), message_id))
            conn.commit()

            # Обновляем время отката в базе данных
            rollback_time = end_time + timedelta(hours=26)
            cursor.execute('UPDATE Trash SET Rollback = ? WHERE ContractID = ?',
                            (rollback_time.strftime('%Y-%d-%m %H:%M'), message_id))

            # Обновляем изначальное сообщение с новым временем и участниками
            channel = bot.get_channel(config['channel_id'])
            if message_id:
                message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
                updated_embed = message.embeds[0]
                description_lines = updated_embed.description.split('\n')

                # Обновляем строку с "♻️ Мусор -" для добавления времени окончания
                new_description_lines = []
                for line in description_lines:
                    if line.startswith("## ♻️ Мусор -"):
                        parts = line.split(' - ')
                        if len(parts) > 1:
                            updated_description = f"{parts[0]} - Контракт откатится - {rollback_time.strftime('%Y-%d-%m %H:%M')}"
                            new_description_lines.append(updated_description)
                    else:
                        new_description_lines.append(line)

                    # Собираем обновленное описание
                updated_embed.description = '\n'.join(new_description_lines)
                await message.edit(embed=updated_embed)

                # Удаляем сообщение о запуске контракта
            if start_message_idt:
                start_message = await channel.fetch_message(start_message_idt)
                await start_message.delete()

            current_month = datetime.now().strftime('%Y-%m')
            # Обновление таблицы Contracts
            cursor.execute('SELECT Count FROM Сontracts WHERE Name = "Trash" AND Month = ?', (current_month,))
            count_row = cursor.fetchone()
            if count_row:
                count = count_row[0] + 1
                cursor.execute('UPDATE Сontracts SET Count = ? WHERE Name = "Trash" AND Month = ?',
                               (count, current_month))
            else:
                cursor.execute('INSERT INTO Сontracts (Name, Month, Count) VALUES ("Trash", ?, 1)', (current_month,))
            conn.commit()

            # Обновление таблицы Stat
            num_registered_users = len(registered_users)
            add_value = 1 / num_registered_users if num_registered_users > 0 else 0

            for user in registered_users:
                cursor.execute('SELECT Trash FROM Stat WHERE Worker = ? AND Month = ?', (user, current_month))
                meet_row = cursor.fetchone()
                if meet_row:
                    current_value = (int(meet_row[0]) if meet_row and meet_row[0] is not None else 0) + 1
                    cursor.execute('UPDATE Stat SET Trash = ? WHERE Worker = ? AND Month = ?',
                                   (current_value, user, current_month))
                else:
                    cursor.execute('INSERT INTO Stat (Worker, Month, Trash) VALUES (?, ?, ?)',
                                   (user, current_month, add_value))
                conn.commit()

            conn.close()

            await interaction.followup.send("Контракт успешно завершен.", ephemeral=True)
        else:
            await interaction.followup.send("Вы не записаны на контракт и не можете его завершить.", ephemeral=True)

    @discord.ui.button(label="Помощь", style=discord.ButtonStyle.secondary)
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_ping = interaction.user.mention
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()
        cursor.execute('SELECT Worker FROM Meet WHERE ContractID = ?', (message_id,))
        registered_users = {row[0] for row in cursor.fetchall()}

        # Проверяем, записан ли пользователь
        if user_ping in registered_users:
            channel = bot.get_channel(config['channel_id'])
            embed = discord.Embed(title="SOS", description="# ♻️ МУСОР \nТребуется помощь!", color=0xFF0000)
            message = f'<@&879192631060606998>\n'  # Добавляем пинг роли в начало сообщения
            sent_message = await channel.send(message, embed=embed, view=SOSViewT())

class BNBView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.message_id = None

    @discord.ui.button(label="Запустить", style=discord.ButtonStyle.secondary)
    async def start_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = bot.get_channel(config['channel_id'])
        message = f'<@&879192631060606998>\n'  # Добавляем пинг роли в начало сообщения
        embed = discord.Embed(description="# ⚒️ ЛНС \nВыполнено: 0/20", color=0x50FFBC)
        view = CompleteBNBView()

        sent_message = await channel.send(message, embed=embed, view=view)
        global completed_count
        global ed_message_id
        ed_message_id = sent_message.id

        # Подключаемся к базе данных и добавляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')
        end_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=72)).strftime('%Y-%d-%m %H:%M')

        cursor.execute("INSERT INTO BNB (ContractID, Start, End) VALUES (?, ?, ?)",
                       (ed_message_id, current_time, end_time))
        conn.commit()
        conn.close()

        # Запускаем задачу для обновления таймера
        asyncio.create_task(self.update_timer(sent_message))

    async def update_timer(self, message):
        while True:
            await asyncio.sleep(30)  # Обновляем каждые 30 минут
            channel = bot.get_channel(config['channel_id'])
            try:
                message = await channel.fetch_message(message.id)  # Получаем сообщение по ID
            except discord.errors.NotFound:
                print(f"Message with ID {message.id} not found. Stopping update task.")
                break

            updated_embed = message.embeds[0]

            # Подключаемся к базе данных и обновляем запись
            conn = sqlite3.connect('escdb.db')
            cursor = conn.cursor()

            cursor.execute("SELECT Worker, End FROM BNB WHERE ContractID = ? AND Worker IS NOT NULL", (ed_message_id,))
            completed_users = cursor.fetchall()

            conn.close()

            # Обновляем embed с информацией о выполнивших пользователях и таймером
            description_lines = updated_embed.description.split('\n')
            description_lines[0] = f"# ⚒️ ЛНС \nВыполнено: {completed_count}/20"

            # Удаляем старые строки с информацией о выполнивших пользователях
            description_lines = description_lines[:1]

            # Добавляем информацию о выполнивших пользователях
            for user, end_time in completed_users:
                end_time_dt = datetime.strptime(end_time, '%Y-%d-%m %H:%M')
                end_time_dt = pytz.timezone('Europe/Moscow').localize(end_time_dt)  # Делаем end_time_dt offset-aware
                remaining_time = end_time_dt - datetime.now(pytz.timezone('Europe/Moscow'))
                if remaining_time.total_seconds() <= 0:
                    new_line = f"{user} - доступно"
                else:
                    remaining_time_str = str(remaining_time).split('.')[0]
                    new_line = f"{user} - {remaining_time_str}"
                description_lines.append(new_line)

            updated_embed.description = '\n'.join(description_lines)
            await message.edit(embed=updated_embed)

class CompleteBNBView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Выполнил", style=discord.ButtonStyle.secondary)
    async def complete_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        global completed_count
        completed_count += 1
        channel = bot.get_channel(config['channel_id'])
        try:
            message = await channel.fetch_message(ed_message_id)  # Получаем сообщение по ID
        except discord.errors.NotFound:
            return

        updated_embed = message.embeds[0]

        # Подключаемся к базе данных и обновляем запись
        conn = sqlite3.connect('escdb.db')
        cursor = conn.cursor()

        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%d-%m %H:%M')
        end_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=24)).strftime('%Y-%d-%m %H:%M')
        current_month = datetime.now().strftime('%Y-%m')

        # Проверяем, существует ли уже запись для данного пользователя и контракта
        cursor.execute("SELECT 1 FROM BNB WHERE ContractID = ? AND Worker = ?",
                       (ed_message_id, interaction.user.mention))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO BNB (ContractID, Worker, Start, End) VALUES (?, ?, ?, ?)",
                           (ed_message_id, interaction.user.mention, current_time, end_time))
        else:
            cursor.execute("UPDATE BNB SET Start = ?, End = ? WHERE ContractID = ? AND Worker = ?",
                           (current_time, end_time, ed_message_id, interaction.user.mention))
        conn.commit()

        if completed_count == 20:
            rollback_time = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(hours=72)).strftime(
                '%Y-%d-%m %H:%M')
            cursor.execute("UPDATE BNB SET Rollback = ? WHERE ContractID = ?", (rollback_time, ed_message_id))
            conn.commit()

            # Fetch and update the original message with message_id
            original_message = await channel.fetch_message(message_id)  # Получаем сообщение по ID
            original_embed = original_message.embeds[0]
            original_description_lines = original_embed.description.split('\n')

            # Обновляем строку с "## ⚒️ ЛНС -"
            for i, line in enumerate(original_description_lines):
                if line.startswith("## ⚒️ ЛНС -"):
                    original_description_lines[i] = f"{line.split(' - ')[0]} - Контракт откатится - {rollback_time}"
                    break

            # Собираем обновленное описание
            original_embed.description = '\n'.join(original_description_lines)
            await original_message.edit(embed=original_embed)

            # Update the statistics for each user
            cursor.execute("SELECT Worker FROM BNB WHERE ContractID = ? AND Worker IS NOT NULL", (ed_message_id,))
            existing_users = cursor.fetchall()
            for user in existing_users:
                user = user[0]  # Extract the actual username from the tuple
                cursor.execute('SELECT BNB FROM Stat WHERE Worker = ? AND Month = ?', (user, current_month))
                bnb_row = cursor.fetchone()
                if bnb_row:
                    current_value = (int(bnb_row[0]) if bnb_row and bnb_row[0] is not None else 0) + 1
                    cursor.execute('UPDATE Stat SET BNB = ? WHERE Worker = ? AND Month = ?',
                                   (current_value, user, current_month))
                else:
                    cursor.execute('INSERT INTO Stat (Worker, Month, BNB) VALUES (?, ?, ?)', (user, current_month, 1))
                conn.commit()

            # Update the BNB contract count
            cursor.execute('SELECT Count FROM Сontracts WHERE Name = "BNB" AND Month = ?', (current_month,))
            count_row = cursor.fetchone()
            if count_row:
                count = count_row[0] + 1
                cursor.execute('UPDATE Сontracts SET Count = ? WHERE Name = "BNB" AND Month = ?',
                               (count, current_month))
            else:
                cursor.execute('INSERT INTO Сontracts (Name, Month, Count) VALUES ("BNB", ?, 1)', (current_month,))
            conn.commit()

            await interaction.message.delete()
            completed_count = 0

        # Извлекаем все записи для данного контракта
        cursor.execute("SELECT Worker, End FROM BNB WHERE ContractID = ? AND Worker IS NOT NULL", (ed_message_id,))
        completed_users = cursor.fetchall()

        conn.close()

        # Обновляем embed с информацией о выполнивших пользователях
        description_lines = updated_embed.description.split('\n')
        description_lines[0] = f"# ⚒️ ЛНС \nВыполнено: {completed_count}/20"

        # Удаляем старые строки с информацией о выполнивших пользователях
        description_lines = description_lines[:1]

        # Добавляем информацию о выполнивших пользователях
        for user, end_time in completed_users:
            end_time_dt = datetime.strptime(end_time, '%Y-%d-%m %H:%M')
            end_time_dt = pytz.timezone('Europe/Moscow').localize(end_time_dt)  # Делаем end_time_dt offset-aware
            remaining_time = end_time_dt - datetime.now(pytz.timezone('Europe/Moscow'))
            if remaining_time.total_seconds() <= 10:
                new_line = f"{user} - доступно"
            else:
                remaining_time_str = str(remaining_time).split('.')[0]
                new_line = f"{user} - {remaining_time_str}"
            description_lines.append(new_line)

        updated_embed.description = '\n'.join(description_lines)
        await message.edit(embed=updated_embed)

def get_stats(user=None):
    conn = sqlite3.connect('escdb.db')
    cursor = conn.cursor()

    current_month = datetime.now().strftime('%Y-%m')  # Получаем текущий месяц в формате ГГГГ-ММ

    if user:
        cursor.execute('SELECT * FROM Stat WHERE Worker = ? AND Month = ?', (user, current_month))
        result = cursor.fetchone()
        conn.close()
        return result
    else:
        cursor.execute('SELECT * FROM Stat WHERE Month = ?', (current_month,))
        result = cursor.fetchall()
        conn.close()
        return result

# Define the /stats command
@bot.command(name="статистика", case_insensitive=True)
async def статистика(ctx, member: discord.Member = None):
    embed = discord.Embed(title="Статистика", color=0x50FFBC)

    if member:
        stats = get_stats(member.mention)
        if stats:
            embed.add_field(name="Пользователь", value=member.mention, inline=False)
            embed.add_field(name="Контракты",
                            value=f"🥩 - {stats[1]} | ♻️️ - {stats[2]} | 💾 - {stats[3]} | ⚒️ - {stats[4]}",
                            inline=False)
        else:
            embed.add_field(name="Ошибка", value=f"Нет статистики для {member.mention} за текущий месяц.", inline=False)
    else:
        stats = get_stats()
        if stats:
            for stat in stats:
                embed.add_field(name="\u200b",  # Используем невидимый символ, чтобы убрать заголовок поля
                                value=f"{stat[0]}: 🥩 - {stat[1]} | ♻️️ - {stat[2]} | 💾 - {stat[3]} | ⚒️ - {stat[4]}",
                                inline=False)
        else:
            embed.add_field(name="Ошибка", value="Нет статистики для пользователей за текущий месяц.", inline=False)

    await ctx.send(embed=embed)


@bot.command(name="сконтракты", case_insensitive=True)
async def сконтракты(ctx):
    conn = sqlite3.connect('escdb.db')
    cursor = conn.cursor()

    # Получаем текущий месяц в формате ГГГГ-ММ
    current_month = datetime.now().strftime('%Y-%m')

    # Извлекаем данные из таблицы Contracts для текущего месяца
    cursor.execute('SELECT Name, Count FROM Сontracts WHERE Month = ?', (current_month,))
    contracts = cursor.fetchall()
    conn.close()

    # Сопоставляем названия контрактов с их отображаемыми именами и значениями прибыли
    contract_names = {
        'Meet': {'display_name': '🥩 Мясо', 'profit_per_unit': 13000},
        'Trash': {'display_name': '♻️ Мусор', 'profit_per_unit': 13000},
        'BNB': {'display_name': '⚒️ ЛНС', 'profit_per_unit': 25000},
        'Circuits': {'display_name': '💾 Схемы', 'profit_per_unit': 30000}
    }

    month_names = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }

    display_month = month_names.get(current_month[-2:], current_month)
    embed = discord.Embed(description=f"# Статистика контрактов за {display_month}", color=0x50FFBC)

    if contracts:
        for contract in contracts:
            name = contract[0]
            count = contract[1]

            # Получаем отображаемое имя и значение прибыли за единицу
            display_name = contract_names.get(name, {'display_name': name, 'profit_per_unit': 0})['display_name']
            profit_per_unit = contract_names.get(name, {'display_name': name, 'profit_per_unit': 0})['profit_per_unit']

            # Рассчитываем общую прибыль
            total_profit = count * profit_per_unit

            # Добавляем информацию о контракте в embed
            embed.add_field(name=display_name, value=f"Количество: {count} | Прибыль: {total_profit}$", inline=False)
    else:
        embed.add_field(name="Ошибка", value="Нет данных по контрактам за текущий месяц.", inline=False)

    await ctx.send(embed=embed)


class GatheringView(discord.ui.View):
    def __init__(self, count, embed):
        super().__init__()
        self.count = count
        self.embed = embed
        self.participants = []

    @discord.ui.button(label="Записаться", style=discord.ButtonStyle.primary)
    async def записаться(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user.mention in self.participants:
            return

        # Добавляем участника в список
        self.participants.append(user.mention)

        # Обновляем embed
        if len(self.participants) >= self.count:
            button.disabled = True  # Отключаем кнопку, если набрано нужное количество участников

        participant_list = "\n".join(self.participants)
        self.embed.set_field_at(0, name="Участники", value=participant_list, inline=False)

        await interaction.response.edit_message(embed=self.embed, view=self)


# Использование кастомного View в команде
@bot.command(name="сборвзп")
async def сборвзп(ctx, count : int):
    if count <= 0:
        await ctx.send("Количество участников должно быть больше 0.")
        return

    embed = discord.Embed(
        description=f"# ⚔️ ВЗП \n## Необходимо: {count}",
        color=0x50FFBC
    )
    embed.add_field(name="Участники", value="Пока нет записанных участников.", inline=False)

    # Создаем экземпляр кастомного View и передаем параметры
    view = GatheringView(count, embed)

    # Отправляем embed с View
    await ctx.send(content=f"<@&879192631060606998>", embed=embed, view=view)

TOKEN = os.getenv('DISCORD_TOKEN')

filename = "example.txt"

# Текст, который нужно записать
content = "Привет, мир! Это пример записи в файл."

# Создание и открытие файла для записи
with open(filename, "w") as file:
    # Запись текста в файл
    file.write(content)

bot.run(TOKEN)
