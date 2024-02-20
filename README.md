# Viobot

A Discord bot made with Python mainly used for my private server.

The bot uses TinyDB to create file based databases in readable json format. This makes it easy to manage saved data.

**NEW!** There is now full support for the games **Truth or Dare**, **Never Have I Ever**, **Would You Rather** and **Paranoia**!
There might still be bugs present that I haven't discovered yet myself, so feel free to report them to me!

## Current command list:

##### General Commands

- `/ping`
- `/quote`

##### Bday Commands

- `/bday add`
- `/bday show`
- `/bday list`

##### Nickname Commands

- `/nickname add`
- `/nickname show`
- `/nickname list`

##### Pairing Commands

- `/pair add`
- `/pair nickname`
- `/pair partner`
- `/pair remove`
- `/pair list`

##### Play Commands

- `/play start`
- `/play stop`
- `/play players`

##### Clear Commands
- `/clear all`
- `/clear amount`

## How to set up?
1) Clone the repository and unpack it.

2) Make sure to have python3 installed and install the `requirements.txt` packages.

3) Create a `.env` file at the root of the project containing the following.
Make sure to replace the parameters inside `<...>` with your own parameters!

    ```dotenv
    TOKEN='<YOUR BOTS TOKEN>'
    BDAY_CHANNEL_ID='<THE CHANNEL-ID FOR BDAY MESSAGES>'
    ```
4) Run the bot with `python3 main.py` and you're done!

**Any problems? Feel free to contact me on discord: @viovyx**

## TO-DO

- [x] simplify command usage with sub-commands
- [x] add list command for all db's
- [x] add truth or dare commands with api
- [ ] add automatically updated embeds displaying db contents (bdays, nicknames & pairs)
- [ ] add auto added and removed bday role
- [ ] sort list command embeds (bdays, nicknames & pairs)
