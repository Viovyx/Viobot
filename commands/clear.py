import interactions
from interactions import Extension, slash_command, SlashContext

from automations.log import log_command


class Clear(Extension):
    @slash_command(
        name="clear",
        dm_permission=False,
        sub_cmd_name="messages",
        sub_cmd_description="Clear a certain amount of messages. Default is 50 from everyone.",
        options=[
            interactions.SlashCommandOption(
                name="amount",
                description="How many messages should be deleted?",
                type=interactions.OptionType.INTEGER,
                required=False
            ),
            interactions.SlashCommandOption(
                name="user",
                description="From which user should the messages be deleted?",
                type=interactions.OptionType.USER,
                required=False
            ),
        ],
    )
    async def clear(self, ctx: SlashContext, amount: int = 50, user: interactions.Member = None):
        log_command(ctx=ctx, cmd="clear.amount")
        deleted = await ctx.channel.purge(deletion_limit=amount, predicate=lambda m: m.author.id == user.id if user else True)
        await ctx.send(f"{deleted} messages deleted {'from ' + user.mention if user else ''}", ephemeral=True)
