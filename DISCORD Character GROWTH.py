import json
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class Equipment:
    def __init__(self):
        self.weapon = {"name": "None", "attack": 0}
        self.armor = {"name": "None", "defense": 0}
        self.accessory = {"name": "None", "effect": "None"}
    
    def get_equipment_embed(self):
        embed = discord.Embed(title="Current Equipment", color=0x00ff00)
        embed.add_field(name="Weapon", value=f"{self.weapon['name']} (ATK +{self.weapon['attack']})", inline=False)
        embed.add_field(name="Armor", value=f"{self.armor['name']} (DEF +{self.armor['defense']})", inline=False)
        embed.add_field(name="Accessory", value=f"{self.accessory['name']} ({self.accessory['effect']})", inline=False)
        return embed
    
    async def edit_equipment(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        while True:
            embed = discord.Embed(title="Edit Equipment", color=0x00ff00)
            embed.add_field(name="1", value="Weapon", inline=False)
            embed.add_field(name="2", value="Armor", inline=False)
            embed.add_field(name="3", value="Accessory", inline=False)
            embed.add_field(name="4", value="Back to Menu", inline=False)
            
            await ctx.send(embed=embed)
            
            try:
                choice_msg = await bot.wait_for('message', timeout=30.0, check=check)
                choice = choice_msg.content.strip()
                
                if choice == "1":
                    await ctx.send("Enter weapon name:")
                    name_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    self.weapon["name"] = name_msg.content
                    
                    await ctx.send("Enter attack bonus:")
                    attack_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    try:
                        self.weapon["attack"] = int(attack_msg.content)
                    except ValueError:
                        await ctx.send("Please enter a valid number. Setting attack to 0.")
                        self.weapon["attack"] = 0
                
                elif choice == "2":
                    await ctx.send("Enter armor name:")
                    name_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    self.armor["name"] = name_msg.content
                    
                    await ctx.send("Enter defense bonus:")
                    defense_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    try:
                        self.armor["defense"] = int(defense_msg.content)
                    except ValueError:
                        await ctx.send("Please enter a valid number. Setting defense to 0.")
                        self.armor["defense"] = 0
                
                elif choice == "3":
                    await ctx.send("Enter accessory name:")
                    name_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    self.accessory["name"] = name_msg.content
                    
                    await ctx.send("Enter accessory effect:")
                    effect_msg = await bot.wait_for('message', timeout=30.0, check=check)
                    self.accessory["effect"] = effect_msg.content
                
                elif choice == "4":
                    break
                else:
                    await ctx.send("Invalid choice. Please select 1-4.")
            
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. Equipment editing cancelled.")
                break

class Character:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_limit = self.calculate_exp_limit()
        
        # Base stats
        self.base_hp = 100
        self.base_mp = 23
        self.base_atk = 8
        self.base_def = 8
        self.base_speed = 10
        
        # Status points
        self.vit = 0
        self.int = 0
        self.str = 0
        self.def_stat = 0
        self.agi = 0
        self.unallocated_points = 3  # Starting free points
        
        # Equipment
        self.equipment = Equipment()
        
        # Ascension tracking
        self.ascension_count = 0
        
    def calculate_exp_limit(self):
        if self.level <= 5:
            return self.level * 500
        elif self.level <= 10:
            return self.level * 600
        elif self.level <= 15:
            return self.level * 700
        elif self.level <= 20:
            return self.level * 800
        elif self.level <= 25:
            return self.level * 900
        elif self.level <= 30:
            return self.level * 1000
        elif self.level <= 35:
            return self.level * 1100
        elif self.level <= 40:
            return self.level * 1200
        elif self.level <= 45:
            return self.level * 1300
        elif self.level <= 50:
            return self.level * 1400
        elif self.level <= 55:
            return self.level * 1500
        elif self.level <= 60:
            return self.level * 1600
        elif self.level <= 65:
            return self.level * 1700
        elif self.level <= 70:
            return self.level * 1800
        elif self.level <= 75:
            return self.level * 1900
        elif self.level <= 80:
            return self.level * 2000
        elif self.level <= 85:
            return self.level * 2100
        elif self.level <= 90:
            return self.level * 2200
        elif self.level <= 95:
            return self.level * 2300
        else:
            return self.level * 2500
    
    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_limit:
            self.level_up()
    
    async def level_up(self, ctx):
        # Calculate excess EXP
        excess_exp = self.exp - self.exp_limit
        self.level += 1
        self.exp = excess_exp
        self.exp_limit = self.calculate_exp_limit()
        
        # Store old stats for display
        old_hp = self.base_hp
        old_mp = self.base_mp
        old_atk = self.base_atk
        old_def = self.base_def
        
        # Update base stats
        self.base_hp = 100 * self.level
        self.base_mp = 3 * self.level + 20
        self.base_atk = 3 * self.level + 5
        self.base_def = 3 * self.level + 5
        
        # Create level up embed
        embed = discord.Embed(
            title=f"Level Up!",
            description=f"Level {self.level-1} {self.name} levels up to level {self.level}!",
            color=0xffd700
        )
        
        embed.add_field(name="Increasing base stats", value="\u200b", inline=False)
        embed.add_field(name="HP", value=f"{100*(self.level-1)} → {self.base_hp}", inline=True)
        embed.add_field(name="MP", value=f"{3*(self.level-1)+20} → {self.base_mp}", inline=True)
        embed.add_field(name="ATK", value=f"{3*(self.level-1)+5} → {self.base_atk}", inline=True)
        embed.add_field(name="DEF", value=f"{3*(self.level-1)+5} → {self.base_def}", inline=True)
        
        await ctx.send(embed=embed)
        
        # Check for ascension
        if self.level in [25, 50, 75, 100]:
            await self.ascend(ctx)
        
        # Add 3 status points
        self.unallocated_points += 3
        
        # Create stats embed
        stats_embed = discord.Embed(
            title="Status Points Applied",
            color=0x00ff00
        )
        
        stats_embed.add_field(name="VIT", value=f"{self.vit}\t\tHP: {self.base_hp + (self.vit * 30)}", inline=False)
        stats_embed.add_field(name="INT", value=f"{self.int}\t\tMP: {round(self.base_mp + (self.int * 5), 1)}", inline=False)
        stats_embed.add_field(name="STR", value=f"{self.str}\t\tATK: {round(self.base_atk + (self.str * 2), 1)}", inline=False)
        stats_embed.add_field(name="DEF", value=f"{self.def_stat}\t\tDEF: {round(self.base_def + self.def_stat, 1)}", inline=False)
        stats_embed.add_field(name="AGI", value=f"{self.agi}\t\tSpeed: {self.base_speed + self.agi}", inline=False)
        
        stats_embed.add_field(
            name="Reward", 
            value=f"You have been rewarded with +3 status points from leveling up.\nTotal unallocated points: {self.unallocated_points}",
            inline=False
        )
        
        await ctx.send(embed=stats_embed)
    
    async def ascend(self, ctx):
        self.ascension_count += 1
        
        # Store old base stats
        old_hp = self.base_hp
        old_mp = self.base_mp
        old_atk = self.base_atk
        old_def = self.base_def
        
        # Apply 10% boost
        self.base_hp = int(self.base_hp * 1.1)
        self.base_mp = round(self.base_mp * 1.1, 1)
        self.base_atk = round(self.base_atk * 1.1, 1)
        self.base_def = round(self.base_def * 1.1, 1)
        
        # Create ascension embed
        embed = discord.Embed(
            title=f"**{self.name.upper()} IS ASCENDING!**",
            description=f"**{self.name} felt their power increasing...**\nYour base stats received +10% boost in all stats except speed through your ascension.",
            color=0xff00ff
        )
        
        embed.add_field(name="HP", value=f"{old_hp} → {self.base_hp}", inline=True)
        embed.add_field(name="MP", value=f"{old_mp} → {self.base_mp}", inline=True)
        embed.add_field(name="ATK", value=f"{old_atk} → {self.base_atk}", inline=True)
        embed.add_field(name="DEF", value=f"{old_def} → {self.base_def}", inline=True)
        
        await ctx.send(embed=embed)
    
    async def allocate_stats(self, ctx, vit=0, int_stat=0, str_stat=0, def_stat=0, agi=0):
        total_requested = vit + int_stat + str_stat + def_stat + agi
        if total_requested > self.unallocated_points:
            await ctx.send(f"Error: Not enough status points available (have {self.unallocated_points}, requested {total_requested})")
            return
        
        self.vit += vit
        self.int += int_stat
        self.str += str_stat
        self.def_stat += def_stat
        self.agi += agi
        self.unallocated_points -= total_requested
        
        # Create allocation embed
        embed = discord.Embed(
            title=f"{self.name}'s Stat Allocation",
            color=0x00ff00
        )
        
        if vit > 0: embed.add_field(name="VIT", value=f"+{vit}", inline=True)
        if int_stat > 0: embed.add_field(name="INT", value=f"+{int_stat}", inline=True)
        if str_stat > 0: embed.add_field(name="STR", value=f"+{str_stat}", inline=True)
        if def_stat > 0: embed.add_field(name="DEF", value=f"+{def_stat}", inline=True)
        if agi > 0: embed.add_field(name="AGI", value=f"+{agi}", inline=True)
        
        await ctx.send(embed=embed)
        
        # Create stats embed
        stats_embed = discord.Embed(
            title="New Stats",
            color=0x00ff00
        )
        
        stats_embed.add_field(name="VIT", value=f"{self.vit}\t\tHP: {self.total_hp()}", inline=False)
        stats_embed.add_field(name="INT", value=f"{self.int}\t\tMP: {self.total_mp()}", inline=False)
        stats_embed.add_field(name="STR", value=f"{self.str}\t\tATK: {self.total_atk()}", inline=False)
        stats_embed.add_field(name="DEF", value=f"{self.def_stat}\t\tDEF: {self.total_def()}", inline=False)
        stats_embed.add_field(name="AGI", value=f"{self.agi}\t\tSpeed: {self.total_speed()}", inline=False)
        
        stats_embed.add_field(
            name="Remaining Points", 
            value=f"Remaining unallocated points: {self.unallocated_points}",
            inline=False
        )
        
        stats_embed.set_footer(text=f"Level {self.level} {self.name} has now {self.exp}/{self.exp_limit} EXP")
        
        await ctx.send(embed=stats_embed)
    
    def total_hp(self):
        return self.base_hp + (self.vit * 30)
    
    def total_mp(self):
        return round(self.base_mp + (self.int * 5), 1)
    
    def total_atk(self):
        return round(self.base_atk + (self.str * 2) + self.equipment.weapon["attack"], 1)
    
    def total_def(self):
        return round(self.base_def + self.def_stat + self.equipment.armor["defense"], 1)
    
    def total_speed(self):
        return self.base_speed + self.agi
    
    async def show_stats(self, ctx):
        embed = discord.Embed(
            title=f"Character: {self.name}",
            description=f"Level: {self.level}\nEXP: {self.exp}/{self.exp_limit}\nAscensions: {self.ascension_count}\nUnallocated points: {self.unallocated_points}",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
        
        # Show equipment
        equipment_embed = self.equipment.get_equipment_embed()
        await ctx.send(embed=equipment_embed)
        
        # Base stats
        base_embed = discord.Embed(
            title="Base Stats (without equipment or bonuses)",
            color=0x00ff00
        )
        base_embed.add_field(name="HP", value=self.base_hp, inline=True)
        base_embed.add_field(name="MP", value=self.base_mp, inline=True)
        base_embed.add_field(name="ATK", value=self.base_atk, inline=True)
        base_embed.add_field(name="DEF", value=self.base_def, inline=True)
        base_embed.add_field(name="Speed", value=self.base_speed, inline=True)
        await ctx.send(embed=base_embed)
        
        # Modified stats
        mod_embed = discord.Embed(
            title="Modified Stats (with status points)",
            color=0x00ff00
        )
        mod_embed.add_field(name="HP", value=self.base_hp + (self.vit * 30), inline=True)
        mod_embed.add_field(name="MP", value=round(self.base_mp + (self.int * 5), 1), inline=True)
        mod_embed.add_field(name="ATK", value=round(self.base_atk + (self.str * 2), 1), inline=True)
        mod_embed.add_field(name="DEF", value=round(self.base_def + self.def_stat, 1), inline=True)
        mod_embed.add_field(name="Speed", value=self.base_speed + self.agi, inline=True)
        await ctx.send(embed=mod_embed)
        
        # Final stats
        final_embed = discord.Embed(
            title="Final Stats (with equipment)",
            color=0x00ff00
        )
        final_embed.add_field(name="HP", value=self.total_hp(), inline=True)
        final_embed.add_field(name="MP", value=self.total_mp(), inline=True)
        final_embed.add_field(
            name="ATK", 
            value=f"{self.total_atk()} (Base: {round(self.base_atk + (self.str * 2), 1)} + Weapon: {self.equipment.weapon['attack']})", 
            inline=False
        )
        final_embed.add_field(
            name="DEF", 
            value=f"{self.total_def()} (Base: {round(self.base_def + self.def_stat, 1)} + Armor: {self.equipment.armor['defense']})", 
            inline=False
        )
        final_embed.add_field(name="Speed", value=self.total_speed(), inline=True)
        await ctx.send(embed=final_embed)
        
        # Status points
        points_embed = discord.Embed(
            title="Status Points",
            color=0x00ff00
        )
        points_embed.add_field(name="VIT", value=self.vit, inline=True)
        points_embed.add_field(name="INT", value=self.int, inline=True)
        points_embed.add_field(name="STR", value=self.str, inline=True)
        points_embed.add_field(name="DEF", value=self.def_stat, inline=True)
        points_embed.add_field(name="AGI", value=self.agi, inline=True)
        await ctx.send(embed=points_embed)
    
    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "base_hp": self.base_hp,
            "base_mp": self.base_mp,
            "base_atk": self.base_atk,
            "base_def": self.base_def,
            "base_speed": self.base_speed,
            "vit": self.vit,
            "int": self.int,
            "str": self.str,
            "def_stat": self.def_stat,
            "agi": self.agi,
            "unallocated_points": self.unallocated_points,
            "ascension_count": self.ascension_count,
            "equipment": {
                "weapon": self.equipment.weapon,
                "armor": self.equipment.armor,
                "accessory": self.equipment.accessory
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        char = cls(data["name"])
        char.level = data["level"]
        char.exp = data["exp"]
        char.base_hp = data["base_hp"]
        char.base_mp = data["base_mp"]
        char.base_atk = data["base_atk"]
        char.base_def = data["base_def"]
        char.base_speed = data["base_speed"]
        char.vit = data["vit"]
        char.int = data["int"]
        char.str = data["str"]
        char.def_stat = data["def_stat"]
        char.agi = data["agi"]
        char.unallocated_points = data["unallocated_points"]
        char.ascension_count = data["ascension_count"]
        char.equipment.weapon = data["equipment"]["weapon"]
        char.equipment.armor = data["equipment"]["armor"]
        char.equipment.accessory = data["equipment"]["accessory"]
        char.exp_limit = char.calculate_exp_limit()
        return char

# Global character storage
characters = {}

def save_character(user_id, character):
    filename = f"characters/{user_id}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(character.to_dict(), f, indent=2)
    return filename

def load_character(user_id):
    filename = f"characters/{user_id}.json"
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        data = json.load(f)
    character = Character.from_dict(data)
    return character

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='create')
async def create_character(ctx):
    """Create a new character"""
    user_id = str(ctx.author.id)
    
    if user_id in characters:
        await ctx.send("You already have a character. Use `!load` to access it.")
        return
    
    await ctx.send("Enter your character's name:")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        name_msg = await bot.wait_for('message', timeout=30.0, check=check)
        name = name_msg.content
        
        character = Character(name)
        characters[user_id] = character
        
        embed = discord.Embed(
            title="New Character Created",
            description=f"{name} (Level 1)\nYou have 3 free stat points to allocate!",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
        await character.show_stats(ctx)
        
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Character creation cancelled.")

@bot.command(name='addexp')
async def add_exp(ctx, amount: int):
    """Add EXP to your character"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character yet. Use `!create` to make one.")
        return
    
    character = characters[user_id]
    character.add_exp(amount)
    
    # Check if level up occurred (exp was spent)
    if character.exp < amount:
        # The level_up method will handle its own messaging
        pass
    else:
        await ctx.send(f"Added {amount} EXP to {character.name}. Current EXP: {character.exp}/{character.exp_limit}")

@bot.command(name='allocate')
async def allocate_stats(ctx):
    """Allocate your status points"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character yet. Use `!create` to make one.")
        return
    
    character = characters[user_id]
    
    if character.unallocated_points <= 0:
        await ctx.send("No status points available to allocate (you may need to level up first).")
        return
    
    await ctx.send(f"You have {character.unallocated_points} status points to allocate!")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        await ctx.send("How many points in VIT? (0 if none)")
        vit_msg = await bot.wait_for('message', timeout=30.0, check=check)
        vit = int(vit_msg.content) if vit_msg.content.isdigit() else 0
        
        await ctx.send("How many points in INT? (0 if none)")
        int_msg = await bot.wait_for('message', timeout=30.0, check=check)
        int_stat = int(int_msg.content) if int_msg.content.isdigit() else 0
        
        await ctx.send("How many points in STR? (0 if none)")
        str_msg = await bot.wait_for('message', timeout=30.0, check=check)
        str_stat = int(str_msg.content) if str_msg.content.isdigit() else 0
        
        await ctx.send("How many points in DEF? (0 if none)")
        def_msg = await bot.wait_for('message', timeout=30.0, check=check)
        def_stat = int(def_msg.content) if def_msg.content.isdigit() else 0
        
        await ctx.send("How many points in AGI? (0 if none)")
        agi_msg = await bot.wait_for('message', timeout=30.0, check=check)
        agi = int(agi_msg.content) if agi_msg.content.isdigit() else 0
        
        await character.allocate_stats(ctx, vit, int_stat, str_stat, def_stat, agi)
        
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Stat allocation cancelled.")
    except ValueError as e:
        await ctx.send(f"Error: {e}")

@bot.command(name='equip')
async def edit_equipment(ctx):
    """Edit your character's equipment"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character yet. Use `!create` to make one.")
        return
    
    character = characters[user_id]
    await character.equipment.edit_equipment(ctx)

@bot.command(name='stats')
async def show_stats(ctx):
    """Show your character's stats"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character yet. Use `!create` to make one.")
        return
    
    character = characters[user_id]
    await character.show_stats(ctx)

@bot.command(name='save')
async def save_character_cmd(ctx):
    """Save your character"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character yet. Use `!create` to make one.")
        return
    
    character = characters[user_id]
    filename = save_character(user_id, character)
    await ctx.send(f"Character saved to {filename}")

@bot.command(name='load')
async def load_character_cmd(ctx):
    """Load your character"""
    user_id = str(ctx.author.id)
    
    character = load_character(user_id)
    if not character:
        await ctx.send("No character found. Use `!create` to make a new one.")
        return
    
    characters[user_id] = character
    await ctx.send(f"Character {character.name} loaded successfully!")
    await character.show_stats(ctx)

@bot.command(name='delete')
async def delete_character(ctx):
    """Delete your character"""
    user_id = str(ctx.author.id)
    
    if user_id not in characters:
        await ctx.send("You don't have a character to delete.")
        return
    
    # Confirm deletion
    await ctx.send("Are you sure you want to delete your character? This cannot be undone. Type 'YES' to confirm.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() == 'YES'
    
    try:
        await bot.wait_for('message', timeout=30.0, check=check)
        
        # Delete from memory and file
        filename = f"characters/{user_id}.json"
        if os.path.exists(filename):
            os.remove(filename)
        del characters[user_id]
        await ctx.send("Character deleted successfully.")
        
    except asyncio.TimeoutError:
        await ctx.send("Character deletion cancelled.")

bot.run('YOUR_DISCORD_BOT_TOKEN')