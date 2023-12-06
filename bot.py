import interactions
from datetime import datetime
from tinydb import TinyDB, Query, where
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
User = Query()


def log_command(ctx, cmd):
    db = TinyDB(f'{ROOT_DIR}/db/logs.json', indent=4, create_dirs=True)
    db.default_table_name = f'{cmd}'
    db.insert({
        'time-utc': f'{datetime.utcnow()}',
        'user': f'{ctx.user}',
        'user-id': f'{ctx.user.id}',
        'guild-id': f'{ctx.guild_id}',
        'channel': f'{ctx.channel}',
        'channel-id': f'{ctx.channel_id}'
    })
    db.close()
    print(f"{ctx.user}(uid:{ctx.user.id}) used /{cmd} in {ctx.channel}(chid:{ctx.channel_id})(gid:{ctx.guild_id}) at UTC:{datetime.utcnow()}")


def run_discord_bot(token):
    bot = interactions.Client(token=token)

    @bot.event
    async def on_ready():
        print('Bot is now running!')

    @bot.command(
        name="ping",
        description="Test bot latency",
        dm_permission=False
    )
    async def ping(ctx: interactions.CommandContext):
        log_command(ctx=ctx, cmd="ping")
        await ctx.send(f"Pong! The response time is {bot.latency}ms")

    @bot.command(
        name="quote",
        description="Quote someone's dumb words",
        dm_permission=False,
        options=[
            interactions.Option(
                name="text",
                description="What do you wish to quote?",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="user",
                description="Select user to mention",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def quote(ctx: interactions.CommandContext, text: str, user: interactions.Member):
        log_command(ctx=ctx, cmd="quote")
        await ctx.send(f'"{text}"\t~{user.mention}')

    @bot.command(
        name="bday-set",
        description="Add your birthday to the bot",
        dm_permission=False,
        options=[
            interactions.Option(
                name="date",
                description="YYYY-MM-DD Example: 1992-01-31 or 2005-12-05",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def bday_set(ctx: interactions.CommandContext, date: str):
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
                        db.update({'date': f'{fdate}'}, User['user-id'] == f'{ctx.user.id}')
                        await ctx.send(f'Bday succesfully changed for {ctx.user.mention}: "{fdate.strftime("%d %B, %Y")}"')
                    else:
                        db.insert({
                            'user': f'{ctx.user}',
                            'user-id': f'{ctx.user.id}',
                            'date': f'{fdate}',
                            'last-change-utc': f'{datetime.utcnow()}'
                        })
                        await ctx.send(f'Bday succesfully added for {ctx.user.mention}: "{fdate.strftime("%d %B, %Y")}"')
                    db.close()
            else:
                await ctx.send(f"ERROR: Make sure to use the correct seperator '-' and give the year, month and day", ephemeral=True)
        except ValueError:
            await ctx.send(f"ERROR: Date is invalid", ephemeral=True)

    @bot.command(
        name="bday-show",
        description="Show someones bday",
        dm_permission=False,
        options=[
            interactions.Option(
                name="user",
                description="Who's bday do you wish to show?",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def bday_show(ctx: interactions.CommandContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="bday-show")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
            db.default_table_name = 'bdays'
            date = db.search(where('user-id') == user.id)
            db.close()
            if date:
                date = date[0]['date']
                await ctx.send(f"Bday of {user} is {date}", ephemeral=True)
            else:
                await ctx.send(f"ERROR: No birthday found for {user}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    bot.start()
