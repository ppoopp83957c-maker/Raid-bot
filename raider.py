import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from colorama import init, Fore, Style

init(autoreset=True)

def save_token(token):
    with open("token.json", "w") as file:
        json.dump({"TOKEN": token}, file)

def load_token():
    try:
        with open("token.json", "r") as file:
            data = json.load(file)
            return data.get("TOKEN")
    except FileNotFoundError:
        print(Fore.RED + "Error: token.json not found.")
        return None
    except json.JSONDecodeError:
        print(Fore.RED + "Error: Invalid JSON format in token.json.")
        return None

def load_premium_users():
    try:
        with open("premium_users.json", "r") as file:
            data = json.load(file)
            return data.get("premium_users", [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(Fore.RED + "Error: Invalid JSON format in premium_users.json.")
        return []

def save_premium_users(premium_users):
    with open("premium_users.json", "w") as file:
        json.dump({"premium_users": premium_users}, file, ind ent=2)

def is_premium(user_id):
    premium_users = load_premium_users()
    return user_id in premium_users

def add_premium(user_id):
    premium_users = load_premium_users()
    if user_id not in premium_users:
        premium_users.append(user_id)
        save_premium_users(premium_users)
        return True
    return False

def remove_premium(user_id):
    premium_users = load_premium_users()
    if user_id in premium_users:
        premium_users.remove(user_id)
        save_premium_users(premium_users)
        return True
    return False

def display_logo():
    logo = '''
░░█ ▄▀█ █▀▀ █▄▀ █▀█ █▀ █▀█ ▄▀█ █▀▄▀█
█▄█ █▀█ █▄▄ █░█ █▄█ ▄█ █▀▀ █▀█ █░▀░█ 
'''
    os.system('cls' if os.name == 'nt' else 'clear')  
    print(Fore.BLUE + logo)

def display_status(connected):
    if connected:
        print(Fore.GREEN + "Status: Connected")
    else:
        print(Fore.RED + "Status: Disconnected")

def token_management():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "Welcome to the bot token management!\n")
    print("1. Set new token")
    print("2. Load previous token")
    
    print()

    choice = input(Fore.YELLOW + "Choose an option (1, 2): ")

    if choice == "1":
        new_token = input(Fore.GREEN + "Enter the new token: ")
        save_token(new_token)
        print(Fore.GREEN + "Token successfully set!")
        return new_token
    elif choice == "2":
        token = load_token()
        if token:
            print(Fore.GREEN + f"Previous token loaded: {token}")
            return token
        else:
            print(Fore.RED + "No token found.")
            return None
    else:
        print(Fore.RED + "Invalid choice. Please try again.")
        return None

OWNER_ID = 1386474185034825741

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

class SpamButton(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message

    @discord.ui.button(label="Spam", style=discord.ButtonStyle.red)
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  
        for _ in range(5):  
            await interaction.followup.send(self.message)  

PRESET_MESSAGE = """# LMAO GET RAIDED JOIN US TO LEARN HOW TO RAID AND BEAM ROBLOX ACCOUNTS 👻

@everyone 
https://discord.gg/M8HjnKYsFs"""

@bot.tree.command(name="spamraid", description="Generate a button to spam the raid message")
async def spamraid(interaction: discord.Interaction):
    view = SpamButton(PRESET_MESSAGE)
    await interaction.response.send_message(f"💥SPAM TEXT💥", view=view, ephemeral=True)

@bot.tree.command(name="premiumspam", description="Send a custom spam message (Premium only)")
@app_commands.describe(message="The custom message you want to spam")
async def premiumspam(interaction: discord.Interaction, message: str):
    if not is_premium(interaction.user.id):
        await interaction.response.send_message("❌ This command is only available to premium users!", ephemeral=True)
        return
    
    view = SpamButton(message)
    await interaction.response.send_message(f"💥PREMIUM SPAM TEXT💥 : {message}", view=view, ephemeral=True)

@bot.tree.command(name="set", description="Grant premium status to a user (Owner only)")
@app_commands.describe(user="The user to grant premium status")
async def set_premium(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Only the bot owner can use this command!", ephemeral=True)
        return
    
    if add_premium(user.id):
        await interaction.response.send_message(f"✅ Premium status granted to {user.mention}!", ephemeral=True)
        print(Fore.GREEN + f"Premium granted to {user.name} (ID: {user.id})")
    else:
        await interaction.response.send_message(f"ℹ️ {user.mention} already has premium status!", ephemeral=True)

@bot.tree.command(name="remove", description="Remove premium status from a user (Owner only)")
@app_commands.describe(user="The user to remove premium status from")
async def remove_premium_cmd(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Only the bot owner can use this command!", ephemeral=True)
        return
    
    if remove_premium(user.id):
        await interaction.response.send_message(f"✅ Premium status removed from {user.mention}!", ephemeral=True)
        print(Fore.YELLOW + f"Premium removed from {user.name} (ID: {user.id})")
    else:
        await interaction.response.send_message(f"ℹ️ {user.mention} doesn't have premium status!", ephemeral=True)

@bot.event
async def on_ready():
    display_logo()
    display_status(True)
    print("Connected as " + Fore.YELLOW + f"{bot.user}")

    try:
        await bot.tree.sync()  
        print(Fore.GREEN + "Commands successfully synchronized.")
    except Exception as e:
        display_status(False)
        print(Fore.RED + f"Error during synchronization: {e}")

if __name__ == "__main__":
    TOKEN = token_management()
    if TOKEN:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print(Fore.RED + "Can't connect to token. Please check your token.")
            input(Fore.YELLOW + "Press Enter to go back to the menu...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
        except Exception as e:
            print(Fore.RED + f"An unexpected error occurred: {e}")
            input(Fore.YELLOW + "Press Enter to restart the menu...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
    else:
        print(Fore.RED + "❌ Error: Unable to load or set a token.")
