import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import json
import os

# Battle System Setup
BATTLE_COOLDOWN = timedelta(hours=24)
BATTLES_PER_DAY = 10
CHARACTER_DB = "characters.json"

class Character:
    def __init__(self, name, level=1):
        self.name = name
        self.level = level
        self.exp = 0
        self.next_level_exp = 100 * level
        self.last_battle_time = None
        self.battles_today = 0
        self.stats = {
            "ATK": 5 + level * 2,
            "DEF": 3 + level * 1.5,
            "HP": 50 + level * 10,
            "DEX": 5 + level * 1.2
        }
    
    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "next_level_exp": self.next_level_exp,
            "last_battle_time": self.last_battle_time.isoformat() if self.last_battle_time else None,
            "battles_today": self.battles_today,
            "stats": self.stats
        }
    
    @classmethod
    def from_dict(cls, data):
        char = cls(data["name"], data["level"])
        char.exp = data["exp"]
        char.next_level_exp = data["next_level_exp"]
        char.last_battle_time = datetime.fromisoformat(data["last_battle_time"]) if data["last_battle_time"] else None
        char.battles_today = data["battles_today"]
        char.stats = data["stats"]
        return char
    
    def can_battle(self):
        now = datetime.now()
        if not self.last_battle_time or now.date() > self.last_battle_time.date():
            self.battles_today = 0
            return True
        return self.battles_today < BATTLES_PER_DAY
    
    def time_until_next_battle(self):
        if self.can_battle():
            return "now"
        
        next_reset = (self.last_battle_time + BATTLE_COOLDOWN).replace(
            hour=0, minute=0, second=0
        ) + timedelta(days=1)
        return str(next_reset - datetime.now()).split(".")[0]
    
    def level_up(self):
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.exp -= self.next_level_exp
            self.next_level_exp = 100 * self.level
            self.stats = {
                "ATK": 5 + self.level * 2,
                "DEF": 3 + self.level * 1.5,
                "HP": 50 + self.level * 10,
                "DEX": 5 + self.level * 1.2
            }
            return True
        return False

def load_characters():
    if os.path.exists(CHARACTER_DB):
        with open(CHARACTER_DB, "r") as f:
            return {name: Character.from_dict(data) for name, data in json.load(f).items()}
    return {}

def save_characters(characters):
    with open(CHARACTER_DB, "w") as f:
        json.dump({name: char.to_dict() for name, char in characters.items()}, f, indent=2)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# Battle Commands
@bot.tree.command(name="autobattle", description="Start an auto-battle sequence")
@app_commands.describe(character="Your character's name")
async def autobattle(interaction: discord.Interaction, character: str):
    characters = load_characters()
    
    if character not in characters:
        await interaction.response.send_message(f"❌ Character {character} doesn't exist!", ephemeral=True)
        return
    
    char = characters[character]
    
    if not char.can_battle():
        cooldown = char.time_until_next_battle()
        await interaction.response.send_message(
            f"⏳ {character} has battled too much today! Next battle available in: {cooldown}",
            ephemeral=True
        )
        return
    
    # Generate enemy based on character level
    enemy_level = max(1, char.level + random.randint(-2, 2))
    enemy_types = [
        "Goblin", "Orc", "Skeleton", "Bandit", "Wolf",
        "Spider", "Zombie", "Ghost", "Harpy", "Troll"
    ]
    enemy_type = random.choice(enemy_types)
    
    # Calculate battle stats
    enemy_stats = {
        "HP": 30 + enemy_level * 8,
        "ATK": 5 + enemy_level * 3,
        "DEF": 2 + enemy_level * 2
    }
    
    player_dmg = max(1, char.stats["ATK"] - enemy_stats["DEF"] // 2)
    enemy_dmg = max(1, enemy_stats["ATK"] - char.stats["DEF"] // 2)
    
    # Battle simulation
    battle_log = []
    player_hp = char.stats["HP"]
    enemy_hp = enemy_stats["HP"]
    
    for turn in range(1, 6):  # Max 5 turns
        # Player attack
        crit = random.random() < (char.stats["DEX"] / 100)
        damage = player_dmg * (2 if crit else 1)
        enemy_hp -= damage
        battle_log.append(
            f"**Turn {turn}:** {character} hits {enemy_type} for {damage} damage"
            f"{' (CRIT!)' if crit else ''}"
        )
        
        if enemy_hp <= 0:
            battle_log.append(f"🏆 **Victory!** {character} defeated the {enemy_type}!")
            break
        
        # Enemy attack
        if random.random() > 0.2:  # 20% chance to miss
            player_hp -= enemy_dmg
            battle_log.append(f"💥 {enemy_type} hits {character} for {enemy_dmg} damage")
            
            if player_hp <= 0:
                battle_log.append(f"☠️ **Defeat!** {character} was defeated by the {enemy_type}!")
                player_hp = 1  # Don't let character die
                break
        else:
            battle_log.append(f"💨 {character} dodged the {enemy_type}'s attack!")
    
    # Calculate rewards
    if enemy_hp <= 0:
        exp_gain = 20 + enemy_level * 5
        gold_gain = 10 + enemy_level * 3
        
        # Bonus for higher level enemies
        if enemy_level > char.level:
            exp_gain = int(exp_gain * 1.5)
            gold_gain = int(gold_gain * 1.5)
        
        char.exp += exp_gain
        leveled_up = char.level_up()
        
        reward_msg = (
            f"✨ Gained {exp_gain} EXP and {gold_gain} gold!\n"
            f"🔹 EXP: {char.exp}/{char.next_level_exp}"
        )
        
        if leveled_up:
            reward_msg += f"\n🎉 **Level Up!** {character} is now level {char.level}!"
    else:
        reward_msg = "No rewards earned (battle not won)"
    
    # Update character
    char.battles_today += 1
    char.last_battle_time = datetime.now()
    save_characters(characters)
    
    # Create battle embed
    embed = discord.Embed(
        title=f"⚔️ {character} vs Level {enemy_level} {enemy_type}",
        description="\n".join(battle_log),
        color=0x00ff00 if enemy_hp <= 0 else 0xff0000
    )
    
    embed.add_field(
        name="Battle Results",
        value=f"{character} HP: {player_hp}/{char.stats['HP']}\n"
              f"{enemy_type} HP: {max(0, enemy_hp)}/{enemy_stats['HP']}\n\n"
              f"{reward_msg}",
        inline=False
    )
    
    embed.set_footer(
        text=f"Battles today: {char.battles_today}/{BATTLES_PER_DAY} | "
             f"Next battle: {char.time_until_next_battle()}"
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="create_character", description="Create a new character")
@app_commands.describe(name="Your character's name")
async def create_character(interaction: discord.Interaction, name: str):
    characters = load_characters()
    
    if name in characters:
        await interaction.response.send_message(f"❌ Character {name} already exists!", ephemeral=True)
        return
    
    characters[name] = Character(name)
    save_characters(characters)
    await interaction.response.send_message(f"✅ Created new character: {name} (Level 1)")

@bot.tree.command(name="character_info", description="View character stats")
@app_commands.describe(name="Your character's name")
async def character_info(interaction: discord.Interaction, name: str):
    characters = load_characters()
    
    if name not in characters:
        await interaction.response.send_message(f"❌ Character {name} doesn't exist!", ephemeral=True)
        return
    
    char = characters[name]
    
    embed = discord.Embed(title=f"Character: {name}", color=0x7289da)
    embed.add_field(name="Level", value=char.level, inline=True)
    embed.add_field(name="EXP", value=f"{char.exp}/{char.next_level_exp}", inline=True)
    embed.add_field(name="Battles Today", value=f"{char.battles_today}/{BATTLES_PER_DAY}", inline=True)
    
    stats = "\n".join(f"{stat}: {value}" for stat, value in char.stats.items())
    embed.add_field(name="Stats", value=stats, inline=False)
    
    if not char.can_battle():
        embed.add_field(
            name="Cooldown",
            value=f"Next battle available in: {char.time_until_next_battle()}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN_HERE')
