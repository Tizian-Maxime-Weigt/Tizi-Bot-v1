import nextcord
import requests
import speedtest
import asyncio
import datetime
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from nextcord.ext import commands
from nextcord import File, ButtonStyle, Embed, Color, SelectOption, Intents, Interaction, SlashOption, Member
from nextcord.ui import Button, View, Select
from nextcord.ext.commands import Bot

intents = Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot = Bot(command_prefix="/", intents=intents)

weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=de'
API_KEY = 'c7e9c062587c337eeeb12c463912148c'

latency_values = {}

youtube_dl.utils.bug_reports_message = lambda: ''

wordlist = [
 "guten Morgen", "guten morgen", "Guten Morgen", "Guten morgen", "hallo",
 "Hallo", "hi", "Hi", "hey", "Hey", "servus", "Servus"
]
wordlist2 = [
 "gute Nacht", "gute nacht", "Gute Nacht", "Gute nacht", "tschüss", "Tschüss",
 "auf wiedersehen", "Auf Wiedersehen", "bis später", "Bis später"
]


@bot.event
async def on_ready():
	guilds = [guild.id for guild in bot.guilds]
	await bot.change_presence(activity=nextcord.Game(
	 name=f"mit {len(bot.users)} Nutzern | /help"))
	print(
	 f"The {bot.user.name} Bot ist in {len(guilds)} Servern.\nThe Server ids list : {guilds}"
	)
	print(f"-----\nEingeloggt als: {bot.user.name} : {bot.user.id}\n-----")


@bot.slash_command(name="ping", description="Ping command")
async def ping(interaction: Interaction):
	await interaction.response.send_message("Pong!")


@bot.slash_command(name="echo", description="Repeats your message")
async def echo(interaction: Interaction,
               arg: str = SlashOption(description="Message")):
	await interaction.response.send_message(arg)


@bot.slash_command(name="enter-a-numer", description="Choose a number")
async def enter_a_number(
  interaction: Interaction,
  number: int = SlashOption(description="Your number", required=False),
):
	if not number:
		await interaction.response.send_message("No number was specified!",
		                                        ephemeral=True)
	else:
		await interaction.response.send_message(f"You chose {number}!")


@bot.slash_command(name='help')
async def list_commands(ctx):
	"""Zeigt eine Liste der verfügbaren Befehle an."""
	embed = nextcord.Embed(title='Verfügbare Befehle', color=0xff0000)
	for cmd in bot.commands:
		if not cmd.hidden:
			embed.add_field(name=cmd.name, value=cmd.help, inline=False)
	await ctx.send(embed=embed)


@bot.slash_command(name='hilfe')
async def list_commands_german(ctx):
	"""Zeigt eine Liste der verfügbaren Befehle an."""
	embed = nextcord.Embed(title='Verfügbare Befehle', color=0xff0000)
	for cmd in bot.commands:
		if not cmd.hidden:
			embed.add_field(name=cmd.name, value=cmd.help, inline=False)
	await ctx.send(embed=embed)


@bot.event
async def on_message(message):
	if message.type == nextcord.MessageType.premium_guild_subscription:
		channel = bot.get_channel(1074745223697154130)
		embed = nextcord.Embed(
		 title=":wave: Danke für den Serverboost!",
		 description=f"Danke für den Serverboost! {message.author.mention}!")
		embed.add_field(name="**Nicht vergessen!**",
		                value="Vergiss nicht deine Vorteile abzuholen!")
		embed.set_image(
		 url=
		 "https://cdn.nextcordapp.com/attachments/1035876269394493490/1044436064753950800/ligne-gif-nextcord-line.gif"
		)
		await channel.send(embed=embed)
		print(message)

	if any(word in message.content for word in wordlist):
		await message.channel.send(
		 f'Moinsen {message.author.mention} :wave: ! Freut mich dich wieder zu sehen! Wie gehts dir?'
		)

	if any(word in message.content for word in wordlist2):
		await message.channel.send(
		 f'Ich wünsche einen erholsamen Schlaf :zzz: ! Aber komm morgen wieder! {message.author.mention}'
		)


@bot.event
async def on_member_join(member):
	channel = bot.get_channel(1074745223697154130)
	embed = nextcord.Embed(
	 title=":wave: Willkommen auf **Tizi-Development**",
	 description=
	 f"Herzlich willkommen {member.mention}! Bitte vergiss nicht die Regeln zu akzeptieren und lass doch gerne ein hallo da!"
	)
	embed.add_field(
	 name="Wir freuen uns dich zu sehen",
	 value=f"Du bist der {len(set(bot.users))}. Member auf diesem Server!")
	embed.set_image(
	 url=
	 "https://cdn.nextcordapp.com/attachments/1035876269394493490/1044453962008506459/GIF.gif"
	)
	embed.timestamp = datetime.datetime.today()
	await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
	channel = bot.get_channel(1074745223697154130)
	embed = nextcord.Embed(
	 title=":wave: Du gehst schon?",
	 description=f"Anscheinend war {member.mention} nicht cool genug für uns!")
	embed.set_image(
	 url=
	 "https://cdn.nextcordapp.com/attachments/1074745223697154130/1044440675451674724/giphy.gif"
	)
	embed.timestamp = datetime.datetime.today()
	await channel.send(embed=embed)


@bot.slash_command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: nextcord.Member, role: nextcord.Role):
	if role in member.roles:
		await member.remove_roles(role)
		embed = nextcord.Embed(
		 title='Rollen vergabe',
		 description=
		 f"Rolle {role.mention} wurde erfolgreich {member.mention} **entfernt**!",
		 colour=nextcord.Colour.dark_purple())
		await ctx.respond(embed=embed)

	else:
		await member.add_roles(role)

		embed = nextcord.Embed(
		 title='Rollen vergabe',
		 description=
		 f"Rolle {role.mention} wurde erfolgreich {member.mention} **hinzugefügt**!",
		 colour=nextcord.Colour.dark_purple())
		await ctx.respond(embed=embed)


@bot.slash_command(name="delete",
                   description="Lösch die Nachrichten einer bestimmten Person!"
                   )
@commands.has_permissions(manage_messages=True)
async def self(ctx, amount: int, member: nextcord.Member):
	channel = ctx.channel

	def check_author(m):
		return m.author.id == member.id

	await channel.purge(limit=amount, check=check_author)
	embed = nextcord.Embed(
	 title='Chat Löschen',
	 description=
	 f"Erfolgreich {amount} Nachrichten von **{member.name}** gelöscht!",
	 colour=nextcord.Colour.dark_purple())
	await ctx.send(embed=embed, ephemeral=True)


@bot.slash_command(name='unmute', description="unmutes/untimeouts a member")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: nextcord.Member, reason: str = None):
	if reason is None:
		await member.remove_roles(get_muted_role(ctx.guild))
		await ctx.respond(
		 f"**{member.mention}** was unmuted by **{ctx.author.mention}**.")
	else:
		await member.remove_roles(get_muted_role(ctx.guild), reason=reason)
		await ctx.respond(
		 f"**{member.mention}** was unmuted by **{ctx.author.mention}** for **'{reason}'**."
		)


@bot.slash_command(name="vorstellen")
async def vorstellen(
 interaction: nextcord.Interaction,
 alter: str,
 wohnort: str,
 name: str,
 hobbys: str,
 geschlecht: str,
 wunsch: str = None,
):
	embed = nextcord.Embed(
	 title=":fire: Vorstellung :fire:",
	 description=f"Vorstellung von {interaction.user.mention}")
	embed.add_field(name="Dein Wohnort", value=wohnort)
	embed.add_field(name="Dein Alter", value=alter, inline=False)
	embed.add_field(name="Dein Name", value=name, inline=False)
	embed.add_field(name="Deine Hobbys", value=hobbys, inline=False)
	embed.add_field(name="Dein Geschlecht", value=geschlecht, inline=False)
	embed.add_field(name="Dein Wunsch für die Zukunft",
	                value=wunsch,
	                inline=False)
	await interaction.response.send_message(embed=embed)


@unmute.error
async def unmuteerror(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.respond(
		 "You do not have the necessary permissions to use this command!")
	else:
		raise error


@bot.slash_command(name="beichten")
async def beichten(ctx, beichte: str):
	embed = nextcord.Embed(title=":mute: Beichte")
	embed.add_field(name="Beichte von **ANONYM**!", value=beichte)
	await ctx.send(content="Deine Nachricht wurde anonym geposted!", embed=embed)


@bot.slash_command(name="invite")
async def invite(ctx):
	embed = nextcord.Embed(color=nextcord.Colour.dark_teal())
	embed.add_field(
	 name='Ich wünschte du fügst mich deinem Server hinzu,',
	 value=
	 '[Click here to add](https://Discord.com/api/oauth2/authorize?client_id=1044673831035490385&permissions=1102158260279&scope=bot)',
	 inline=False)
	await ctx.respond(embed=embed)


@bot.slash_command(name="kissmarrykillorlove",
                   description="Zeige das Wetter für eine bestimmte Stadt")
async def kissmarrykill(interaction: nextcord.Interaction, heiraten: str,
                        küssen: str, töten: str, love: str):
	embed = nextcord.Embed(title=" :ring: KISS MARRY KILL OR LOVE :ring: ")
	embed.add_field(name="Wen küsst du? :kiss: ", value=küssen)
	embed.add_field(name="Wen heiratest du? :ring: ",
	                value=heiraten,
	                inline=False)
	embed.add_field(name="Wen tötest du? :knife:", value=töten, inline=False)
	embed.add_field(name="Wen Liebst du? :heart:", value=love, inline=False)
	await interaction.response.send_message(embed=embed)


@bot.slash_command(name="wetter",
                   description="Zeige das Wetter für eine bestimmte Stadt")
async def weather(ctx, stadt: str):
	response = requests.get(weather_url.format(stadt, API_KEY))
	data = response.json()

	if data["cod"] != "404":
		city_name = data["name"]
		temperature = data["main"]["temp"]
		feels_like = data["main"]["feels_like"]
		temp_max = data["main"]["temp_max"]
		weather_description = data["weather"][0]["description"]
		wind_speed = data["wind"]["speed"]

		embed = nextcord.Embed(title=f"Wetter für {city_name}",
		                       description=f"Beschreibung: {weather_description}\n"
		                       f"Temperatur: {temperature}°C\n"
		                       f"Temperatur Maximal: {temp_max}°C\n"
		                       f"Gefühlt wie: {feels_like}°C\n"
		                       f"Windgeschwindigkeit: {wind_speed}m/s\n",
		                       colour=nextcord.Colour.dark_purple())
		await ctx.send(embed=embed)
	else:
		await ctx.send(f"Konnte kein Wetter für {stadt} finden.")


@bot.slash_command()
async def serverinfo(interaction):
	guild = interaction.guild
	embed = nextcord.Embed(title=f"{guild.name} Informationen",
	                       description=f"Informationen zu {guild.name}",
	                       color=nextcord.Color.blue())
	embed.set_thumbnail(url=guild.icon.url)
	embed.add_field(name="Mitglieder", value=guild.member_count)
	embed.add_field(name="Sprach-Kanäle", value=len(guild.voice_channels))
	embed.add_field(name="Text-Kanäle", value=len(guild.text_channels))
	embed.add_field(name='Server erstellt am',
	                value=guild.created_at.strftime('%d.%m.%Y %H:%M:%S'),
	                inline=False)
	embed.add_field(name='Server-Owner', value=guild.owner.mention)
	embed.add_field(name='Region', value=str(guild.region))
	embed.add_field(name='Rollen', value=len(guild.roles))
	embed.add_field(name='Emojis', value=len(guild.emojis))
	embed.add_field(name='Bot-Name', value=interaction.bot.name)
	embed.add_field(name='Bot-ID', value=interaction.bot.id)
	embed.add_field(name='Bot-Diskriminator', value=interaction.bot.discriminator)
	embed.add_field(name='Bot-Status', value=str(interaction.bot.status))
	embed.add_field(name='Bot-Latenz',
	                value=f'{round(interaction.bot.latency * 1000)}ms')
	await interaction.response.send_message(embed=embed)


@bot.slash_command(name="timeout",
                   description="Temporarily bans a member from the server")
async def timeout(
 interaction: nextcord.Interaction,
 member: nextcord.Member,
 reason: str = "",
 days: int = 0,
 hours: int = 0,
 minutes: int = 0,
 seconds: int = 0,
):
	total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
	if total_seconds <= 0:
		await interaction.response.send_message("Invalid timeout duration.")
		return
	await member.ban(reason=reason)
	await interaction.response.send_message(
	 f"{member} has been temporarily banned for {total_seconds} seconds.")
	await asyncio.sleep(total_seconds)
	await member.unban(reason="Timeout complete.")
	await interaction.response.send_message(f"{member} has been unbanned.")


@bot.slash_command()
async def cip(ctx, code: str):
	headers = {
	 'User-Agent':
	 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
	}
	urlfivem = f"https://servers-frontend.fivem.net/api/servers/single/{code}"
	response = requests.get(urlfivem)

	if response.status_code == 404:
		mensaje = nextcord.Embed(title="Error",
		                         description="Invalid Code",
		                         color=0xc73e10)
		await ctx.send(embed=mensaje)
	else:
		response = requests.get(urlfivem, headers=headers)
		out = response.json()
		mensaje = nextcord.Embed(
		 title="IP:Port",
		 description=f"`{out['Data']['connectEndPoints'][0]}`",
		 color=0xc73e10)
		await ctx.send(embed=mensaje)


@bot.slash_command(description="Streams a YouTube video.")
async def play(ctx: nextcord.Interaction, url: str):
	voice_channel = ctx.user.voice.channel
	if voice_channel is None:
		await ctx.send("You must be in a voice channel to use this command.")
		return
	vc = await voice_channel.connect()

	ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
    }
	ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
    }
	with YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		URL = info['formats'][0]['url']
		source = await nextcord.FFmpegOpusAudio.from_probe(URL)

	vc.play(source)
	await ctx.send(f"Now playing: {info['title']}")


bot.run(
 "BOT_TOKEN_HERE")
