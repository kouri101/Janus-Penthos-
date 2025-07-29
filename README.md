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
