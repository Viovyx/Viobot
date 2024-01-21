from datetime import datetime

import interactions
from interactions import Extension, slash_command, SlashContext
from tinydb import TinyDB

from automations.log import log_command
from shared import ROOT_DIR, User


class Pair(Extension):
    @slash_command(
        name="pair",
        dm_permission=False,
        sub_cmd_name="add",
        sub_cmd_description="Add a new pair",
        options=[
            interactions.SlashCommandOption(
                name="user1",
                description="The first user you wish to pair",
                type=interactions.OptionType.USER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="user2",
                description="The second user you wish to pair",
                type=interactions.OptionType.USER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="nickname",
                description="An optional nickname you can add to the pair",
                type=interactions.OptionType.STRING,
                required=False
            ),
        ],
    )
    async def pair(self, ctx: SlashContext, user1: interactions.Member, user2: interactions.Member, nickname=''):
        log_command(ctx=ctx, cmd="pair.add")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if user1.id != user2.id:
                if db.search(User['user1-id'] == f'{user1.id}') or db.search(User['user2-id'] == f'{user2.id}'):
                    await ctx.send(
                        f'A pair already exist for either <@{user1.id}> or <@{user2.id}>. Please unpair them first using `/unpair` before attempting to pair!.',
                        ephemeral=True)
                else:
                    db.insert({
                        'user1': f'{user1.username}',
                        'user1-id': f'{user1.id}',
                        'user2': f'{user2.username}',
                        'user2-id': f'{user2.id}',
                        'nickname': f'{nickname}',
                        'last-change-utc': f'{datetime.utcnow()}'
                    })
                    if nickname:
                        await ctx.send(
                            f'Pair successfully added for <@{user1.id}> & <@{user2.id}> with nickname "{nickname}"')
                    else:
                        await ctx.send(f'Pair successfully added for <@{user1.id}> & <@{user2.id}>')
            else:
                await ctx.send("ERROR: Can't pair a user to themselves!", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @pair.subcommand(
        sub_cmd_name="nickname",
        sub_cmd_description="Add or edit the nickname of a pair",
        options=[
            interactions.SlashCommandOption(
                name='user',
                description='Either user of the pair',
                type=interactions.OptionType.USER,
                required=True
            ),
            interactions.SlashCommandOption(
                name='nickname',
                description='The new nickname',
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def pair_nick(self, ctx: SlashContext, user: interactions.Member, nickname: str):
        log_command(ctx=ctx, cmd="pair.nickname")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if db.search(User['user1-id'] == f'{user.id}') or db.search(User['user2-id'] == f'{user.id}'):
                db.update({'nickname': f'{nickname}', 'last-change-utc': f'{datetime.utcnow()}'},
                          ((User['user1-id'] == f'{user.id}') | (User['user2-id'] == f'{user.id}')))
                await ctx.respond(f"Successfully updated nickname of <@{user.id}>'s pair to '{nickname}'")
            else:
                await ctx.respond(f"There was no pair found for <@{user.id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @pair.subcommand(
        sub_cmd_name="partner",
        sub_cmd_description="Display the partner of a user in a pair",
        options=[
            interactions.SlashCommandOption(
                name='user',
                description='The use of who you wish to view the partner of',
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
    )
    async def partner(self, ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="pair.partner")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'
            partner_id = ''
            nickname = ''

            if db.search(User['user1-id'] == f'{user.id}'):
                apair = db.search(User['user1-id'] == f'{user.id}')
                partner_id = apair[0]['user2-id']
                nickname = apair[0]['nickname']
            elif db.search(User['user2-id'] == f'{user.id}'):
                apair = db.search(User['user2-id'] == f'{user.id}')
                partner_id = apair[0]['user1-id']
                nickname = apair[0]['nickname']
            else:
                await ctx.respond(f"No pair found for <@{user.id}>", ephemeral=True)

            if nickname != '':
                await ctx.respond(f"The partner of <@{user.id}> is <@{partner_id}>. Their nickname is '{nickname}'",
                                  ephemeral=True)
            else:
                await ctx.respond(f"The partner of <@{user.id}> is <@{partner_id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @pair.subcommand(
        sub_cmd_name="remove",
        sub_cmd_description="Remove a pair",
        options=[
            interactions.SlashCommandOption(
                name='user',
                description='Either user of the pair you wish to unpair',
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
    )
    async def unpair(self, ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="pair.remove")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if db.search(User['user1-id'] == f'{user.id}'):
                await ctx.respond(
                    f"Unpair successful for <@{user.id}> & <@{db.search(User['user1-id'] == f'{user.id}')[0]['user2-id']}>")
                db.remove(User['user1-id'] == f'{user.id}')
            elif db.search(User['user2-id'] == f'{user.id}'):
                await ctx.respond(
                    f"Unpair successful for <@{user.id}> & <@{db.search(User['user2-id'] == f'{user.id}')[0]['user1-id']}>")
                db.remove(User['user2-id'] == f'{user.id}')
            else:
                await ctx.respond(f"There was no pair found for <@{user.id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @pair.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List all pairs"
    )
    async def list_all(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="pair.list")
        embed = interactions.Embed(title="All Pairs:", color="#9b59b6")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'
            for pair in db.all():
                embed.add_field(name=f"{pair['user1']} & {pair['user2']}", value=f"Nickname: {pair['nickname']}",
                                inline=False)
            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)
        await ctx.respond(embed=embed)
