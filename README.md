
Autobattle 0.4.1
COMMANDS

        !battle  "Start your daily auto-battles (10 max with 24h cooldown)
        !profile "View your character profile
        !inventory "Check your inventory
        !equip [item] "Equip an item from your inventory
        !rest" "Heal and reset daily battles (doesn't affect cooldown)
        !help"  "Show this help message










Monster Encouter 
Commands:
For discord

    !start - Create a new character

    !stats - Show your character stats

    !explore - Find a monster to fight

    !inventory - Show your inventory

    !skills - Show your available skills

    !attack - Attack in combat

    !skill <number> - Use a skill in combat

    !flee - Attempt to flee from combat

    !save - Save your game

    !load - Load your saved game








COMMANDS CHARACTER GROWTH 
        !create - Make a new character

        !addexp <amount> - Add experience points

        !allocate - Distribute status points

        !equip - Edit equipment

        !stats - Show character stats

        !save - Save your character

        !load - Load your character

        !delete - Delete your character

The bot will create a characters/ directory to store all character data as JSON files.











    AUTO BATTLE 
    How to Use:

    Create a Character:
    text

/create_character name:"Aric"

Check Character Info:
text

/character_info name:"Aric"

Start a Battle:
text

/autobattle character:"Aric"

Example Battle Output:
text

⚔️ Aric vs Level 5 Goblin
Turn 1: Aric hits Goblin for 12 damage
Goblin hits Aric for 8 damage
Turn 2: Aric hits Goblin for 24 damage (CRIT!)
🏆 Victory! Aric defeated the Goblin!

✨ Gained 45 EXP and 25 gold!
🔹 EXP: 45/100
Battles today: 1/10 | Next battle: now
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
   Basic Commands: Discord 

        !character - View your character sheet

        !create <name> - Create a new character

        !distribute <stat> - Spend a stat point (VIT/INT/STR/DEF/AGI)

        !equip <slot> <name> <power> <stat> <bonus> - Equip an item

        !roll - Roll for a random event

    Admin Commands:

        !admin_reset [user] - Reset a character (bot owner only)

    Equipment Examples:

        !equip Weapon Sword 5 - Equip a sword with +5 damage

        !equip Armor Plate 3 VIT 2 - Equip plate armor with +3 defense and +2 VIT

        !equip Accessory Ring STR 1 - Equip a ring with +1 STR


Stats Calculator 

Main Commands
Command	Description
!stats	shows the main help menu with available commands
!stats help	Detailed help with parameter explanations and examples
Calculation Commands
Command	Description
!stats new	Starts a new calculation (resets all values)
!stats set <parameter> <value>	Sets a stat value (e.g., !stats set character_level 50)
!stats calculate	Calculates and displays final stats
!stats show	: Shows your current input values
Example Workflow

    Start a new calculation:
    text

!stats new

Set your character level and stats:
text

!stats set character_level 50
!stats set vit_points 30
!stats set str_points 50

Set weapon/armor bonuses:
text

!stats set flat_weapon_atk 150
!stats set atk_percent 0.25

Calculate and view results:
text

    !stats calculate

Available Parameters for !stats set
Character Progression

    character_level (1-100)

    vit_points (VIT points)

    def_points (DEF points)

    str_points (STR points)

    int_points (INT points)

    agi_points (AGI points)

Attack Stats

    flat_weapon_atk (Base weapon ATK)

    atk_percent (ATK % bonus)

    crit_rate_weapon, crit_rate_armor, crit_rate_substats (Crit Rate sources)

    crit_damage_weapon, crit_damage_armor, crit_damage_substats (Crit DMG sources)

    elemental_dmg_bonus (Elemental DMG %)

Defense Stats

    def_percent (DEF % bonus)

    hp_percent (HP % bonus)

Speed & MP

    speed_boots (Speed from boots)

    speed_substats (Speed from substats)

    mp_gear (MP from gear)

    mp_substats (MP from substats)

Notes

    The bot stores calculations per user, so multiple people can use it simultaneously.

    Use !stats help for a full breakdown of parameters and examples.







INVENTORY SYSTEM 



Commands:

    /inventory [character] - View a character's inventory

    /add_item - Add items to a character:
    text

    /add_item character:"Aric" item_name:"Iron Sword" item_type:"weapon" damage:15
    /add_item character:"Liana" item_name:"Health Potion" item_type:"potion" quantity:3
    /add_item character:"Aric" item_name:"Steel Armor" item_type:"armor" defense:20 slot:"chest"

    /equip [character] [item_name] - Equip an item

    /use_potion [character] [potion_name] - Use a potion

Features:

    Persistent storage (saves to JSON file)

    Beautiful embed displays

    Error handling

    Autocomplete for commands

    Supports weapons, armor, and potions

Example Session:
text

    /add_item character:"Aric" item_name:"Dragon Slayer" item_type:"weapon" damage:25
    ✅ Added Dragon Slayer to inventory

    /equip character:"Aric" item_name:"Dragon Slayer"
    🛡️ Equipped Dragon Slayer in weapon slot

    /inventory character:"Aric"
    [Shows beautiful embed with equipped items and inventory]

The bot handles all inventory management through Discord slash commands and automatically saves all changes between restarts. The code is organized, error-free, and ready to integrate with your existing Janus Penthos bot.
