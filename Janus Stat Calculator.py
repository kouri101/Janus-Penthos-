import discord
from discord.ext import commands
import asyncio

class JanusPenthosStatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}  # Stores user calculations
    
    @commands.group(name="stats", invoke_without_command=True)
    async def stats_group(self, ctx):
        """Janus Penthos Stat Calculator - Main command"""
        embed = discord.Embed(
            title="Janus Penthos Stat Calculator",
            description="Calculate your character stats for Janus Penthos",
            color=0x4f46e5
        )
        embed.add_field(
            name="Available Commands",
            value=(
                "`!stats new` - Start a new calculation\n"
                "`!stats calculate` - Calculate your stats\n"
                "`!stats show` - Show current values\n"
                "`!stats set <parameter> <value>` - Set a value\n"
                "`!stats help` - Show detailed help"
            ),
            inline=False
        )
        embed.set_footer(text="Version 0.0.1")
        await ctx.send(embed=embed)
    
    @stats_group.command(name="new")
    async def new_calculation(self, ctx):
        """Start a new calculation"""
        self.user_data[ctx.author.id] = {
            # Character Progression
            "character_level": 1,
            "vit_points": 0,
            "def_points": 0,
            "str_points": 0,
            "int_points": 0,
            "agi_points": 0,
            
            # Attack & Defense Stats
            "flat_weapon_atk": 0.0,
            "atk_percent": 0.0,
            "def_percent": 0.0,
            "hp_percent": 0.0,
            
            # Critical Stats
            "crit_rate_weapon": 0.0,
            "crit_rate_armor": 0.0,
            "crit_rate_substats": 0.0,
            "crit_damage_weapon": 0.0,
            "crit_damage_armor": 0.0,
            "crit_damage_substats": 0.0,
            
            # Special Bonuses
            "elemental_dmg_bonus": 0.0,
            "speed_boots": 0.0,
            "speed_substats": 0.0,
            "mp_gear": 0.0,
            "mp_substats": 0.0,
            
            # Results (will be calculated)
            "results": {}
        }
        
        await ctx.send(f"New calculation started for {ctx.author.mention}! Use `!stats set` to configure your values.")
    
    @stats_group.command(name="set")
    async def set_value(self, ctx, parameter: str, value: float):
        """Set a parameter value"""
        if ctx.author.id not in self.user_data:
            await ctx.send("Please start a new calculation with `!stats new` first.")
            return
        
        valid_params = [
            'character_level', 'vit_points', 'def_points', 'str_points', 'int_points', 'agi_points',
            'flat_weapon_atk', 'atk_percent', 'def_percent', 'hp_percent',
            'crit_rate_weapon', 'crit_rate_armor', 'crit_rate_substats',
            'crit_damage_weapon', 'crit_damage_armor', 'crit_damage_substats',
            'elemental_dmg_bonus', 'speed_boots', 'speed_substats', 'mp_gear', 'mp_substats'
        ]
        
        if parameter not in valid_params:
            await ctx.send(f"Invalid parameter. Valid parameters are: {', '.join(valid_params)}")
            return
        
        self.user_data[ctx.author.id][parameter] = value
        await ctx.send(f"Set `{parameter}` to `{value}` for {ctx.author.mention}")
    
    @stats_group.command(name="calculate")
    async def calculate_stats(self, ctx):
        """Calculate the stats"""
        if ctx.author.id not in self.user_data:
            await ctx.send("Please start a new calculation with `!stats new` first.")
            return
        
        data = self.user_data[ctx.author.id]
        results = {}
        
        try:
            # Validate inputs first
            level = max(1, min(data["character_level"], 100))
            data["character_level"] = level
            
            # Get status points (ensured to be 0-300)
            vit = max(0, min(data["vit_points"], 300))
            defense = max(0, min(data["def_points"], 300))
            strength = max(0, min(data["str_points"], 300))
            intelligence = max(0, min(data["int_points"], 300))
            agility = max(0, min(data["agi_points"], 300))
            
            # Update data with validated values
            data["vit_points"] = vit
            data["def_points"] = defense
            data["str_points"] = strength
            data["int_points"] = intelligence
            data["agi_points"] = agility
            
            # Calculate available and allocated SP
            sp_available = min(3 * level, 300)
            sp_allocated = vit + defense + strength + intelligence + agility
            
            if sp_allocated > sp_available:
                await ctx.send(
                    f"Error: Total allocated status points ({sp_allocated}) exceed available points ({sp_available})"
                )
                return
            
            results["sp_available"] = f"{sp_available} (Max: 300)"
            results["sp_allocated"] = f"{sp_allocated}"
            
            # Calculate base stats from level
            base_hp = 100 * level
            base_mp = 3 * level + 20
            base_atk = 3 * level + 5
            base_def = 3 * level + 5
            base_speed = 10
            
            results["base_hp"] = f"{base_hp:.1f}"
            results["base_mp"] = f"{base_mp:.1f}"
            results["base_atk"] = f"{base_atk:.1f}"
            results["base_def"] = f"{base_def:.1f}"
            results["base_speed"] = f"{base_speed:.1f}"
            
            # Calculate ascension boost
            ascension = 0
            if level >= 25: ascension += 1
            if level >= 50: ascension += 1
            if level >= 75: ascension += 1
            if level >= 100: ascension += 1
            
            ascension_percent = ascension * 0.10
            results["ascension_boost"] = f"{ascension_percent*100:.0f}%"
            
            # Apply ascension to stats (except speed)
            ascended_hp = base_hp * (1 + ascension_percent)
            ascended_mp = base_mp * (1 + ascension_percent)
            ascended_atk = base_atk * (1 + ascension_percent)
            ascended_def = base_def * (1 + ascension_percent)
            
            # Apply status point bonuses
            effective_hp = ascended_hp + (vit * 30)
            effective_mp = ascended_mp + (intelligence * 5)
            effective_atk = ascended_atk + (strength * 2) + (intelligence * 2)
            effective_def = ascended_def + (defense * 1)
            effective_speed = base_speed + (agility * 1)
            
            results["effective_hp"] = f"{effective_hp:.1f}"
            results["effective_mp"] = f"{effective_mp:.1f}"
            results["effective_atk"] = f"{effective_atk:.1f}"
            results["effective_def"] = f"{effective_def:.1f}"
            results["effective_speed"] = f"{effective_speed:.1f}"
            
            # Get equipment bonuses
            weapon_atk = max(0.0, data["flat_weapon_atk"])
            atk_percent = max(0.0, data["atk_percent"])
            def_percent = max(0.0, data["def_percent"])
            hp_percent = max(0.0, data["hp_percent"])
            
            # Calculate crit stats
            crit_rate = (
                max(0.0, data["crit_rate_weapon"]) +
                max(0.0, data["crit_rate_armor"]) +
                max(0.0, data["crit_rate_substats"])
            )
            
            crit_dmg = (
                max(0.0, data["crit_damage_weapon"]) +
                max(0.0, data["crit_damage_armor"]) +
                max(0.0, data["crit_damage_substats"])
            )
            
            results["final_crit_rate"] = f"{crit_rate:.1f}%"
            results["final_crit_dmg"] = f"{crit_dmg:.1f}%"
            
            # Calculate final ATK
            total_atk = (effective_atk + weapon_atk) * (1 + atk_percent)
            results["final_atk"] = f"{total_atk:.1f}"
            
            # Calculate average damage (including crit)
            avg_damage = total_atk * (1 + (crit_rate/100) * (crit_dmg/100))
            results["avg_damage"] = f"{avg_damage:.1f}"
            
            # Calculate final damage with elemental bonus
            elemental_bonus = max(0.0, data["elemental_dmg_bonus"])
            total_damage = avg_damage * (1 + elemental_bonus)
            results["total_damage"] = f"{total_damage:.1f}"
            
            # Calculate defensive stats
            results["final_def"] = f"{effective_def * (1 + def_percent):.1f}"
            results["final_hp"] = f"{effective_hp * (1 + hp_percent):.1f}"
            
            # Calculate speed and MP
            speed_bonus = max(0.0, data["speed_boots"]) + max(0.0, data["speed_substats"])
            results["final_speed"] = f"{effective_speed + speed_bonus:.1f}"
            
            mp_bonus = max(0.0, data["mp_gear"]) + max(0.0, data["mp_substats"])
            results["final_mp"] = f"{effective_mp + mp_bonus:.1f}"
            
            # Store results
            self.user_data[ctx.author.id]["results"] = results
            
            # Create result embed
            embed = discord.Embed(
                title=f"Stat Calculation Results for {ctx.author.display_name}",
                color=0x10b981
            )
            
            # Base Stats
            embed.add_field(
                name="Base Stats",
                value=(
                    f"**Level:** {level}\n"
                    f"**HP:** {results['base_hp']}\n"
                    f"**MP:** {results['base_mp']}\n"
                    f"**ATK:** {results['base_atk']}\n"
                    f"**DEF:** {results['base_def']}\n"
                    f"**Speed:** {results['base_speed']}\n"
                    f"**Ascension:** {results['ascension_boost']}"
                ),
                inline=False
            )
            
            # Status Points
            embed.add_field(
                name="Status Points",
                value=(
                    f"**Available:** {results['sp_available']}\n"
                    f"**Allocated:** {results['sp_allocated']}\n"
                    f"**VIT:** {vit} (+{vit*30} HP)\n"
                    f"**DEF:** {defense} (+{defense} DEF)\n"
                    f"**STR:** {strength} (+{strength*2} ATK)\n"
                    f"**INT:** {intelligence} (+{intelligence*5} MP, +{intelligence*2} ATK)\n"
                    f"**AGI:** {agility} (+{agility} Speed)"
                ),
                inline=False
            )
            
            # Final Stats
            embed.add_field(
                name="Final Stats",
                value=(
                    f"**Total HP:** {results['final_hp']}\n"
                    f"**Total MP:** {results['final_mp']}\n"
                    f"**Total ATK:** {results['final_atk']}\n"
                    f"**Total DEF:** {results['final_def']}\n"
                    f"**Total Speed:** {results['final_speed']}\n"
                    f"**Crit Rate:** {results['final_crit_rate']}\n"
                    f"**Crit Damage:** {results['final_crit_dmg']}\n"
                    f"**Avg. Damage:** {results['avg_damage']}\n"
                    f"**Total Damage:** {results['total_damage']}"
                ),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred during calculation: {str(e)}")
    
    @stats_group.command(name="show")
    async def show_values(self, ctx):
        """Show current values"""
        if ctx.author.id not in self.user_data:
            await ctx.send("Please start a new calculation with `!stats new` first.")
            return
        
        data = self.user_data[ctx.author.id]
        embed = discord.Embed(
            title=f"Current Values for {ctx.author.display_name}",
            color=0x4f46e5
        )
        
        # Character Progression
        embed.add_field(
            name="Character Progression",
            value=(
                f"**Level:** {data['character_level']}\n"
                f"**VIT:** {data['vit_points']}\n"
                f"**DEF:** {data['def_points']}\n"
                f"**STR:** {data['str_points']}\n"
                f"**INT:** {data['int_points']}\n"
                f"**AGI:** {data['agi_points']}"
            ),
            inline=False
        )
        
        # Attack Stats
        embed.add_field(
            name="Attack Stats",
            value=(
                f"**Weapon ATK:** {data['flat_weapon_atk']}\n"
                f"**ATK % Bonus:** {data['atk_percent']}%\n"
                f"**Crit Rate (Weapon):** {data['crit_rate_weapon']}%\n"
                f"**Crit Rate (Armor):** {data['crit_rate_armor']}%\n"
                f"**Crit Rate (Substats):** {data['crit_rate_substats']}%\n"
                f"**Crit DMG (Weapon):** {data['crit_damage_weapon']}%\n"
                f"**Crit DMG (Armor):** {data['crit_damage_armor']}%\n"
                f"**Crit DMG (Substats):** {data['crit_damage_substats']}%\n"
                f"**Elemental DMG %:** {data['elemental_dmg_bonus']}%"
            ),
            inline=False
        )
        
        # Defense Stats
        embed.add_field(
            name="Defense Stats",
            value=(
                f"**DEF % Bonus:** {data['def_percent']}%\n"
                f"**HP % Bonus:** {data['hp_percent']}%"
            ),
            inline=False
        )
        
        # Speed and MP
        embed.add_field(
            name="Speed & MP",
            value=(
                f"**Speed (Boots):** {data['speed_boots']}\n"
                f"**Speed (Substats):** {data['speed_substats']}\n"
                f"**MP (Gear):** {data['mp_gear']}\n"
                f"**MP (Substats):** {data['mp_substats']}"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @stats_group.command(name="help")
    async def show_help(self, ctx):
        """Show detailed help"""
        embed = discord.Embed(
            title="Janus Penthos Stat Calculator Help",
            description="Detailed information about the stat calculator",
            color=0x4f46e5
        )
        
        embed.add_field(
            name="Getting Started",
            value=(
                "1. Start a new calculation with `!stats new`\n"
                "2. Set your values with `!stats set <parameter> <value>`\n"
                "3. Calculate your stats with `!stats calculate`\n"
                "4. View your current values with `!stats show`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Available Parameters",
            value=(
                "**Character Progression:**\n"
                "`character_level` (1-100), `vit_points`, `def_points`, `str_points`, `int_points`, `agi_points`\n\n"
                "**Attack Stats:**\n"
                "`flat_weapon_atk`, `atk_percent`, `crit_rate_weapon`, `crit_rate_armor`, `crit_rate_substats`, "
                "`crit_damage_weapon`, `crit_damage_armor`, `crit_damage_substats`, `elemental_dmg_bonus`\n\n"
                "**Defense Stats:**\n"
                "`def_percent`, `hp_percent`\n\n"
                "**Speed & MP:**\n"
                "`speed_boots`, `speed_substats`, `mp_gear`, `mp_substats`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Example",
            value=(
                "```\n"
                "!stats new\n"
                "!stats set character_level 50\n"
                "!stats set vit_points 30\n"
                "!stats set str_points 50\n"
                "!stats set flat_weapon_atk 150\n"
                "!stats set atk_percent 0.25\n"
                "!stats calculate\n"
                "```"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(JanusPenthosStatBot(bot))