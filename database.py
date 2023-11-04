import discord
import mysql.connector

import random
# Connect to the database
db = mysql.connector.connect(
  host="HOST",
  user="USER",
  password="PASS",
  database="DBNAME",

)

owner_user_id = "623472673463"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def generate_key():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))

def create_key(user):
    key = generate_key()
    cursor = db.cursor()
    sql = "INSERT INTO `keys` (`key`, `user`) VALUES (%s, %s);"
    val = (key, user)
    cursor.execute(sql, val)
    db.commit()
    return key

def delete_key(key):
    cursor = db.cursor()
    sql = "DELETE FROM keys WHERE key = %s"
    val = (key,)
    cursor.execute(sql, val)
    db.commit()


def show_keys(user):
    cursor = db.cursor()
    sql = "SELECT key FROM keys WHERE user = %s"
    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    keys = [r[0] for r in result]
    return keys


def reset_ip(key):
    cursor = db.cursor()
    sql = "UPDATE keys SET ip = NULL WHERE key = %s"
    val = (key,)
    cursor.execute(sql, val)
    db.commit()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!create'):
        if message.author.id != owner_user_id:
            return
        user = message.content[8:]
        key = create_key(user)
        await message.channel.send('Key created: {}'.format(key))

    if message.content.startswith('!delete'):
        if message.author.id != owner_user_id:
            return
        key = message.content[8:]
        delete_key(key)
        await message.channel.send('Key deleted: {}'.format(key))

    if message.content.startswith('!show'):
        if message.author.id != owner_user_id:
            return
        user = message.content[6:]
        keys = show_keys(user)
        await message.channel.send('Keys for {}: {}'.format(user, ', '.join(keys)))

    if message.content.startswith('!reset'):
        key = message.content[7:]
        reset_ip(key)
        await message.channel.send('IP address for key {} reset'.format(key))


client.run('TOKEN')
