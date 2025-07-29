import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Define Item and CharacterInventory classes (same as before)
class Item:
    def __init__(self, name, item_type, stats=None, quantity=1):
        self.name = name
        self.type = item_type  # 'weapon', 'armor', 'potion', 'misc'
        self.stats = stats or {}
        self.quantity = quantity
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'stats': self.stats,
            'quantity': self.quantity
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['type'], data['stats'], data['quantity'])
    
    def __str__(self):
        if self.quantity > 1:
            return f"{self.name} (x{self.quantity})"
        return self.name

class CharacterInventory:
    def __init__(self):
        self.items = []
        self.equipped = {
            'weapon': None,
            'head': None,
            'chest': None,
            'legs': None,
            'accessory': None
        }
    
    def add_item(self, name, item_type, stats=None, quantity=1):
        """Add an item to inventory"""
        for item in self.items:
            if item.name == name and item.type == item_type and item_type in ['potion', 'misc']:
                item.quantity += quantity
                return f"Added {quantity} {name}(s)"
        
        new_item = Item(name, item_type, stats, quantity)
        self.items.append(new_item)
        return f"Added {new_item} to inventory"
    
    def remove_item(self, name, quantity=1):
        """Remove items from inventory"""
        for item in self.items[:]:
            if item.name == name:
                if item.quantity > quantity:
                    item.quantity -= quantity
                    return f"Removed {quantity} {name}(s)"
                else:
                    self.items.remove(item)
                    return f"Removed all {item.quantity} {name}(s)"
        return f"{name} not found in inventory"
    
    def equip(self, item_name):
        """Equip a weapon or armor"""
        for item in self.items:
            if item.name == item_name and item.type in ['weapon', 'armor']:
                slot = 'weapon' if item.type == 'weapon' else item.stats.get('slot', 'chest')
                
                if self.equipped[slot]:
                    self.items.append(self.equipped[slot])
                
                self.equipped[slot] = item
                self.items.remove(item)
                return f"Equipped {item_name} in {slot} slot"
        return f"Cannot equip {item_name} - not found or wrong type"
    
    def use_potion(self, potion_name):
        """Use a potion"""
        for item in self.items:
            if item.name == potion_name and item.type == 'potion':
                item.quantity -= 1
                if item.quantity <= 0:
                    self.items.remove(item)
                return f"Used {potion_name}", item.stats
        return f"No {potion_name} in inventory", None
    
    def to_dict(self):
        return {
            'items': [item.to_dict() for item in self.items],
            'equipped': {
                slot: item.to_dict() if item else None
                for slot, item in self.equipped.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        inv = cls()
        inv.items = [Item.from_dict(item_data) for item_data in data.get('items', [])]
        inv.equipped = {
            slot: Item.from_dict(item_data) if item_data else None
            for slot, item_data in data.get('equipped', {}).items()
        }
        return inv

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Database to store character inventories
CHARACTER_DB = "character_inventories.json"

def load_inventories():
    if os.path.exists(CHARACTER_DB):
        with open(CHARACTER_DB, 'r') as f:
            return {
                name: CharacterInventory.from_dict(data)
                for name, data in json.load(f).items()
            }
    return {}

def save_inventories(inventories):
    with open(CHARACTER_DB, 'w') as f:
        json.dump({
            name: inv.to_dict()
            for name, inv in inventories.items()
        }, f, indent=2)

# Bot Commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="inventory", description="View your character's inventory")
@app_commands.describe(character="Your character's name")
async def inventory(interaction: discord.Interaction, character: str):
    inventories = load_inventories()
    if character not in inventories:
        await interaction.response.send_message(f"Character {character} not found!", ephemeral=True)
        return
    
    inv = inventories[character]
    embed = discord.Embed(title=f"{character}'s Inventory", color=0x00ff00)
    
    # Equipped items
    equipped = []
    for slot, item in inv.equipped.items():
        if item:
            stat = item.stats.get('damage', item.stats.get('defense', 0))
            equipped.append(f"**{slot.title()}:** {item} (`{stat}`)")
    
    embed.add_field(name="⚔️ Equipped", value="\n".join(equipped) if equipped else "None", inline=False)
    
    # Other items
    items = []
    for item in inv.items:
        if item.type in ['weapon', 'armor']:
            stat = item.stats.get('damage', item.stats.get('defense', 0))
            items.append(f"• {item} (`{stat}`)")
        else:
            items.append(f"• {item}")
    
    embed.add_field(name="🎒 Backpack", value="\n".join(items) if items else "Empty", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_item", description="Add an item to a character's inventory")
@app_commands.describe(
    character="Your character's name",
    item_name="Name of the item",
    item_type="Type of item (weapon/armor/potion/misc)",
    quantity="How many to add",
    damage="For weapons only",
    defense="For armor only",
    slot="For armor only (head/chest/legs/accessory)"
)
async def add_item(
    interaction: discord.Interaction,
    character: str,
    item_name: str,
    item_type: str,
    quantity: int = 1,
    damage: int = 0,
    defense: int = 0,
    slot: str = None
):
    item_type = item_type.lower()
    if item_type not in ['weapon', 'armor', 'potion', 'misc']:
        await interaction.response.send_message("Invalid item type! Use weapon/armor/potion/misc", ephemeral=True)
        return
    
    stats = {}
    if item_type == 'weapon':
        stats['damage'] = damage
    elif item_type == 'armor':
        stats['defense'] = defense
        if slot:
            stats['slot'] = slot.lower()
    
    inventories = load_inventories()
    if character not in inventories:
        inventories[character] = CharacterInventory()
    
    result = inventories[character].add_item(item_name, item_type, stats, quantity)
    save_inventories(inventories)
    
    await interaction.response.send_message(f"✅ {result}")

@bot.tree.command(name="equip", description="Equip an item from inventory")
@app_commands.describe(
    character="Your character's name",
    item_name="Name of the item to equip"
)
async def equip(interaction: discord.Interaction, character: str, item_name: str):
    inventories = load_inventories()
    if character not in inventories:
        await interaction.response.send_message(f"Character {character} not found!", ephemeral=True)
        return
    
    result = inventories[character].equip(item_name)
    save_inventories(inventories)
    
    await interaction.response.send_message(f"🛡️ {result}")

@bot.tree.command(name="use_potion", description="Use a potion from inventory")
@app_commands.describe(
    character="Your character's name",
    potion_name="Name of the potion to use"
)
async def use_potion(interaction: discord.Interaction, character: str, potion_name: str):
    inventories = load_inventories()
    if character not in inventories:
        await interaction.response.send_message(f"Character {character} not found!", ephemeral=True)
        return
    
    result, stats = inventories[character].use_potion(potion_name)
    save_inventories(inventories)
    
    if stats:
        effect = ", ".join(f"{k}: {v}" for k, v in stats.items())
        await interaction.response.send_message(f"🧪 {result}\n✨ Effect: {effect}")
    else:
        await interaction.response.send_message(f"❌ {result}")

# Run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN_HERE')