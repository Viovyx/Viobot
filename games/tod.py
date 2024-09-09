import random

import interactions
from interactions import ActionRow, Button, Embed, EmbedField
from tinydb import TinyDB, where

import truthordare
from shared import ROOT_DIR
from shared import User


async def play(ctx, rating, game):
    join_menu = ActionRow(
        Button(
            label="Join",
            custom_id="tod.join",
            style=interactions.ButtonStyle.SUCCESS,
        ),
        Button(
            label="Leave",
            custom_id="tod.leave",
            style=interactions.ButtonStyle.DANGER,
        ),
    )

    start_menu = ActionRow(
        Button(
            label="Start",
            custom_id="tod.start",
            style=interactions.ButtonStyle.PRIMARY,
        ),
        Button(
            label="Stop",
            custom_id="tod.stop",
            style=interactions.ButtonStyle.DANGER,
        ),
    )

    info_embed = Embed(
        title=f"{game.replace('tod', 'Truth or Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
        description="Waiting for the host to start the game...",
        color="#9b59b6",
        fields=[
            EmbedField(name="Host", value=ctx.author.mention, inline=True),
            EmbedField(name="Rating", value=f"{rating.upper() if rating else 'default'}", inline=True),
        ],
    )

    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_settings = db.table('game_settings')
    game_players = db.table('game_players')

    game_settings.truncate()
    game_settings.insert({
        'game': f"{game.replace('tod', 'Truth or Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
        'game-id': f'{game}',
        'rating': f'{rating if rating else "default"}',
        'host': f'{ctx.author.username.removeprefix("@")}',
        'host-id': f'{ctx.author.id}',
        'game-started': 'False',
        'btn_state': 'disabled',
        'total_players': 1,
        'current_player': 1,
    })

    game_players.truncate()
    game_players.insert({
        'user': f'{ctx.author.username.removeprefix("@")}',
        'user-id': f'{ctx.author.id}',
    })

    await ctx.send(embed=info_embed, components=[join_menu])
    await ctx.send(
        "You're hosting this game! Wait for everyone to join and then use these buttons to Start/Stop the game:",
        components=[start_menu], ephemeral=True)


async def join(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_players = db.table('game_players')
    game_settings = db.table('game_settings')

    if game_players.search(User['user-id'] == f'{ctx.author.id}'):
        await ctx.send("You're is already in the game!", ephemeral=True)
    else:
        game_players.insert({
            'user': f'{ctx.author.username.removeprefix("@")}',
            'user-id': f'{ctx.author.id}',
        })
        game_settings.update({'total_players': len(game_players.all())})
        await ctx.send(f"{ctx.author.mention} joined the game!")
    db.close()


async def leave(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_players = db.table('game_players')
    game_settings = db.table('game_settings')

    if game_players.contains(User['user-id'] == f'{ctx.author.id}'):
        game_players.remove(User['user-id'] == f'{ctx.author.id}')
        game_settings.update({'total_players': len(game_players.all())})
        await ctx.send(f"{ctx.author.mention} left the game!")

        current_player = game_settings.search(where('current_player').exists())[0]['current_player']
        total_players = len(game_players.all())
        if current_player > total_players:
            game_settings.update({'current_player': 1})

        if f'{ctx.author.id}' == game_settings.get(where('host-id').exists())['host-id']:
            await ctx.send("The host left the game! Ending game...")
            await stop(ctx)
        elif not game_players:
            await ctx.send("There are no more players left in the game! Ending game...")
            await stop(ctx)
    else:
        await ctx.send("You're not in the game!", ephemeral=True)
    db.close()


async def start(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_settings = db.table('game_settings')
    game_players = db.table('game_players')

    current_player = game_settings.search(where('current_player').exists())[0]['current_player']
    if current_player == 1 and game_settings.search(where('game-started').exists())[0]['game-started'] == 'False':
        game_settings.update({'current_player': random.randint(1, len(game_players.all()))})

    game_settings.update({'game-started': 'True', 'btn_state': 'enabled'})

    game = game_settings.search(where('game').exists())[0]['game']
    current_player = game_settings.search(where('current_player').exists())[0]['current_player']
    player_id = game_players.all()[current_player-1]['user-id']

    game_settings.update({'current_player': current_player + 1 if current_player < len(game_players.all()) else 1})
    options = None
    match game_settings.search(where('game-id').exists())[0]['game-id']:
        case "tod":
            options = ActionRow(
                Button(
                    label="Truth",
                    custom_id="tod.truth",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
                Button(
                    label="Dare",
                    custom_id="tod.dare",
                    style=interactions.ButtonStyle.DANGER,
                ),
                Button(
                    label='Random',
                    custom_id='tod.random',
                    style=interactions.ButtonStyle.PRIMARY,
                ),
            )
        case "nhie":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.nhie",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
        case "wyr":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.wyr",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
        case "paranoia":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.paranoia",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
    options.add_component(
        Button(
            label="Skip",
            custom_id="tod.skip",
            style=interactions.ButtonStyle.SECONDARY,
        ),
    )
    embed = Embed(
        title=game,
        description=f"It's your turn <@{player_id}>! Choose an option to continue the game:",
        color="#9b59b6"
    )
    await ctx.send(embed=embed, components=[options])
    db.close()


async def stop(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_settings = db.table('game_settings')

    await ctx.send(f"Game '{game_settings.get(where('game').exists())['game']}' ended by {ctx.author.mention}!")
    game_settings.truncate()

    game_players = db.table('game_players')
    game_players.truncate()

    db.close()


async def get(ctx, request):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    game_settings = db.table('game_settings')
    game_players = db.table('game_players')

    if game_settings.get(User['game-started'] == 'True'):
        players = [player['user-id'] for player in game_players.all()]
        rating = game_settings.get(where('game').exists())['rating']
        player_id = ctx.author.id

        if str(player_id) not in players:
            await ctx.send("You're not in the game!", ephemeral=True)
            return

        if request != 'continue':
            btn_state = game_settings.get(where('btn_state').exists())['btn_state']
            if btn_state == 'disabled':
                await ctx.send("The button has already been pressed! Wait for the game to continue.", ephemeral=True)
                return
            game_settings.update({'btn_state': 'disabled'})

        if request == 'skip':
            await ctx.send(f"<@{player_id}> skipped!")

        if request != 'skip' and request != 'continue':
            response = getattr(truthordare, request)(rating if rating != 'default' else None)['question']
            game = game_settings.get(where('game').exists())['game']
            embed = Embed(
                title=f"{game}",
                description=f"{response}",
                color="#9b59b6",
                fields=[
                    EmbedField(name="Type",
                               value=f"{request.replace('truth', 'Truth').replace('dare', 'Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
                               inline=True),
                    EmbedField(name="Rating", value=f"{rating.upper()}", inline=True),
                    EmbedField(name="Initiated by", value=f"<@{player_id}>", inline=True),
                ],
            )
            options = ActionRow(
                Button(
                    label="Continue",
                    custom_id="tod.continue",
                    style=interactions.ButtonStyle.PRIMARY,
                ),
                Button(
                    label="Leave",
                    custom_id="tod.leave",
                    style=interactions.ButtonStyle.DANGER,
                ),
            )
            await ctx.send(embed=embed, components=options)
        else:
            if game_players.all():
                await start(ctx)
            else:
                await ctx.send("There are no more players left in the game! Ending game...")
                await stop(ctx)
    else:
        await ctx.send("There is no game happening currently!", ephemeral=True)
