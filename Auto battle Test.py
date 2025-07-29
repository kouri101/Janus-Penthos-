Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import discord
from discord.ext import commands, tasks
import random
import json
import os
from datetime import datetime, timedelta

# --- Insert your MONSTERS, MONSTER_ABILITIES, Monster and Player classes here ---
# (Use your existing classes but adapt to manage state per Discord user)

# Below is partial example of how to adapt Player and AutoBattleSystem for Discord

class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.gold = 0
        self.battles_today = 0
        self.total_battles = 0
        self.last_battle_date = None
        self.stats = {"STR": 10, "VIT": 10, "DEX": 10, "DEF": 10}
        self.kills = 0
        self.total_damage = 0
        self.max_hp = 50 + (self.stats["VIT"] * 5)
        self.hp = self.max_hp
        self.attack = 5 + (self.stats["STR"] * 2)
        self.defense = self.stats["DEF"]
        self.dodge_chance = self.stats["DEX"] * 0.005
        self.load()

    def save_path(self):
        return f"player_{self.user_id}.json"

    def save(self):
        data = {
            "level": self.level,
            "exp": self.exp,
            "exp_to_level": self.exp_to_level,
            "gold": self.gold,
            "stats": self.stats,
            "kills": self.kills,
            "total_damage": self.total_damage,
            "battles_today": self.battles_today,
            "total_battles": self.total_battles,
            "last_battle_date": self.last_battle_date.strftime("%Y-%m-%d") if self.last_battle_date else None,
            "hp": self.hp
        }
        with open(self.save_path(), "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.save_path()):
            try:
                with open(self.save_path(), "r") as f:
                    data = json.load(f)
                self.level = data.get("level", 1)
                self.exp = data.get("exp", 0)
                self.exp_to_level = data.get("exp_to_level", 100)
                self.gold = data.get("gold", 0)
                self.stats = data.get("stats", {"STR": 10, "VIT": 10, "DEX": 10, "DEF": 10})
                self.kills = data.get("kills", 0)
                self.total_damage = data.get("total_damage", 0)
                self.battles_today = data.get("battles_today", 0)
                self.total_battles = data.get("total_battles", 0)
                last_date = data.get("last_battle_date", None)
                if last_date:
                    self.last_battle_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                self.hp = data.get("hp", 50 + (self.stats["VIT"] * 5))
                self.max_hp = 50 + (self.stats["VIT"] * 5)
                self.attack = 5 + (self.stats["STR"] * 2)
                self.defense = self.stats["DEF"]
                self.dodge_chance = self.stats["DEX"] * 0.005
            except Exception as e:
                print(f"Error loading player data for user {self.user_id}: {e}")

    def can_battle_today(self):
        today = datetime.now().date()
        if self.last_battle_date != today:
            self.battles_today = 0
            self.last_battle_date = today
            return True
        return self.battles_today < 10

    def remaining_battles_today(self):
        today = datetime.now().date()
        if self.last_battle_date != today:
            return 10
        return max(0, 10 - self.battles_today)

    def time_until_reset(self):
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        reset_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0)
        return reset_time - now

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.2)
        self.stats["STR"] += 1
        self.stats["VIT"] += 1
        self.stats["DEX"] += 1
        self.stats["DEF"] += 1
        self.max_hp = 50 + (self.stats["VIT"] * 5)
        self.hp = self.max_hp
        self.attack = 5 + (self.stats["STR"] * 2)
        self.defense = self.stats["DEF"]
        self.dodge_chance = self.stats["DEX"] * 0.005

    def attack_monster(self, monster):
        damage = max(1, self.attack - (monster.defense // 2))
        damage = int(damage * random.uniform(0.9, 1.1))
        monster.hp -= damage
        self.total_damage += damage
        return damage

    def take_damage(self, damage):
        actual_damage = max(1, damage - (self.defense // 2))
        if random.random() < self.dodge_chance:
            return 0  # Dodged
        self.hp -= actual_damage
        return actual_damage


class AutoBattleSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.battle_locks = {}  # Lock battle per user

    def get_random_monster(self, player):
        valid_monsters = []
        for name, data in MONSTERS.items():
            if (data["min_level"] <= player.level <= data["max_level"]) or \
               (abs(player.level - data["min_level"]) <= 2) or \
               (abs(player.level - data["max_level"]) <= 2):
                valid_monsters.append(name)
        if not valid_monsters:
            valid_monsters = list(MONSTERS.keys())
        current_tier_monsters = [
            name for name, data in MONSTERS.items()
            if data["min_level"] <= player.level <= data["max_level"]
        ]
        if current_tier_monsters and random.random() < 0.7:
            name = random.choice(current_tier_monsters)
        else:
            name = random.choice(valid_monsters)
        monster_level = player.level + random.randint(-2, 2)
        monster_level = max(1, min(99, monster_level))
        return Monster(name, monster_level)

    async def simulate_battle(self, ctx, player):
        if not player.can_battle_today():
            remaining = player.time_until_reset()
            await ctx.send(f"Daily battle limit reached! Next reset in: {str(remaining).split('.')[0]}")
            return

        monster = self.get_random_monster(player)
        player.battles_today += 1
        player.total_battles += 1

        await ctx.send(f"⚔️ You encounter a level {monster.level} **{monster.name}**!")
        await ctx.send(f"Your HP: {player.hp}/{player.max_hp}")

        turn = 1
        while True:
            await ctx.send(f"**Turn {turn}:**")

            damage = player.attack_monster(monster)
            await ctx.send(f"You hit the {monster.name} for {damage} damage!")
            if monster.hp <= 0:
                await ctx.send(f"🎉 You defeated the {monster.name}!")
...                 exp_gained = monster.exp
...                 gold_gained = monster.gold
...                 if player.total_battles % 10 == 0:
...                     bonus_exp = player.level * 20
...                     exp_gained += bonus_exp
...                     await ctx.send(f"★ Bonus EXP for completing 10 battles: +{bonus_exp} EXP!")
...                 player.exp += exp_gained
...                 player.gold += gold_gained
...                 player.kills += 1
...                 await ctx.send(f"Gained {exp_gained} EXP and {gold_gained} gold!")
...                 if player.exp >= player.exp_to_level:
...                     player.level_up()
...                     await ctx.send(f"\n**LEVEL UP! You are now level {player.level}!**")
...                     await ctx.send(f"HP: {player.max_hp}, ATK: {player.attack}, DEF: {player.defense}")
...                 player.save()
...                 player.hp = player.max_hp  # Heal after battle
...                 break
... 
...             ability = monster.use_ability()
...             if ability:
...                 await ctx.send(f"{monster.name} uses {ability['name']}!")
...                 if "damage_mult" in ability:
...                     damage = int(monster.attack * ability["damage_mult"])
...                 else:
...                     damage = monster.attack
...             else:
...                 damage = monster.attack
... 
...             damage_taken = player.take_damage(damage)
...             if damage_taken == 0:
...                 await ctx.send(f"You dodged the {monster.name}'s attack!")
...             else:
...                 await ctx.send(f"{monster.name} hits you for {damage_taken} damage!")
...                 if player.hp <= 0:
...                     await ctx.send("💀 You were defeated! Reviving with 1 HP...")
                    player.hp = 1
                    player.save()
                    break
            turn += 1

    @commands.command(name="battle")
    async def battle(self, ctx):
        user_id = ctx.author.id
        if user_id in self.battle_locks:
            await ctx.send("You're already in a battle!")
            return

        self.battle_locks[user_id] = True
        player = Player(user_id)
        try:
            await self.simulate_battle(ctx, player)
        finally:
            self.battle_locks.pop(user_id, None)

    @commands.command(name="stats")
    async def stats(self, ctx):
        player = Player(ctx.author.id)
        embed = discord.Embed(title=f"{ctx.author.name}'s Stats")
        embed.add_field(name="Level", value=player.level)
        embed.add_field(name="EXP", value=f"{player.exp}/{player.exp_to_level}")
        embed.add_field(name="Gold", value=player.gold)
        embed.add_field(name="HP", value=f"{player.hp}/{player.max_hp}")
        embed.add_field(name="Kills", value=player.kills)
        embed.add_field(name="Total Battles", value=player.total_battles)
        embed.add_field(name="Battles Left Today", value=player.remaining_battles_today())
        await ctx.send(embed=embed)

# --- Setup the bot ---

intents = discord.Intents.default()
intents.message_content = True  # Required for message content in commands

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.add_cog(AutoBattleSystem(bot))

# Run your bot with your token
bot.run("YOUR_DISCORD_BOT_TOKEN")
