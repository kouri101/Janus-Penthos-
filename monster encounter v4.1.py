import discord
from discord.ext import commands
import random
import json
import os
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Any

# ---------------------------
# Enums and Base Classes (keep these the same)
# ---------------------------
class Element(Enum):
    NONE = auto()
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    WIND = auto()
    LIGHT = auto()
    DARK = auto()
    ICE = auto()
    LIGHTNING = auto()
    POISON = auto()

class StatusEffect:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration
    
    def apply_effect(self, target: Any) -> None:
        pass
    
    def update(self, target: Any) -> None:
        self.duration -= 1
        if self.duration <= 0:
            target.remove_status(self)

class BurnStatus(StatusEffect):
    def __init__(self, damage: int):
        super().__init__("Burn", 3)
        self.damage = damage
    
    def apply_effect(self, target: Any) -> None:
        target.current_hp -= self.damage
        return f"{target.name} takes {self.damage} burn damage!"

class WetStatus(StatusEffect):
    def __init__(self):
        super().__init__("Wet", 3)

class FrozenStatus(StatusEffect):
    def __init__(self):
        super().__init__("Frozen", 2)
    
    def apply_effect(self, target: Any) -> None:
        return f"{target.name} is frozen and can't move!"

class BleedStatus(StatusEffect):
    def __init__(self, damage: int):
        super().__init__("Bleed", -1)
        self.damage = damage
    
    def apply_effect(self, target: Any) -> None:
        target.current_hp -= self.damage
        return f"{target.name} bleeds for {self.damage} damage!"

class PoisonStatus(StatusEffect):
    def __init__(self, damage: int):
        super().__init__("Poisoned", 10)
        self.damage = damage
        
    def apply_effect(self, target: Any) -> None:
        target.current_hp -= self.damage
        return f"{target.name} takes {self.damage} poison damage!"

# ---------------------------
# Game Components (keep these mostly the same, just modify print statements to return strings)
# ---------------------------
class Inventory:
    def __init__(self):
        self.items: Dict[str, int] = {}
        self.capacity = 10
    
    def add_item(self, item_name: str, quantity: int = 1) -> Tuple[bool, str]:
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            if len(self.items) >= self.capacity:
                return False, "Inventory is full!"
            self.items[item_name] = quantity
        return True, f"Added {quantity} {item_name} to inventory."
    
    def show_inventory(self) -> str:
        if not self.items:
            return "Inventory is empty."
        else:
            inventory_str = "\nInventory:"
            for item, quantity in self.items.items():
                inventory_str += f"\n- {item}: {quantity}"
            inventory_str += f"\nCapacity: {len(self.items)}/{self.capacity}"
            return inventory_str

class Skill:
    def __init__(self, name: str, power_multiplier: float, element: Element = Element.NONE, 
                 healing: bool = False, mp_cost: int = 0, description: str = "", 
                 aoe: bool = False):
        self.name = name
        self.power_multiplier = power_multiplier
        self.element = element
        self.healing = healing
        self.mp_cost = mp_cost
        self.description = description
        self.aoe = aoe

class Equipment:
    def __init__(self):
        self.weapon = {"name": "Rusty Sword", "attack": 5}
        self.armor = {"name": "Leather Armor", "defense": 3}
        self.accessory = {"name": "None", "effect": "None"}
    
    def show_equipment(self) -> str:
        equipment_str = "\nCurrent Equipment:"
        equipment_str += f"\nWeapon: {self.weapon['name']} (ATK +{self.weapon['attack']})"
        equipment_str += f"\nArmor: {self.armor['name']} (DEF +{self.armor['defense']})"
        equipment_str += f"\nAccessory: {self.accessory['name']} ({self.accessory['effect']})"
        return equipment_str

# ---------------------------
# Character Class (modified for Discord)
# ---------------------------
class Character:
    def __init__(self, name: str, user_id: int):
        self.name = name
        self.user_id = user_id  # Discord user ID
        self.level = 1
        self.exp = 0
        self.ascension_count = 0
        self.base_vit = 0
        self.base_int = 0
        self.base_str = 0
        self.base_def = 0
        self.base_agi = 0
        self.skill_points = 3
        
        self.update_base_stats()
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        
        self.equipment = Equipment()
        self.inventory = Inventory()
        self.status_effects: List[StatusEffect] = []
        self.skills = [
            Skill("Power Slap", 1.5, mp_cost=2, description="Basic attack"),
            Skill("Fireball", 1.8, Element.FIRE, mp_cost=10, description="Fire damage"),
            Skill("Heal", 0.5, healing=True, mp_cost=15, description="Restores HP"),
            Skill("Ice Shard", 1.6, Element.ICE, mp_cost=8, description="Ice damage"),
            Skill("Water Blast", 1.7, Element.WATER, mp_cost=9, description="Water damage")
        ]
        self.in_combat = False
        self.current_combat = None

    # ... (keep all the existing methods, but modify print statements to return strings)
    
    def add_status(self, status: StatusEffect) -> str:
        self.status_effects.append(status)
        effect_msg = status.apply_effect(self)
        return effect_msg if effect_msg else f"{self.name} is now {status.name.lower()}!"
    
    def remove_status(self, status: StatusEffect) -> str:
        if status in self.status_effects:
            self.status_effects.remove(status)
            return f"{self.name} is no longer {status.name.lower()}!"
        return ""
    
    def update_statuses(self) -> List[str]:
        messages = []
        for status in self.status_effects[:]:
            status.update(self)
            if status.duration <= 0:
                msg = self.remove_status(status)
                if msg:
                    messages.append(msg)
        return messages
    
    def show_stats(self) -> str:
        stats_str = "\nCharacter Stats:"
        stats_str += f"\nName: {self.name}"
        stats_str += f"\nLevel: {self.level}"
        stats_str += f"\nEXP: {self.exp}/{self.get_exp_required()}"
        stats_str += f"\nHP: {self.current_hp}/{self.max_hp}"
        stats_str += f"\nMP: {self.current_mp}/{self.max_mp}"
        stats_str += f"\nATK: {self.total_atk} (Base: {self.total_base_atk} + Weapon: {self.equipment.weapon['attack']})"
        stats_str += f"\nDEF: {self.total_def} (Base: {self.total_base_defense} + Armor: {self.equipment.armor['defense']})"
        stats_str += f"\nSpeed: {self.total_speed}"
        stats_str += f"\nUnused Skill Points: {self.skill_points}"
        
        if self.status_effects:
            stats_str += "\nStatus Effects:"
            for status in self.status_effects:
                stats_str += f"\n- {status.name} ({status.duration} turns)"
        
        stats_str += self.equipment.show_equipment()
        return stats_str
    
    def show_skills(self) -> str:
        skills_str = "\nAvailable Skills:"
        for i, skill in enumerate(self.skills, 1):
            mp_cost = f" (MP: {skill.mp_cost})" if skill.mp_cost > 0 else ""
            skills_str += f"\n{i}. {skill.name}{mp_cost}: {skill.description}"
        return skills_str

# ---------------------------
# Monster Class (modified for Discord)
# ---------------------------
class Monster:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.set_stats()
        self.exp_reward = self.calculate_exp_reward()
        self.status_effects: List[StatusEffect] = []
        
    def set_stats(self):
        """Set monster stats based on type and level"""
        if "Slime" in self.name:
            self.max_hp = 50 + (self.level * 20)
            self.atk = 5 + (self.level * 2)
            self.defense = 3 + self.level
            self.speed = 5 + self.level
            self.element = Element.NONE
        elif "Jelly" in self.name:
            self.max_hp = 70 + (self.level * 25)
            self.atk = 8 + (self.level * 3)
            self.defense = 5 + self.level
            self.speed = 7 + self.level
            self.element = Element.NONE
        elif "Goblin" in self.name:
            self.max_hp = 100 + (self.level * 30)
            self.atk = 15 + (self.level * 4)
            self.defense = 8 + self.level
            self.speed = 10 + self.level
            self.element = Element.NONE
            
        self.current_hp = self.max_hp
    
    def calculate_exp_reward(self) -> int:
        """Calculate EXP based on monster type and level"""
        if "Slime" in self.name:
            if self.level == 1: return 10
            if self.level == 2: return 20
            if self.level == 3: return 25
        elif "Acid Slime" in self.name or "Poison Slime" in self.name:
            if self.level == 2: return 15
            if self.level == 3: return 25
        elif "Pyro Slime" in self.name or "Cryo Slime" in self.name or "Hydro Slime" in self.name or "Geo Slime" in self.name or "Dendro Slime" in self.name:
            if self.level == 2: return 15
            if self.level == 3: return 25
        elif "Jelly" in self.name and not any(x in self.name for x in ["Lava", "Sea", "Forest", "Desert", "Swamp", "Iron", "Silver", "Golden", "Diamond", "Lapis", "Emerald"]):
            if self.level == 2: return 15
            if self.level == 3: return 25
        elif "Lava Jelly" in self.name or "Sea Jelly" in self.name or "Forest Jelly" in self.name or "Desert Jelly" in self.name or "Swamp Jelly" in self.name:
            if self.level == 3: return 20
            if self.level == 4: return 30
        elif "Iron Jelly" in self.name or "Silver Jelly" in self.name or "Golden Jelly" in self.name or "Diamond Jelly" in self.name or "Lapis Jelly" in self.name or "Emerald Jelly" in self.name:
            if self.level == 4: return 30
            if self.level == 5: return 40
        elif "Goblin" in self.name:
            if self.level == 3: return 20
            if self.level == 4: return 25
            if self.level == 5: return 30
            if self.level == 6: return 35
            if self.level == 7: return 40
            if self.level == 8: return 45
            if self.level == 9: return 50
    
    def roll_for_loot(self) -> Dict[str, int]:
        """Roll for loot based on monster type and level"""
        drops = {}
        
        # All slimes drop monster essence
        if "Slime" in self.name:
            # Monster essence drops
            if random.random() <= 0.5:
                if self.level in [1, 2]:
                    drops["Monster Essence"] = random.randint(1, 6)
                else:
                    drops["Monster Essence"] = random.randint(1, 10)
            
            # Type-specific drops
            if random.random() <= 0.5:
                if self.name == "Slime":
                    if self.level == 1:
                        drops["Slime Essence"] = random.randint(1, 3)
                    else:
                        drops["Slime Essence"] = random.randint(1, 6)
                elif self.name == "Acid Slime":
                    drops["Acidic Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Poison Slime":
                    drops["Toxic Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Pyro Slime":
                    drops["Pyro Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Cryo Slime":
                    drops["Cryo Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Hydro Slime":
                    drops["Hydro Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Geo Slime":
                    drops["Geo Slime Essence"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Dendro Slime":
                    drops["Dendro Seed"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
        
        # Jelly drops
        elif "Jelly" in self.name:
            # Monster essence drops
            if random.random() <= 0.5:
                if self.level in [2, 3]:
                    drops["Monster Essence"] = random.randint(1, 6)
                else:
                    drops["Monster Essence"] = random.randint(1, 10)
            
            # Type-specific drops
            if random.random() <= 0.5:
                if self.name == "Jelly":
                    drops["Pale Gelatin"] = random.randint(1, 3) if self.level == 2 else random.randint(1, 6)
                elif self.name == "Lava Jelly":
                    drops["Red Gelatin"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                elif self.name == "Sea Jelly":
                    drops["Blue Gelatin"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                elif self.name == "Forest Jelly":
                    drops["Green Gelatin"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                elif self.name == "Desert Jelly":
                    drops["Orange Gelatin"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                elif self.name == "Swamp Jelly":
                    drops["Purple Gelatin"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                elif self.name == "Iron Jelly":
                    drops["Iron Jelly's Fluid"] = random.randint(1, 3) if self.level == 4 else random.randint(1, 6)
                elif self.name == "Silver Jelly":
                    drops["Silver Jelly's Fluid"] = random.randint(1, 3) if self.level == 4 else random.randint(1, 6)
                elif self.name == "Golden Jelly":
                    drops["Golden Jelly's Fluid"] = random.randint(1, 3) if self.level == 4 else random.randint(1, 6)
                elif self.name == "Diamond Jelly":
                    drops["Diamond Jelly's Fluid"] = 1 if self.level == 4 else random.randint(1, 2)
                elif self.name == "Lapis Jelly":
                    drops["Lapis Jelly's Fluid"] = 1 if self.level == 4 else random.randint(1, 2)
                elif self.name == "Emerald Jelly":
                    drops["Emerald Jelly's Fluid"] = 1 if self.level == 4 else random.randint(1, 2)
        
        # Goblin drops
        elif "Goblin" in self.name:
            # Common drops
            if "Tank" in self.name or "Warrior" in self.name or "Archer" in self.name or "Thief" in self.name:
                if random.random() <= 0.3:
                    drops["Goblin Bones"] = random.randint(1, 6)
                if random.random() <= 0.3:
                    drops["Monster Essence"] = random.randint(1, 10)
                if random.random() <= 0.25:
                    drops["Goblin Armor"] = 1
                
                # Specialized drops
                if "Tank" in self.name:
                    if random.random() <= 0.06:
                        drops["Goblin Shield"] = 1
                    if random.random() <= 0.06:
                        drops["Goblin Mace"] = 1
                elif "Warrior" in self.name:
                    if random.random() <= 0.06:
                        drops["Goblin Sword"] = 1
                    if random.random() <= 0.06:
                        drops["Goblin Spear"] = 1
                elif "Archer" in self.name:
                    if random.random() <= 0.06:
                        drops["Goblin Bow"] = 1
                    if random.random() <= 0.06:
                        drops["Goblin Arrow"] = 1
                elif "Thief" in self.name:
                    if random.random() <= 0.06:
                        drops["Goblin Knife"] = 1
                    if random.random() <= 0.06:
                        drops["Goblin Coin Pouch"] = 1
            else:
                # Regular goblins
                if random.random() <= 0.49:
                    drops["Goblin Bones"] = random.randint(1, 3) if self.level == 3 else random.randint(1, 6)
                if random.random() <= 0.49:
                    drops["Monster Essence"] = random.randint(1, 6) if self.level == 3 else random.randint(1, 10)
            
            # Rare drop (Bold Gaze)
            if random.random() <= 0.02 if self.level in [3,4] else 0.03 if self.level in [5,6,7] else 0.04:
                drops["Bold Gaze"] = 1
        
        return drops

# ---------------------------
# Game Systems (modified for Discord)
# ---------------------------
def create_monster(name: str, level: int) -> Monster:
    # ... (keep this function the same, it already returns a Monster instance)

class Combat:
    def __init__(self, character: Character, monster: Monster):
        self.character = character
        self.monster = monster
        self.additional_monsters: List[Monster] = []
        self.messages: List[str] = []
    
    def add_message(self, message: str) -> None:
        self.messages.append(message)
    
    def get_messages(self) -> str:
        return "\n".join(self.messages)
    
    def clear_messages(self) -> None:
        self.messages = []
    
    def use_skill(self, skill_index: int) -> Tuple[bool, str]:
        """Returns (combat_ended, message)"""
        if 0 <= skill_index < len(self.character.skills):
            skill = self.character.skills[skill_index]
            
            if self.character.current_mp < skill.mp_cost:
                return False, f"Not enough MP! Need {skill.mp_cost}, have {self.character.current_mp}"
            
            self.character.current_mp -= skill.mp_cost
            self.add_message(f"{self.character.name} uses {skill.name}!")
            
            if skill.healing:
                heal_amount = max(1, round(self.character.max_hp * skill.power_multiplier))
                self.character.current_hp = min(self.character.max_hp, 
                                              self.character.current_hp + heal_amount)
                return False, f"{self.character.name} heals for {heal_amount} HP!"
            else:
                base_damage = max(1, (self.character.total_atk * skill.power_multiplier) - 
                              (self.monster.defense * 0.5))
                damage = round(base_damage * random.uniform(0.9, 1.1))
                
                # Elemental reactions
                if (skill.element in [Element.ICE, Element.LIGHTNING] and 
                    any(isinstance(s, WetStatus) for s in self.monster.status_effects)):
                    damage = round(damage * 1.5)
                    self.add_message("Elemental reaction! Extra damage!")
                
                if skill.element == Element.FIRE:
                    for status in self.monster.status_effects[:]:
                        if isinstance(status, FrozenStatus):
                            self.monster.remove_status(status)
                            self.add_message(f"The heat melts {self.monster.name}'s frozen status!")
                
                self.monster.current_hp -= damage
                self.add_message(f"{skill.name} hits for {damage} damage!")
                
                if self.monster.current_hp <= 0:
                    self.handle_victory()
                    return True, self.get_messages()
                
                return False, self.get_messages()
        else:
            return False, f"Invalid skill index. Please select 1-{len(self.character.skills)}."

    def start_combat(self) -> str:
        self.add_message(f"Battle between {self.character.name} and {self.monster.name}!")
        self.add_message(self.monster.show_stats())
        return self.get_messages()
    
    def do_player_turn(self, action: str, skill_index: Optional[int] = None) -> Tuple[bool, str]:
        """Returns (combat_ended, message)"""
        self.clear_messages()
        
        if action == "attack":
            base_damage = max(1, self.character.total_atk - (self.monster.defense * 0.7))
            damage = round(base_damage * random.uniform(0.9, 1.1))
            self.monster.current_hp -= damage
            self.add_message(f"{self.character.name} attacks for {damage} damage!")
            
            if self.monster.current_hp <= 0:
                self.handle_victory()
                return True, self.get_messages()
            
            return False, self.get_messages()
        
        elif action == "skill" and skill_index is not None:
            return self.use_skill(skill_index)
        
        elif action == "flee":
            if random.random() < 0.5:
                self.add_message(f"{self.character.name} successfully fled from battle!")
                return True, self.get_messages()
            self.add_message(f"{self.character.name} failed to flee!")
            return False, self.get_messages()
        
        else:
            return False, "Invalid action."
    
    def do_monster_turn(self) -> Tuple[bool, str]:
        """Returns (combat_ended, message)"""
        self.clear_messages()
        combatants = [self.monster] + self.additional_monsters
        
        for monster in combatants[:]:
            if monster.current_hp <= 0:
                continue
            
            # Check if monster is frozen
            if any(isinstance(s, FrozenStatus) for s in monster.status_effects):
                self.add_message(f"{monster.name} is frozen and can't move!")
                continue
            
            # Monster special abilities
            new_monster = monster.special_ability()
            if new_monster:
                self.additional_monsters.append(new_monster)
                self.add_message(f"{monster.name} spawns a {new_monster.name}!")
            
            # Monster attack
            base_damage = max(1, monster.atk - (self.character.total_def * 0.7))
            damage = round(base_damage * random.uniform(0.9, 1.1))
            
            # Check for dodge chance
            if ("Archer" in monster.name or "Thief" in monster.name) and random.random() < 0.3:
                self.add_message(f"{monster.name} dodges your attack!")
                continue
            
            self.character.current_hp -= damage
            self.add_message(f"{monster.name} attacks for {damage} damage!")
            
            # Attack effects
            effect_messages = monster.attack_effect(self.character)
            for msg in effect_messages:
                self.add_message(msg)
            
            if self.character.current_hp <= 0:
                self.add_message(f"{self.character.name} was defeated!")
                self.character.current_hp = 1  # Prevent death
                return True, self.get_messages()
        
        # Update status effects
        status_messages = self.character.update_statuses()
        for msg in status_messages:
            self.add_message(msg)
        
        status_messages = self.monster.update_statuses()
        for msg in status_messages:
            self.add_message(msg)
        
        for m in self.additional_monsters:
            status_messages = m.update_statuses()
            for msg in status_messages:
                self.add_message(msg)
        
        # Check victory conditions
        if self.monster.current_hp <= 0 and not self.additional_monsters:
            self.handle_victory()
            return True, self.get_messages()
        
        return False, self.get_messages()
    
    def handle_victory(self) -> None:
        total_exp = self.monster.exp_reward
        for m in self.additional_monsters:
            total_exp += m.exp_reward
        
        self.add_message(f"Gained {total_exp} EXP!")
        self.character.add_exp(total_exp)
        
        all_drops = []
        for m in [self.monster] + self.additional_monsters:
            if m.current_hp <= 0:
                drops = m.roll_for_loot()
                if drops:
                    all_drops.extend(drops)
        
        if all_drops:
            self.add_message("Loot Dropped:")
            for item, rarity in all_drops:
                self.add_message(f"- {item} ({rarity})")
                self.character.inventory.add_item(item)
        else:
            self.add_message("No loot dropped.")
        
        # Small HP/MP recovery after battle
        self.character.current_hp = min(self.character.max_hp, self.character.current_hp + max(10, self.character.max_hp // 10))
        self.character.current_mp = min(self.character.max_mp, self.character.current_mp + max(5, self.character.max_mp // 10))

# ---------------------------
# Discord Bot Implementation
# ---------------------------
class JanusPenthos(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.characters: Dict[int, Character] = {}  # user_id -> Character
        self.active_combats: Dict[int, Combat] = {}  # user_id -> Combat
        
        # Register commands
        self.add_command(commands.Command('start', self.start_game))
        self.add_command(commands.Command('stats', self.show_stats))
        self.add_command(commands.Command('explore', self.explore))
        self.add_command(commands.Command('inventory', self.show_inventory))
        self.add_command(commands.Command('skills', self.show_skills))
        self.add_command(commands.Command('attack', self.attack))
        self.add_command(commands.Command('skill', self.use_skill))
        self.add_command(commands.Command('flee', self.flee))
        self.add_command(commands.Command('save', self.save_game))
        self.add_command(commands.Command('load', self.load_game))
    
    async def start_game(self, ctx):
        """Start a new game with your character"""
        user_id = ctx.author.id
        if user_id in self.characters:
            await ctx.send("You already have a character! Use `!load` to resume your adventure.")
            return
        
        name = ctx.author.display_name
        self.characters[user_id] = Character(name, user_id)
        await ctx.send(f"Welcome, {name}! Your adventure begins now.")
        await ctx.send(self.characters[user_id].show_stats())
        await ctx.send("You have 3 skill points to allocate. Use `!stats` to allocate them.")
    
    async def show_stats(self, ctx):
        """Show your character's stats"""
        user_id = ctx.author.id
        if user_id not in self.characters:
            await ctx.send("You don't have a character yet. Use `!start` to begin your adventure.")
            return
        
        char = self.characters[user_id]
        await ctx.send(char.show_stats())
    
    async def explore(self, ctx):
        """Explore and encounter monsters"""
        user_id = ctx.author.id
        if user_id not in self.characters:
            await ctx.send("You don't have a character yet. Use `!start` to begin your adventure.")
            return
        
        char = self.characters[user_id]
        if char.in_combat:
            await ctx.send("You're already in combat! Use `!attack`, `!skill`, or `!flee`.")
            return
        
        monster_weights = [
            ("Slime", 30),
            ("Pyro Slime", 15),
            ("Hydro Slime", 15),
            ("Geo Slime", 15),
            ("Dendro Slime", 10),
            ("Cryo Slime", 10),
            ("Jelly", 5),
            ("Forest Jelly", 3),
            ("Goblin", 20),
            ("Goblin Tank", 10),
            ("Goblin Warrior", 10),
            ("Goblin Archer", 10),
            ("Goblin Thief", 10),
            ("Goblin Shaman", 5)
            
        ]
        
        available_monsters = []
        for name, weight in monster_weights:
            if name.startswith("Goblin") and char.level < 5:
                continue
            available_monsters.append((name, weight))
        
        if not available_monsters:
            await ctx.send("No monsters available for encounter at your level!")
            return
        
        monster_name = random.choices(
            [m[0] for m in available_monsters],
            weights=[m[1] for m in available_monsters]
        )[0]
        
        monster_level = max(1, min(char.level + random.randint(-2, 2), 100)
        monster = create_monster(monster_name, monster_level)
        
        char.in_combat = True
        combat = Combat(char, monster)
        self.active_combats[user_id] = combat
        
        await ctx.send(combat.start_combat())
        await ctx.send("What will you do? `!attack`, `!skill <number>`, or `!flee`")
    
    async def show_inventory(self, ctx):
        """Show your inventory"""
        user_id = ctx.author.id
        if user_id not in self.characters:
            await ctx.send("You don't have a character yet. Use `!start` to begin your adventure.")
            return
        
        char = self.characters[user_id]
        await ctx.send(char.inventory.show_inventory())
    
    async def show_skills(self, ctx):
        """Show your available skills"""
        user_id = ctx.author.id
        if user_id not in self.characters:
            await ctx.send("You don't have a character yet. Use `!start` to begin your adventure.")
            return
        
        char = self.characters[user_id]
        await ctx.send(char.show_skills())
    
    async def attack(self, ctx):
        """Attack in combat"""
        user_id = ctx.author.id
        if user_id not in self.characters or user_id not in self.active_combats:
            await ctx.send("You're not in combat right now. Use `!explore` to find monsters.")
            return
        
        char = self.characters[user_id]
        combat = self.active_combats[user_id]
        
        combat_ended, message = combat.do_player_turn("attack")
        await ctx.send(message)
        
        if combat_ended:
            char.in_combat = False
            del self.active_combats[user_id]
            return
        
        # Monster turn
        combat_ended, message = combat.do_monster_turn()
        await ctx.send(message)
        
        if combat_ended:
            char.in_combat = False
            if user_id in self.active_combats:
                del self.active_combats[user_id]
    
    async def use_skill(self, ctx, skill_index: int):
        """Use a skill in combat"""
        user_id = ctx.author.id
        if user_id not in self.characters or user_id not in self.active_combats:
            await ctx.send("You're not in combat right now. Use `!explore` to find monsters.")
            return
        
        try:
            skill_index = int(skill_index) - 1
        except ValueError:
            await ctx.send("Please provide a valid skill number.")
            return
        
        char = self.characters[user_id]
        combat = self.active_combats[user_id]
        
        combat_ended, message = combat.do_player_turn("skill", skill_index)
        await ctx.send(message)
        
        if combat_ended:
            char.in_combat = False
            del self.active_combats[user_id]
            return
        
        # Monster turn
        combat_ended, message = combat.do_monster_turn()
        await ctx.send(message)
        
        if combat_ended:
            char.in_combat = False
            if user_id in self.active_combats:
                del self.active_combats[user_id]
    
    async def flee(self, ctx):
        """Attempt to flee from combat"""
        user_id = ctx.author.id
        if user_id not in self.characters or user_id not in self.active_combats:
            await ctx.send("You're not in combat right now. Use `!explore` to find monsters.")
            return
        
        char = self.characters[user_id]
        combat = self.active_combats[user_id]
        
        combat_ended, message = combat.do_player_turn("flee")
        await ctx.send(message)
        
        if combat_ended:
            char.in_combat = False
            if user_id in self.active_combats:
                del self.active_combats[user_id]
    
    async def save_game(self, ctx):
        """Save your game progress"""
        user_id = ctx.author.id
        if user_id not in self.characters:
            await ctx.send("You don't have a character yet. Use `!start` to begin your adventure.")
            return
        
        char = self.characters[user_id]
        data = {
            "name": char.name,
            "user_id": char.user_id,
            "level": char.level,
            "exp": char.exp,
            "ascension_count": char.ascension_count,
            "base_vit": char.base_vit,
            "base_int": char.base_int,
            "base_str": char.base_str,
            "base_def": char.base_def,
            "base_agi": char.base_agi,
            "skill_points": char.skill_points,
            "current_hp": char.current_hp,
            "current_mp": char.current_mp,
            "equipment": {
                "weapon": char.equipment.weapon,
                "armor": char.equipment.armor,
                "accessory": char.equipment.accessory
            },
            "inventory": char.inventory.items
        }
        
        try:
            os.makedirs("saves", exist_ok=True)
            with open(f"saves/{user_id}.json", "w") as f:
                json.dump(data, f, indent=2)
            await ctx.send("Game saved successfully!")
        except Exception as e:
            await ctx.send(f"Error saving game: {e}")
    
    async def load_game(self, ctx):
        """Load your saved game"""
        user_id = ctx.author.id
        save_path = f"saves/{user_id}.json"
        
        if not os.path.exists(save_path):
            await ctx.send("No save file found for you. Use `!start` to begin a new game.")
            return
        
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
            
            char = Character(data["name"], data["user_id"])
            char.level = data["level"]
            char.exp = data["exp"]
            char.ascension_count = data["ascension_count"]
            char.base_vit = data["base_vit"]
            char.base_int = data["base_int"]
            char.base_str = data["base_str"]
            char.base_def = data["base_def"]
            char.base_agi = data["base_agi"]
            char.skill_points = data["skill_points"]
            char.current_hp = data["current_hp"]
            char.current_mp = data["current_mp"]
            char.equipment.weapon = data["equipment"]["weapon"]
            char.equipment.armor = data["equipment"]["armor"]
            char.equipment.accessory = data["equipment"]["accessory"]
            char.inventory.items = data["inventory"]
            
            char.update_base_stats()
            self.characters[user_id] = char
            
            await ctx.send("Game loaded successfully!")
            await ctx.send(char.show_stats())
        except Exception as e:
            await ctx.send(f"Error loading game: {e}")

# Run the bot
if __name__ == "__main__":
    bot = JanusPenthos()
    bot.run("YOUR_DISCORD_BOT_TOKEN")  # Replace with your actual bot token
