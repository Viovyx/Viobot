import interactions
from interactions import Extension, slash_command, SlashContext

from automations.log import log_command


class Clear(Extension):
    @slash_command(
        name="clear",
        dm_permission=False,
        sub_cmd_name="amount",
        sub_cmd_description="Clear a certain amount of messages",
        options=[
            interactions.SlashCommandOption(
                name="amount",
                description="How many messages should be deleted?",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="user",
                description="From which user should the messages be deleted?",
                type=interactions.OptionType.USER,
                required=False
            ),
        ],
    )
    async def clear(self, ctx: SlashContext, amount: int, user: interactions.Member=None):
        log_command(ctx=ctx, cmd="clear.amount")
        deleted = await ctx.channel.purge(deletion_limit=amount, predicate=lambda m: m.author.id == user.id if user else True)
        await ctx.send(f"{deleted} messages deleted {'from ' + user.mention if user else ''}", ephemeral=True)

    @clear.subcommand(
        sub_cmd_name="all",
        sub_cmd_description="Clear all messages in the current channel",
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="From which user should the messages be deleted?",
                type=interactions.OptionType.USER,
                required=False
            ),
        ],
    )
    async def clear_all(self, ctx: SlashContext, user: interactions.Member=None):
        log_command(ctx=ctx, cmd="clear.all")
        deleted = await ctx.channel.purge(predicate=lambda m: m.author.id == user.id if user else True)
        await ctx.send(f"{deleted} messages deleted {'from ' + user.mention if user else ''}", ephemeral=True)
