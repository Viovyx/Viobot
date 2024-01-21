import interactions
from interactions import Extension, slash_command, SlashContext

from automations.log import log_command


class Quote(Extension):
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
    async def quote(self, ctx: SlashContext, text: str, user: interactions.Member):
        log_command(ctx=ctx, cmd="quote")
        await ctx.send(f'"{text}" - {user.mention}')
