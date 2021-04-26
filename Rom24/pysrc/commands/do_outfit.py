import logging

logger = logging.getLogger()

import merc
import interp
import const
import object_creator
import instance


# equips a character
def do_outfit(ch, argument):
    if 5 < ch.level < 55 or ch.is_npc():
        ch.send("Find it yourself!\n")
        return

    item = ch.slots.light
    if not item:
        item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_SCHOOL_BANNER], 0)
        item.cost = 0
        ch.put(item)
        ch.equip(item, True, False)
        item = None

    item = ch.slots.body
    if not item:
        item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_SCHOOL_VEST], 0)
        item.cost = 0
        ch.put(item)
        ch.equip(item, True, False)
        item = None

    # do the weapon thing
    item = ch.slots.main_hand
    if not item:
        vnum = merc.OBJ_VNUM_SCHOOL_SWORD  # just in case!
        for k, weapon in const.weapon_table.items():
            if argument in weapon.gsn:
                vnum = weapon.vnum
        item = object_creator.create_item(instance.item_templates[vnum], 0)
        ch.put(item)
        ch.equip(item, True, False)
        item = None

    item = ch.slots.main_hand
    shield = ch.slots.off_hand
    if (not item or not item.flags.two_handed) and not shield:
        item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_SCHOOL_SHIELD], 0)
        item.cost = 0
        ch.put(item)
        ch.equip(item, True, False)
        item = None

    ch.send("You have been equipped by Mota.\n")


interp.register_command(interp.cmd_type('outfit', do_outfit, merc.POS_RESTING, 0, merc.LOG_NORMAL, 1))
