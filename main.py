import random
import discord
import os
from discord import Button, ButtonStyle, ButtonColor, ButtonClick
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, Context, has_permissions, MissingRequiredArgument, MemberNotFound, CommandInvokeError, MissingPermissions, BadArgument
import asyncio
import requests
import json

with open("config.json", "r") as config:
    cfg = json.load(config)
    token = cfg["token"]
    prefix = cfg["prefix"]
    guild = cfg["guild"]

bot = commands.Bot(prefix, intents=discord.Intents.all(), case_insensitive=True)
bot.remove_command('help')

@tasks.loop(seconds=300)
async def update_status():
    await bot.change_presence(activity=discord.Game(name=f"{bot.get_guild(int(guild)).member_count} members"))

@bot.event
async def on_ready():
    print("Ready To Use")

@bot.command(aliases=["h"])
async def help(ctx):
    embed=discord.Embed(title="**Help**", color=random.randrange(0, 0xffffff))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/949377070289526814/949456390404046890/lightbulb-icon.png")
    embed.add_field(name=f"{prefix}kick", value=f"Usage: {prefix}kick @user reason", inline=False)
    embed.add_field(name=f"{prefix}ban", value=f"Usage: {prefix}ban @user reason", inline=False)
    embed.add_field(name=f"{prefix}unban", value=f"Usage: {prefix}unban @user", inline=False)
    embed.add_field(name=f"{prefix}clear", value=f"Usage: {prefix}clear Amount", inline=False)

    embed.set_footer(text="Help Command - Moamele Apply Bot")
    await ctx.send(embed=embed)

@bot.command(name="kick", aliases=["k"])
@has_permissions(kick_members=True)   
async def kick(ctx, member: discord.Member, *,reason: str): 
    await member.kick(reason=reason)
    with open("Kick_Log.txt", "a+") as k:
        k.write(f"{member} Kick Shod Tavasot {ctx.author} | Reason: {reason}\n")
    embed=discord.Embed(title="**Member Kicked!**", description=f"Reason: {reason}", color=random.randrange(0, 0xffffff))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/949377070289526814/949445414044696686/bhinf1.png")
    embed.add_field(name="Member:", value=f"{member}", inline=True)
    embed.set_footer(text=f"{member} Sho Khosh Shod!")
    await ctx.send(embed=embed)

@bot.command(name="ban", aliases=["b"])
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str):
    await member.ban(reason=reason)
    with open("Ban_Log.txt", "a+") as b:
        b.write(f"{member} Ban Shod Tavasot {ctx.author} | Reason: {reason}\n")
    embed=discord.Embed(title="**Member Banned!**", description=f"Reason: {reason}", color=random.randrange(0, 0xffffff))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/949377070289526814/949445169558745099/220px-Ameer_Vann_2018_28cropped29.png")
    embed.add_field(name="Member:", value=f"{member}", inline=True)
    embed.set_footer(text=f"{member} Sho Khosh Shod!")
    await ctx.send(embed=embed)

@bot.command(name="clear")
@has_permissions(manage_messages=True)
async def pakkardan(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    embed=discord.Embed(title="Cleared!", description=f"{amount} Message Cleared", color=random.randrange(0, 0xffffff))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/949377070289526814/949483170603098122/clear-cache-on-mac-1200x628.png")
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(2)
    await msg.delete()


@bot.command(name="unban", aliases=["ub"])
@has_permissions(ban_members=True)
async def unban(ctx, id : int):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)
    embed=discord.Embed(title="**Member Unbanned!**", color=random.randrange(0, 0xffffff))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/949377070289526814/949445226936807444/brockhampton-ginger-cover-art.png")
    embed.add_field(name="Member:", value=f"{user.name}", inline=True)
    embed.set_footer(text=f"{user.name} Unban Shod!")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def createticket(ctx, *args):
    format_args = list(args)

    guild_id = ctx.message.guild.id
    channel_id = int(format_args[0].strip('<').strip('>').replace('#', ''))
    title = ' '.join(format_args[1:])

    with open('ticket.json', 'r') as file:
        ticket_data = json.load(file)
        new_ticket = str(guild_id)

        if new_ticket in ticket_data:
            ticket_data[new_ticket] += [channel_id]
            with open('ticket.json', 'w') as update_ticket_data:
                json.dump(ticket_data, update_ticket_data, indent=4)
        else:
            ticket_data[new_ticket] = [channel_id]
            with open('ticket.json', 'w') as new_ticket_data:
                json.dump(ticket_data, new_ticket_data, indent=4)

    ticket_embed = discord.Embed(title="**Create Ticket**",description=title, color=random.randrange(0, 0xffffff))

    send_ticket_embed = await bot.get_channel(channel_id).send(embed=ticket_embed)

    await send_ticket_embed.add_reaction(u'\U0001F3AB')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.id != bot.user.id:
        with open('ticket.json', 'r') as file:
            ticket_data = json.load(file)

        channel_id = list(ticket_data.values())
        user_channel_id = payload.channel_id

        for items in channel_id:
            if user_channel_id in items:
                find_guild = bot.get_guild(payload.guild_id)
                guild_roles = discord.utils.get(find_guild.roles, name=f'{payload.member.name}')

                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)

                await message.remove_reaction(u'\U0001F3AB', bot.get_user(payload.user_id))

                if guild_roles is None:
                    permissions = discord.Permissions(send_messages=True, read_messages=True)
                    await find_guild.create_role(name=f'{payload.member.name}', permissions=permissions)

                    new_user_role = discord.utils.get(find_guild.roles, name=f'{payload.member.name}')
                    await payload.member.add_roles(new_user_role, reason=None, atomic=True)

                    admin_role = discord.utils.get(find_guild.roles, name='Admin')

                    overwrites = {
                        find_guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        new_user_role: discord.PermissionOverwrite(read_messages=True),
                        admin_role: discord.PermissionOverwrite(read_messages=True)
                    }

                    create_channel = await find_guild.create_text_channel(
                        u'\U0001F4CB-{}-Ticket'.format(new_user_role), overwrites=overwrites)

                    eb = discord.Embed(title=f'Created Ticket {new_user_role}', description=f'''{payload.member.mention}
                    **Use This Channel To Send Messages To The Admin!
                    And You Can Use The Button Below To Close The Ticket!**''', color=random.randrange(0, 0xffffff))
                    
                    m = await create_channel.send(embed=eb, components=[[
                        Button(label='Close Ticket',
                            custom_id='close',
                            style=ButtonColor.red)
                    ]])

                    def check_button(i: discord.Interaction, button):
                        return i.author == payload.member and i.message == m

                    interaction, button = await bot.wait_for('button_click', check=check_button)

                    embed = discord.Embed(title=f'Closed Ticket {new_user_role}', description=f'''{interaction.author.mention}
                    Closed Ticket!''', color=random.randrange(0, 0xffffff))

                    await interaction.respond(embed=embed)

                    await asyncio.sleep(3)

                    await new_user_role.delete(reason=None)

                    await create_channel.delete(reason=None)               
                else:
                    new_user_role = discord.utils.get(find_guild.roles, name=f'{payload.member.name}')
                    await payload.member.add_roles(new_user_role, reason=None, atomic=True)

                    admin_role = discord.utils.get(find_guild.roles, name='Admin')

                    overwrites = {
                        find_guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        new_user_role: discord.PermissionOverwrite(read_messages=True),
                        admin_role: discord.PermissionOverwrite(read_messages=True)
                    }

                    create_channel = await find_guild.create_text_channel(
                        u'\U0001F4CB-{}-Ticket'.format(new_user_role), overwrites=overwrites)

                    eb = discord.Embed(title=f'Created Ticket {new_user_role}', description=f'''{payload.member.mention}
                    **Use This Channel To Send Messages To The Admin!
                    And You Can Use The Button Below To Close The Ticket!**''', color=random.randrange(0, 0xffffff))
                    
                    m = await create_channel.send(embed=eb, components=[[
                        Button(label='Close Ticket',
                            custom_id='close',
                            style=ButtonColor.red)
                    ]])

                    def check_button(i: discord.Interaction, button):
                        return i.author == payload.member and i.message == m

                    interaction, button = await bot.wait_for('button_click', check=check_button)

                    embed = discord.Embed(title=f'Closed Ticket {new_user_role}', description=f'''{interaction.author.mention}
                    Closed Ticket!''', color=random.randrange(0, 0xffffff))

                    await interaction.respond(embed=embed)

                    await asyncio.sleep(3)

                    await new_user_role.delete(reason=None)

                    await create_channel.delete(reason=None)

bot.run(token)