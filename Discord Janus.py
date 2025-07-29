import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime

class JanusPenthosRP:
    def __init__(self):
        self.save_slots = 3
        self.reset_character()
        
    def reset_character(self):
        """Initialize a new character with 3 free stat points"""
        self.stats = {
            "VIT": 0,    # Vitality (HP)
            "INT": 0,    # Intelligence (MP)
            "STR": 0,    # Strength (Attack)
            "DEF": 0,    # Defense (Damage Reduction)
            "AGI": 0     # Agility (Evasion)
        }
        self.base_hp = 100
        self.base_mp = 25
        self.level = 1
        self.stat_points = 3
        self.character_name = "Unnamed Champion"
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.exp = 0
        self.next_level_exp = self.calculate_exp_requirement()
        
        # Equipment system
        self.equipment = {
            "Weapon": {"name": "Fists", "damage": 0, "bonus": {}},
            "Armor": {"name": "Clothes", "defense": 0, "bonus": {}},
            "Accessory": {"name": "None", "bonus": {}}
        }

    def calculate_exp_requirement(self):
        """Calculate EXP needed for next level"""
        return 100 * (2 ** (self.level - 1))

    def calculate_derived_stats(self):
        """Calculate stats including equipment bonuses"""
        stats = {
            "HP": max(1, self.base_hp + (self.stats["VIT"] * 5)),
            "MP": max(0, self.base_mp + (self.stats["INT"] * 2)),
            "ATK": max(1, 10 + self.stats["STR"] + self.equipment["Weapon"]["damage"]),
            "DEF": self.stats["DEF"] + self.equipment["Armor"]["defense"],
            "EVA": max(0, min(95, self.stats["AGI"] * 0.5))
        }
        
        # Apply equipment bonuses
        for item in self.equipment.values():
            for stat, bonus in item["bonus"].items():
                if stat in stats:
                    stats[stat] += bonus
                    
        return stats

    def save_character(self, filename):
        """Save character data to JSON file"""
        data = {
            "name": self.character_name,
            "stats": self.stats,
            "level": self.level,
            "stat_points": self.stat_points,
            "exp": self.exp,
            "base_hp": self.base_hp,
            "base_mp": self.base_mp,
            "created": self.creation_date,
            "equipment": self.equipment,
            "next_level_exp": self.next_level_exp,
            "system": "Janus Penthos RP"
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_character(self, filename):
        """Load character from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            if data.get("system") != "Janus Penthos RP":
                return False
                
            self.character_name = data["name"]
            self.stats = data["stats"]
            self.level = data["level"]
            self.stat_points = data["stat_points"]
            self.exp = data["exp"]
            self.base_hp = data["base_hp"]
            self.base_mp = data["base_mp"]
            self.creation_date = data.get("created", "Unknown")
            self.equipment = data.get("equipment", {
                "Weapon": {"name": "Fists", "damage": 0, "bonus": {}},
                "Armor": {"name": "Clothes", "defense": 0, "bonus": {}},
                "Accessory": {"name": "None", "bonus": {}}
            })
            self.next_level_exp = data.get("next_level_exp", self.calculate_exp_requirement())
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error loading character: {e} - Discord Janus.py:106")
            return False

    def random_roll_stats(self):
        """Randomize starting stats between -2 to 3"""
        for stat in self.stats:
            roll = random.randint(-2, 3)
            self.stats[stat] = max(-5, min(5, roll))
            
            # 10% chance for Janus blessing
            if random.random() < 0.1:
                self.stats[stat] = min(5, self.stats[stat] + 1)
            
            # 5% chance for Penthos curse
            elif random.random() < 0.05:
                self.stats[stat] = max(-5, self.stats[stat] - 1)

# Discord Bot Implementation
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
user_games = {}

def get_user_game(user_id):
    if user_id not in user_games:
        user_games[user_id] = JanusPenthosRP()
        # Try to load last save automatically
        if not os.path.exists('data'):
            os.makedirs('data')
        user_games[user_id].load_character(f"data/champion_{user_id}.json")
    return user_games[user_id]

def create_stats_embed(character):
    derived = character.calculate_derived_stats()
    
    embed = discord.Embed(
        title=f"{character.character_name} - Level {character.level}",
        description=f"EXP: {character.exp}/{character.next_level_exp}",
        color=0x00ff00
    )
    
    # Core Stats
    stats_field = "\n".join([f"{stat}: {value:>+2}" for stat, value in character.stats.items()])
    embed.add_field(name="Attributes", value=stats_field, inline=True)
    
    # Derived Stats
    derived_field = (
        f"HP: {derived['HP']}\n"
        f"MP: {derived['MP']}\n"
        f"ATK: {derived['ATK']}\n"
        f"DEF: {derived['DEF']}\n"
        f"EVA: {derived['EVA']:.1f}%"
    )
    embed.add_field(name="Stats", value=derived_field, inline=True)
    
    # Equipment
    equipment_field = (
        f"Weapon: {character.equipment['Weapon']['name']} (+{character.equipment['Weapon']['damage']} ATK)\n"
        f"Armor: {character.equipment['Armor']['name']} (+{character.equipment['Armor']['defense']} DEF)\n"
        f"Accessory: {character.equipment['Accessory']['name']}"
    )
    embed.add_field(name="Equipment", value=equipment_field, inline=False)
    
    if character.stat_points > 0:
        embed.set_footer(text=f"{character.stat_points} stat points available to distribute")
    
    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id}) - Discord Janus.py:177')
    print('')

@bot.command()
async def character(ctx):
    """View your character sheet"""
    game = get_user_game(ctx.author.id)
    embed = create_stats_embed(game)
    await ctx.send(embed=embed)

@bot.command()
async def create(ctx, *, name: str):
    """Create a new character"""
    game = get_user_game(ctx.author.id)
    game.reset_character()
    game.character_name = name
    game.random_roll_stats()
    game.save_character(f"data/champion_{ctx.author.id}.json")
    
    embed = create_stats_embed(game)
    await ctx.send(f"Character {name} created!", embed=embed)

@bot.command()
async def distribute(ctx, stat: str):
    """Distribute a stat point"""
    game = get_user_game(ctx.author.id)
    stat = stat.upper()
    
    if game.stat_points <= 0:
        await ctx.send("You don't have any stat points to distribute!")
        return
    
    if stat not in game.stats:
        await ctx.send("Invalid stat! Use VIT, INT, STR, DEF, or AGI")
        return
    
    game.stats[stat] += 1
    game.stat_points -= 1
    game.save_character(f"data/champion_{ctx.author.id}.json")
    
    derived = game.calculate_derived_stats()
    await ctx.send(
        f"{stat} increased to {game.stats[stat]}!\n"
        f"HP: {derived['HP']} | MP: {derived['MP']} | ATK: {derived['ATK']} | "
        f"DEF: {derived['DEF']} | EVA: {derived['EVA']:.1f}%"
    )

@bot.command()
async def equip(ctx, slot: str, name: str, power: int = 0, stat: str = None, bonus: int = 0):
    """Equip an item"""
    game = get_user_game(ctx.author.id)
    slot = slot.capitalize()
    
    if slot not in game.equipment:
        await ctx.send("Invalid slot! Use Weapon, Armor, or Accessory")
        return
    
    game.equipment[slot]["name"] = name
    
    if slot == "Weapon":
        game.equipment[slot]["damage"] = power
    elif slot == "Armor":
        game.equipment[slot]["defense"] = power
    
    if stat and bonus:
        stat = stat.upper()
        if stat in game.stats:
            game.equipment[slot]["bonus"] = {stat: bonus}
        else:
            await ctx.send("Invalid stat bonus! No bonus applied.")
    
    game.save_character(f"data/champion_{ctx.author.id}.json")
    await ctx.send(f"Equipped {name} in {slot} slot!")

@bot.command()
@commands.is_owner()
async def admin_reset(ctx, user: discord.Member = None):
    """Admin command to reset a character"""
    target = user or ctx.author
    user_games[target.id] = JanusPenthosRP()
    await ctx.send(f"Reset character for {target.display_name}")

@bot.command()
async def roll(ctx):
    """Roll for a random event"""
    game = get_user_game(ctx.author.id)
    events = [
        "You find a mysterious artifact",
        "A wandering merchant offers you a deal",
        "You encounter a hidden shrine",
        "The path ahead splits unexpectedly",
        "You feel the gaze of unseen watchers"
    ]
    event = random.choice(events)
    
    # 30% chance for stat change
    if random.random() < 0.3:
        stat = random.choice(list(game.stats.keys()))
        change = random.choice([-1, 1])
        game.stats[stat] += change
        stat_change = f"\n\n{stat} changed by {change:+d} (now {game.stats[stat]})"
        game.save_character(f"data/champion_{ctx.author.id}.json")
    else:
        stat_change = ""
    
    await ctx.send(f"{event}{stat_change}")

# Run the bot
if not os.path.exists('data'):
    os.makedirs('data')

bot.run('YOMTM5OTYwNzAyODAwNzMwOTQ3Ng.GjLkQ4.kWuj-BqVUsLAZGUm0r0-M_e825v7wbMz8j6xJI')