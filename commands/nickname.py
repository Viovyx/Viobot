from datetime import datetime

import interactions
from interactions import Extension, slash_command, SlashContext
from tinydb import TinyDB

from automations.log import log_command
from shared import ROOT_DIR, User


class Nickname(Extension):
    @slash_command(
        name="nickname",
        dm_permission=False,
        sub_cmd_name="add",
        sub_cmd_description="Add a nickname to a user",
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="To who should the nickname be added?",
                type=interactions.OptionType.USER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="nickname",
                description="Enter the nickname of the user.",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def nickname(self, ctx: SlashContext, user: interactions.Member, nickname: str):
        log_command(ctx=ctx, cmd="nickname.add")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/nicknames.json', indent=4, create_dirs=True)
            db.default_table_name = 'nicknames'

            if db.search(User['user-id'] == f'{user.id}'):
                db.update({'nickname': f'{nickname}', 'last-change-utc': f'{datetime.utcnow()}'},
                          User['user-id'] == f'{user.id}')
                await ctx.send(f'Nickname successfully updated for <@{user.id}> as "{nickname}"')
            else:
                db.insert({
                    'user': f'{user.username}',
                    'user-id': f'{user.id}',
                    'nickname': f'{nickname}',
                    'last-change-utc': f'{datetime.utcnow()}'
                })
                await ctx.send(f'Nickname successfully added for <@{user.id}> as "{nickname}"')

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @nickname.subcommand(
        sub_cmd_name="show",
        sub_cmd_description="Display the nickname of a user",
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="Who's nickname do you wish to show?",
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
    )
    async def nickname_show(self, ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="nickname.show")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/nicknames.json', indent=4, create_dirs=True)
            db.default_table_name = 'nicknames'
            anick = db.search(User['user-id'] == f'{user.id}')
            db.close()

            if anick:
                nick = anick[0]['nickname']
                await ctx.send(f"Nickname of {user} is '{nick}'", ephemeral=True)
            else:
                await ctx.send(f"ERROR: No nickname found for {user}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @nickname.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List all nicknames",
    )
    async def nickname_list(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="nickname.list")
        embed = interactions.Embed(title="All Nicknames:", color="#9b59b6")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/nicknames.json', indent=4, create_dirs=True)
            db.default_table_name = 'nicknames'
            for nick in db.all():
                embed.add_field(name=f"{nick['user']}", value=f"{nick['nickname']}", inline=False)
            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)
        await ctx.respond(embed=embed)
