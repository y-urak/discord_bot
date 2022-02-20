# インストールした discord.py を読み込む
# https://github.com/discord-py-ui/discord-ui
# https://discord-ui.readthedocs.io/en/latest/interactions.html
# https://www.sepiamars.work/entry/2021/08/01/091450
# SPOILER https://stackoverflow.com/questions/60408884/how-do-i-get-the-bot-to-post-spoiler-images-in-discord-py
import discord
from discord.ext import commands
from discord_ui import UI, Button
from asyncio import TimeoutError
import glob
import csv
import random

# ----- 前処理 -------
TOKEN = 'OTQxMzExNjQyNDEzNzE1NTA2.YgUGyA.-mGr8VPuZ642FaCO88I1aX9zOlE'
# 任意のチャンネルID(int)
CHANNEL_ID = 895578786303733771

# ファイルの情報取得 -> コマンドで画像情報の一覧表示に利用
map_files = glob.glob("./image/map/overall/*")
map_commands_str = []
print(map_files)
for f in map_files:
    tmp = f.split("/")
    map_name = tmp[4]
    print(map_name)
    map_commands_str.append(map_name[1][:len(map_name[1])])

zeta_map_files = glob.glob("./image/zeta_map/*")
zeta_map_commands_str = []
for f in zeta_map_files:
    tmp = f.split("/")
    map_name = tmp[3]
    print(map_name)
    zeta_map_commands_str.append(map_name[1][:len(map_name[1])])

start_quiz = True
# ACENT=0,BIND=1,ICEBOX=2,Breeze=3,Haven=4,Split=5,Fracture=6
path_load_list = ["./valo_mapdata/acent/*", "./valo_mapdata/bind/*", "./valo_mapdata/icebox/*", "./valo_mapdata/breeze/*", "./valo_mapdata/heaven/*", "./valo_mapdata/split/*", "./valo_mapdata/frac/*"]
quiz_image_container = []

for path in path_load_list:
    quiz_tmp = []
    for f in glob.glob(path):
        tmp = f.split("/")
        map_name = tmp[3]
        print(map_name)
        quiz_tmp.append(map_name[1][:len(map_name[1])])
    quiz_image_container.append(quiz_tmp)

# 問題の内容のinput
# ACENT=0,BIND=1,ICEBOX=2,Breeze=3,Haven=4,Split=5,Fracture=6
# https://script.google.com/home/projects/1F5b4P1ZTg3mKhHuqU3XwWMKm40Ue1Q_1mNUtwPNRw8RjbNnot110fH4d/edit
with open('valo_mapdata/valo_quiz_data.csv', 'r', encoding="utf-8_sig") as f:
    reader = csv.reader(f)
    list_csv = [row for row in reader]
print(list_csv)

ANS_CNT = 0
# ----- bot処理 -------

# 接続に必要なオブジェクトを生成
# client = discord.Client()
client = commands.Bot(" ")
ui = UI(client)

async def map_name_sender(message, cmd, map_commands):
    for map_name in map_commands:
        await message.channel.send("/" + cmd[1:] + " " + map_name[:len(map_name) - len(".jpg")])

async def map_image_sender(message, map_name, files, path="image/map/overall/", extension=".jpg"):
    print(path + map_name + extension)
    print(files)
    for f in files:
        if f.endswith(map_name + extension):
            print(path + map_name + extension)
            await message.channel.send(file=discord.File(path + map_name + extension))
            return
    await message.channel.send("マップ名が違います")

async def map_quiz_generater(message, map_num=0, image_path="valo_mapdata/acent/", map_cmd="/acent"):
    global ANS_CNT
    random_list = random.sample(range(0, len(quiz_image_container[map_num])), k=len(quiz_image_container[map_num]))
    random_range = random.sample(range(0, 3), k=3)
    output_list = [random_list[random_range[0]], random_list[random_range[1]], random_list[random_range[2]]]
    print(random_list, random_range)
    # rand_ans = random.randrange(len(quiz_image_container[0]))
    rand_ans = random_list[0]
    rand_str = str(rand_ans).zfill(2)
    print(rand_str)
    await map_image_sender(message, rand_str, quiz_image_container[map_num], image_path, ".png")

    msg = await message.channel.send("〇の名前は？", components=[
        # [Button("press me", color="green"), LinkButton("https://discord.com", emoji="😁")],
        Button(list_csv[map_num][output_list[0]], color="green"),
        Button(list_csv[map_num][output_list[1]], color="green"),
        Button(list_csv[map_num][output_list[2]], color="green"),
        Button("終わり!")
    ])
    try:
        # by=message.authorで押す人の制約つけれる
        btn = await msg.wait_for("button", client, timeout=60 * 60 * 60)
        if str(btn.component) == "終わり!":
            await btn.respond("連続正解数 :" + str(ANS_CNT) + ", ans : " + list_csv[0][random_list[0]])
            ANS_CNT = 0
        # btn.componentでボタン名の取得可能
        elif list_csv[map_num][random_list[0]] == str(btn.component):
            ANS_CNT += 1
            await btn.respond("正解 !, 連続正解数 :" + str(ANS_CNT) + ", ans : " + str(btn.component))
            await message.channel.send(map_cmd)
        else:
            await btn.respond("連続正解数 :" + str(ANS_CNT) + ", ans : " + list_csv[map_num][random_list[0]])
            ANS_CNT = 0
    except TimeoutError:
        await msg.delete()

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    global ANS_CNT
    # 画像とボタンを利用してクイズを出す
    # ACENT=0,BIND=1,ICEBOX=2,Breeze=3,Haven=4,Split=5,Fracture=6
    if message.content == '/acent':
        if start_quiz:
            await map_quiz_generater(message, 0)
        else:
            # ネタバレしたくないならSPOILER入れてもいいかも
            await message.channel.send('/ans acent')
    if message.content == '/bind':
        if start_quiz:
            await map_quiz_generater(message, 1, "valo_mapdata/bind/", message.content)
        else:
            await message.channel.send('/ans bind')
    if message.content == '/icebox':
        if start_quiz:
            await map_quiz_generater(message, 2, "valo_mapdata/icebox/", message.content)
        else:
            await message.channel.send('/ans ' + message.content[1:])
    if message.content == '/breeze':
        if start_quiz:
            await map_quiz_generater(message, 3, "valo_mapdata/breeze/", message.content)
        else:
            await message.channel.send('/ans breeze')
    if message.content == '/heaven':
        if start_quiz:
            await map_quiz_generater(message, 4, "valo_mapdata/" + message.content[1:] + "/", message.content)
        else:
            await message.channel.send('/ans ' + message.content[1:])
    if message.content == '/split':
        if start_quiz:
            await map_quiz_generater(message, 5, "valo_mapdata/" + message.content[1:] + "/", message.content)
        else:
            await message.channel.send('/ans ' + message.content[1:])
    if message.content == '/frac':
        if start_quiz:
            await map_quiz_generater(message, 6, "valo_mapdata/" + message.content[1:] + "/", message.content)
        else:
            await message.channel.send('/ans ' + message.content[1:])
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if message.content == '/map':
        await message.channel.send("/ans マップ名")
    if message.content == '?map' or message.content == '?ans':
        await map_name_sender(message, '?map', map_commands_str)

    if message.content.startswith('/zeta_map'):
        # 入力を分割
        input_list = message.content.split()
        if len(input_list) != 2:
            await message.channel.send("/zeta_map マップ名")
        else:
            await map_image_sender(message, input_list[1], zeta_map_files, "image/zeta_map/")
    if message.content.startswith('/ans'):
        # 入力を分割
        input_list = message.content.split()
        if len(input_list) != 2:
            await message.channel.send("/ans マップ名")
        else:
            await map_image_sender(message, input_list[1], map_files)
    if message.content == '?zeta_map':
        await map_name_sender(message, message.content, zeta_map_commands_str)

    # 発言時に実行されるイベントハンドラを定義
    if client.user in message.mentions:  # 話しかけられたかの判定
        await reply(message)  # 返信する非同期関数を実行

# 返信する非同期関数を定義
async def reply(message):
    global start_quiz
    if not start_quiz:
        reply = f'お！？ {message.author.mention} やるか？ '  # 返信メッセージの作成
        start_quiz = True
    else:
        reply = '終わっとくか～'   # 返信メッセージの作成
        start_quiz = False
    await message.channel.send(reply)  # 返信メッセージを送信

# 任意のチャンネルで挨拶する非同期関数を定義
async def greet():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('泣いちゃった...')

# bot起動時に実行されるイベントハンドラを定義
@client.event
async def on_ready():
    await greet()  # 挨拶する非同期関数を実行

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
