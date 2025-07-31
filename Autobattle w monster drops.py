import discord
from discord.ext import commands, tasks
import random
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import json
import os
from typing import Dict, List, Tuple, Optional

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Data storage setup
DATA_FILE = "player_data.json"

# Load existing player data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save player data
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({k: v.__dict__ for k, v in players.items()}, f, indent=2)

# Game classes
class Player:
    def __init__(self, user_id: int, data: Optional[dict] = None):
        self.user_id = user_id
        self.health = data.get('health', 100) if data else 100
        self.max_health = data.get('max_health', 100) if data else 100
        self.level = data.get('level', 1) if data else 1
        self.exp = data.get('exp', 0) if data else 0
        self.inventory = defaultdict(int, data.get('inventory', {})) if data else defaultdict(int)
        self.battles_today = data.get('battles_today', 0) if data else 0
        self.alive = data.get('alive', True) if data else True
        self.last_battle_time = datetime.fromisoformat(data['last_battle_time']) if data and data.get('last_battle_time') else None
        self.cooldown_complete = data.get('cooldown_complete', True) if data else True
        self.equipment = data.get('equipment', {
            'weapon': None,
            'armor': None,
            'accessory': None
        }) if data else {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        self.gold = data.get('gold', 0) if data else 0
        self.kills = data.get('kills', 0) if data else 0
        self.deaths = data.get('deaths', 0) if data else 0
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'health': self.health,
            'max_health': self.max_health,
            'level': self.level,
            'exp': self.exp,
            'inventory': dict(self.inventory),
            'battles_today': self.battles_today,
            'alive': self.alive,
            'last_battle_time': self.last_battle_time.isoformat() if self.last_battle_time else None,
            'cooldown_complete': self.cooldown_complete,
            'equipment': self.equipment,
            'gold': self.gold,
            'kills': self.kills,
            'deaths': self.deaths
        }
    
    def take_damage(self, amount: int):
        armor_def = self.equipment['armor']['defense'] if self.equipment.get('armor') else 0
        damage = max(1, amount - armor_def)
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.deaths += 1
    
    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
    
    def add_exp(self, amount: int) -> bool:
        self.exp += amount
        if self.exp >= self.level * 100:
            self.level += 1
            self.max_health += 20
            self.health = self.max_health
            return True
        return False
    
    def add_to_inventory(self, item: str, quantity: int = 1):
        self.inventory[item] += quantity
    
    def reset_daily_battles(self):
        self.battles_today = 0
        self.alive = True
        self.health = self.max_health
    
    def check_cooldown(self) -> timedelta:
        if self.last_battle_time:
            time_elapsed = datetime.now() - self.last_battle_time
            if time_elapsed < timedelta(hours=24):
                remaining = timedelta(hours=24) - time_elapsed
                self.cooldown_complete = False
                return remaining
        self.cooldown_complete = True
        return timedelta(0)
    
    def add_gold(self, amount: int):
        self.gold += amount
    
    def equip_item(self, item_type: str, item_name: str):
        if item_name in self.inventory:
            self.equipment[item_type] = {
                'name': item_name,
                'attack': ITEM_STATS.get(item_name, {}).get('attack', 0),
                'defense': ITEM_STATS.get(item_name, {}).get('defense', 0)
            }
            return True
        return False

class Monster:
    def __init__(self, name: str, level: int, exp: int, drops: List[Tuple[str, int, int, int]], gold_range: Tuple[int, int]):
        self.name = name
        self.level = level
        self.exp = exp
        self.drops = drops
        self.gold_range = gold_range
    
    def calculate_drops(self) -> Tuple[List[Tuple[str, int]], int]:
        drops = []
        for item_name, min_qty, max_qty, drop_chance in self.drops:
            if random.random() * 100 <= drop_chance:
                quantity = random.randint(min_qty, max_qty)
                drops.append((item_name, quantity))
        gold = random.randint(*self.gold_range)
        return drops, gold

# Item database
ITEM_STATS = {
    "Goblin Sword": {"attack": 5, "type": "weapon"},
    "Goblin Shield": {"defense": 5, "type": "armor"},
    "Bold Gaze": {"attack": 3, "defense": 3, "type": "accessory"},
    # Add more items...
}

# Monster database
monster_db = {
    "Slime": {
        1: Monster("Slime", 1, 10, [
            ("slime essence", 1, 3, 50),
            ("monster essence", 1, 6, 50)
        ], (1, 5)),
        2: Monster("Slime", 2, 20, [
            ("slime essence", 1, 6, 50),
            ("monster essence", 1, 10, 50)
        ], (3, 8))
    },
    "Goblin": {
        3: Monster("Goblin", 3, 20, [
            ("goblin bones", 1, 3, 49),
            ("monster essence", 1, 6, 49),
            ("bold gaze", 1, 1, 2),
            ("Goblin Sword", 1, 1, 5),
            ("Goblin Shield", 1, 1, 5)
        ], (5, 15))
    }
    # Add more monsters...
}

# Initialize players from saved data
players: Dict[int, Player] = {}
for user_id, data in load_data().items():
    players[int(user_id)] = Player(int(user_id), data)

# Helper functions
def get_player(user_id: int) -> Player:
    if user_id not in players:
        players[user_id] = Player(user_id)
    return players[user_id]

def format_timedelta(td: timedelta) -> str:
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

async def simulate_battle(player: Player, ctx: commands.Context) -> bool:
    monster_name = random.choice(list(monster_db.keys()))
    monster_levels = list(monster_db[monster_name].keys())
    monster_level = random.choice(monster_levels)
    monster = monster_db[monster_name][monster_level]
    
    # Calculate player attack with equipment
    weapon_attack = player.equipment['weapon']['attack'] if player.equipment.get('weapon') else 0
    base_damage = random.randint(5, 15) + weapon_attack
    damage_taken = max(1, (base_damage * monster.level // player.level) - (weapon_attack // 2))
    
    player.take_damage(damage_taken)
    drops, gold = monster.calculate_drops()
    level_up = player.add_exp(monster.exp)
    player.add_gold(gold)
    
    if player.alive:
        player.kills += 1
    
    embed = discord.Embed(
        title=f"Battle #{player.battles_today + 1}",
        color=discord.Color.orange()
    )
    embed.add_field(name="Encounter", value=f"Level {monster.level} {monster.name}", inline=False)
    embed.add_field(name="Damage Taken", value=f"{damage_taken} HP", inline=True)
    embed.add_field(name="Health", value=f"{player.health}/{player.max_health}", inline=True)
    
    if player.alive:
        result_text = f"Victory! +{monster.exp} EXP"
        if gold > 0:
            result_text += f", +{gold} gold"
        embed.add_field(name="Result", value=result_text, inline=False)
        
        if level_up:
            embed.add_field(name="Level Up!", value=f"You are now level {player.level}!", inline=False)
        
        if drops:
            drop_text = "\n".join([f"- {quantity}x {item}" for item, quantity in drops])
            embed.add_field(name="Drops", value=drop_text, inline=False)
            for item, quantity in drops:
                player.add_to_inventory(item, quantity)
    else:
        embed.add_field(name="Defeat", value="You were defeated in battle but managed to run!", inline=False)
    
    await ctx.send(embed=embed)
    return player.alive

# Bot commands
@bot.command(name="battle", help="Start your daily auto-battles (10 battles max)")
async def daily_auto_battle(ctx: commands.Context):
    player = get_player(ctx.author.id)
    cooldown_remaining = player.check_cooldown()
    
    if not player.alive:
        await ctx.send("You're defeated but managed to run away! Use `!rest` to recover before battling again.")
        return
    
    if not player.cooldown_complete:
        embed = discord.Embed(
            title="Auto-Battle Cooldown",
            description=f"Time remaining: {format_timedelta(cooldown_remaining)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if player.battles_today >= 10:
        await ctx.send("You've already completed your 10 battles today.")
        return
    
    embed = discord.Embed(
        title="Starting Daily Auto-Battles",
        description=f"{ctx.author.display_name} engages in 10 battles...",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    
    for _ in range(10 - player.battles_today):
        if not player.alive:
            break
        
        alive = await simulate_battle(player, ctx)
        player.battles_today += 1
        
        if not alive:
            break
        
        await asyncio.sleep(1)
    
    if player.battles_today >= 10:
        player.last_battle_time = datetime.now()
        player.cooldown_complete = False
    
    # Final report
    embed = discord.Embed(
        title="Battle Report",
        color=discord.Color.blue()
    )
    embed.add_field(name="Battles Completed", value=f"{player.battles_today}/10", inline=True)
    embed.add_field(name="Level", value=player.level, inline=True)
    embed.add_field(name="Gold", value=player.gold, inline=True)
    embed.add_field(name="Kills/Deaths", value=f"{player.kills}/{player.deaths}", inline=True)
    
    if not player.alive:
        embed.add_field(name="Status", value="You almost died in battle but managed to run away! Use `!rest` to recover.", inline=False)
    
    await ctx.send(embed=embed)
    save_data()

@bot.command(name="profile", help="View your player profile")
async def player_profile(ctx: commands.Context):
    player = get_player(ctx.author.id)
    cooldown_remaining = player.check_cooldown()
    
    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Profile",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    # Equipment summary
    equipment_text = []
    for slot, item in player.equipment.items():
        if item:
            stats = []
            if item.get('attack', 0) > 0:
                stats.append(f"ATK +{item['attack']}")
            if item.get('defense', 0) > 0:
                stats.append(f"DEF +{item['defense']}")
            equipment_text.append(f"{slot.title()}: {item['name']} ({', '.join(stats)})")
        else:
            equipment_text.append(f"{slot.title()}: Empty")
    
    embed.add_field(name="Stats", value=(
        f"Level: {player.level}\n"
        f"EXP: {player.exp}/{player.level * 100}\n"
        f"Health: {player.health}/{player.max_health}\n"
        f"Gold: {player.gold}\n"
        f"Kills: {player.kills}\n"
        f"Deaths: {player.deaths}"
    ), inline=False)
    
    embed.add_field(name="Equipment", value="\n".join(equipment_text), inline=False)
    embed.add_field(name="Progress", value=(
        f"Battles Today: {player.battles_today}/10\n"
        f"{'Cooldown: ' + format_timedelta(cooldown_remaining) if not player.cooldown_complete else 'Ready to battle!'}"
    ), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="inventory", help="View your inventory")
async def view_inventory(ctx: commands.Context):
    player = get_player(ctx.author.id)
    
    if not player.inventory:
        await ctx.send("Your inventory is empty.")
        return
    
    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Inventory",
        color=discord.Color.purple()
    )
    
    # Group items by type for better organization
    categories = {
        "Materials": [],
        "Equipment": [],
        "Other": []
    }
    
    for item, quantity in player.inventory.items():
        if "essence" in item.lower() or "bone" in item.lower():
            categories["Materials"].append(f"{item}: {quantity}")
        elif item in ITEM_STATS:
            categories["Equipment"].append(f"{item}: {quantity}")
        else:
            categories["Other"].append(f"{item}: {quantity}")
    
    for category, items in categories.items():
        if items:
            embed.add_field(name=category, value="\n".join(items), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="equip", help="Equip an item from your inventory")
async def equip_item(ctx: commands.Context, *, item_name: str):
    player = get_player(ctx.author.id)
    
    if item_name not in player.inventory:
        await ctx.send(f"You don't have {item_name} in your inventory.")
        return
    
    if item_name not in ITEM_STATS:
        await ctx.send(f"{item_name} cannot be equipped.")
        return
    
    item_type = ITEM_STATS[item_name]["type"]
    player.equip_item(item_type, item_name)
    
    embed = discord.Embed(
        title="Equipment Updated",
        description=f"Equipped {item_name} as your {item_type}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    save_data()

@bot.command(name="rest", help="Rest to reset your daily battles and heal")
async def rest(ctx: commands.Context):
    player = get_player(ctx.author.id)
    player.reset_daily_battles()
    
    embed = discord.Embed(
        title="Resting at Camp",
        description="You are fully healed. Daily battles have been reset.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    save_data()

@bot.command(name="help", help="Show all available commands")
async def show_help(ctx: commands.Context):
    embed = discord.Embed(
        title="Battle Bot Help",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    
    commands_info = {
        "!battle": "Start your daily auto-battles (10 max with 24h cooldown)",
        "!profile": "View your character profile",
        "!inventory": "Check your inventory",
        "!equip [item]": "Equip an item from your inventory",
        "!rest": "Heal and reset daily battles (doesn't affect cooldown)",
        "!help": "Show this help message"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)

# Background tasks
@tasks.loop(minutes=5)
async def auto_save():
    save_data()
    print("Player data saved.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    auto_save.start()

# Run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN')
