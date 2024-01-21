from datetime import datetime

import interactions
from dateutil.relativedelta import relativedelta
from interactions import Extension, slash_command, SlashContext
from tinydb import TinyDB

from automations.log import log_command
from shared import ROOT_DIR, User


class Bday(Extension):
    @slash_command(
        name="bday",
        dm_permission=False,
        sub_cmd_name="add",
        sub_cmd_description="Add your birthday",
        options=[
            interactions.SlashCommandOption(
                name="date",
                description="YYYY-MM-DD Example: 1992-01-31 or 2005-12-05",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def bday(self, ctx: SlashContext, date: str):
        log_command(ctx=ctx, cmd="bday.set")
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
                        db.update({'bday': f'{fdate}', 'last-change-utc': f'{datetime.utcnow()}'},
                                  User['user-id'] == f'{ctx.user.id}')
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

    @bday.subcommand(
        sub_cmd_name="show",
        sub_cmd_description="Show someones bday",
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="Who's bday do you wish to show?",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def bday_show(self, ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="bday.show")
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

    @bday.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List all birthdays",
    )
    async def bday_list(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="bday.list")
        embed = interactions.Embed(title="All Birthdays:", color="#9b59b6")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
            db.default_table_name = 'bdays'
            for bday in db.all():
                bday_str = bday['bday']
                bdate = datetime.strptime(bday_str, '%Y-%m-%d %H:%M:%S')
                today = datetime.now()
                age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
                embed.add_field(name=f"{bday['user']}", value=f"{bdate.strftime('%B %d, %Y')} ({age} years old)",
                                inline=False)
            db.close()
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)
        await ctx.respond(embed=embed)
