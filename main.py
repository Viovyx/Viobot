from dotenv import load_dotenv
from schedules import schedules
import asyncio
import interactions
from interactions import slash_command, SlashContext
from datetime import datetime
from tinydb import TinyDB, Query
import os
from dateutil.relativedelta import relativedelta
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
User = Query()


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TEST_TOKEN')
    bot = interactions.Client()

    # Startup
    async def main():
        asyncio.create_task(schedules(bot))
        await bot.astart(token)

    @interactions.listen()
    async def on_startup():
        print("Bot is ready!")

    # Logging Commands
    def log_command(ctx, cmd):
        db = TinyDB(f'{ROOT_DIR}/db/logs.json', indent=4, create_dirs=True)
        db.default_table_name = f'{cmd}'
        db.insert({
            'time-utc': f'{datetime.utcnow()}',
            'user': f'{ctx.user.username}',
            'user-id': f'{ctx.user.id}',
            'guild-id': f'{ctx.guild_id}',
            'channel': f'{ctx.channel.name}',
            'channel-id': f'{ctx.channel_id}'
        })
        db.close()
        print(f"{ctx.user.username}(uid:{ctx.user.id}) used /{cmd} in {ctx.channel.name}(chid:{ctx.channel_id})(gid:{ctx.guild_id}) at UTC:{datetime.utcnow()}")

    # Ping Command
    @slash_command(
        name="ping",
        description="Test bot latency",
        dm_permission=False
    )
    async def ping(ctx: SlashContext):
        log_command(ctx=ctx, cmd="ping")
        await ctx.send(f"Pong! The response time is {bot.latency * 1000}ms")

    # Quote Command
    @slash_command(
        name="quote",
        description="Quote someone's dumb words",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="text",
                description="What do you wish to quote?",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.SlashCommandOption(
                name="user",
                description="Select user to mention",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def quote(ctx: SlashContext, text: str, user: interactions.Member):
        log_command(ctx=ctx, cmd="quote")
        await ctx.send(f'"{text}" - {user.mention}')

    # Bday Commands
    @slash_command(
        name="bday-set",
        description="Add your birthday to the bot",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="date",
                description="YYYY-MM-DD Example: 1992-01-31 or 2005-12-05",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def bday_set(ctx: SlashContext, date: str):
        log_command(ctx=ctx, cmd="bday-set")
        try:
            adate = date.split("-")
            if len(adate) == 3:
                fdate = datetime(year=int(adate[0]), month=int(adate[1]), day=int(adate[2]))
                if fdate > datetime.now():
                    await ctx.send(f"ERROR: Date can't be in the future", ephemeral=True)
                else:
                    db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
                    db.default_table_name = 'bdays'
                    if db.search(User['user-id'] == f'{ctx.user.id}'):
                        db.update({'bday': f'{fdate}', 'last-change-utc': f'{datetime.utcnow()}'}, User['user-id'] == f'{ctx.user.id}')
                        await ctx.send(
                            f'Bday succesfully changed for {ctx.user.mention} to {fdate.strftime("%B %d, %Y")}')
                    else:
                        db.insert({
                            'user': f'{ctx.user.username}',
                            'user-id': f'{ctx.user.id}',
                            'bday': f'{fdate}',
                            'last-change-utc': f'{datetime.utcnow()}'
                        })
                        await ctx.send(f'Bday succesfully set for {ctx.user.mention} to {fdate.strftime("%B %d, %Y")}')
                    db.close()
            else:
                await ctx.send(f"ERROR: Make sure to use the correct seperator '-' and give the year, month and day",
                               ephemeral=True)
        except ValueError:
            await ctx.send(f"ERROR: Date is invalid", ephemeral=True)


    @slash_command(
        name="bday-show",
        description="Show someones bday",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="Who's bday do you wish to show?",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def bday_show(ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="bday-show")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
            db.default_table_name = 'bdays'
            abday = db.search(User['user-id'] == f'{user.id}')
            db.close()
            if abday:
                bday_str = abday[0]['bday']
                bday = datetime.strptime(bday_str, '%Y-%m-%d %H:%M:%S')
                age = (datetime.now() - relativedelta(years=int(bday.strftime('%Y')))).strftime('%Y').replace('0', '')

                await ctx.send(f"Bday of {user} is {bday.strftime('%B %d, %Y')} ({age} years old)", ephemeral=True)
            else:
                await ctx.send(f"ERROR: No birthday found for {user}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    # Nickname Commands
    @slash_command(
        name="nickname-add",
        description="Add a nickname to a user",
        dm_permission=False,
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
    async def nickname_add(ctx: SlashContext, user: interactions.Member, nickname: str):
        log_command(ctx=ctx, cmd="nickname-add")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/nicknames.json', indent=4, create_dirs=True)
            db.default_table_name = 'nicknames'

            if db.search(User['user-id'] == f'{user.id}'):
                db.update({'nickname': f'{nickname}', 'last-change-utc': f'{datetime.utcnow()}'}, User['user-id'] == f'{user.id}')
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

    @slash_command(
        name="nickname-show",
        description="Display someones nickname",
        dm_permission=False,
        options=[
          interactions.SlashCommandOption(
              name="user",
              description="Who's nickname do you wish to show?",
              type=interactions.OptionType.USER,
              required=True
          ),
        ],
    )
    async def nickname_show(ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="nickname-show")
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

    # Pair Commands
    @slash_command(
        name="pair",
        description="Pair two users together",
        dm_permission=False,
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
    async def pair(ctx: SlashContext, user1: interactions.Member, user2: interactions.Member, nickname=''):
        log_command(ctx=ctx, cmd="pair")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if user1.id != user2.id:
                if db.search(User['user1-id'] == f'{user1.id}') or db.search(User['user2-id'] == f'{user2.id}'):
                    await ctx.send(f'A pair already exist for either <@{user1.id}> or <@{user2.id}>. Please unpair them first using `/unpair` before attempting to pair!.', ephemeral=True)
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
                        await ctx.send(f'Pair successfully added for <@{user1.id}> & <@{user2.id}> with nickname "{nickname}"')
                    else:
                        await ctx.send(f'Pair successfully added for <@{user1.id}> & <@{user2.id}>')
            else:
                await ctx.send("ERROR: Can't pair a user to themselves!", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @slash_command(
        name='pair-nick',
        description='Add or update the nickname of a pair',
        dm_permission=False,
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
    async def pair_nick(ctx: SlashContext, user: interactions.Member, nickname: str):
        log_command(ctx=ctx, cmd="pair-nick")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if db.search(User['user1-id'] == f'{user.id}') or db.search(User['user2-id'] == f'{user.id}'):
                db.update({'nickname': f'{nickname}', 'last-change-utc': f'{datetime.utcnow()}'}, ((User['user1-id'] == f'{user.id}') | (User['user2-id'] == f'{user.id}')))
                await ctx.respond(f"Successfully updated nickname of <@{user.id}>'s pair to '{nickname}'")
            else:
                await ctx.respond(f"There was no pair found for <@{user.id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @slash_command(
        name='partner',
        description='Display the partner of someone',
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name='user',
                description='The use of who you wish to view the partner of',
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
    )
    async def partner(ctx: SlashContext, user:interactions.Member):
        log_command(ctx=ctx, cmd="partner")
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
                await ctx.respond(f"The partner of <@{user.id}> is <@{partner_id}>. Their nickname is '{nickname}'", ephemeral=True)
            else:
                await ctx.respond(f"The partner of <@{user.id}> is <@{partner_id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    @slash_command(
        name='unpair',
        description='Unpair a pair of users',
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
              name='user',
              description='Either user of the pair you wish to unpair',
              type=interactions.OptionType.USER,
              required=True
            ),
        ],
    )
    async def unpair(ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="unpair")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/pairs.json', indent=4, create_dirs=True)
            db.default_table_name = 'pairs'

            if db.search(User['user1-id'] == f'{user.id}'):
                await ctx.respond(f"Unpair successful for <@{user.id}> & <@{db.search(User['user1-id'] == f'{user.id}')[0]['user2-id']}>")
                db.remove(User['user1-id'] == f'{user.id}')
            elif db.search(User['user2-id'] == f'{user.id}'):
                await ctx.respond(f"Unpair successful for <@{user.id}> & <@{db.search(User['user2-id'] == f'{user.id}')[0]['user1-id']}>")
                db.remove(User['user2-id'] == f'{user.id}')
            else:
                await ctx.respond(f"There was no pair found for <@{user.id}>", ephemeral=True)

            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    asyncio.run(main())
