import const
import handler_game
import merc
import object_creator
import instance


def spell_create_rose(sn, level, ch, victim, target):
    rose = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_ROSE], 0)
    handler_game.act("$n has created a beautiful red rose.", ch, rose, None, merc.TO_ROOM)
    ch.send("You create a beautiful red rose.\n")
    ch.put(rose)


const.register_spell(const.skill_type("create rose",
                          {'mage': 16, 'cleric': 11, 'thief': 10, 'warrior': 24},
                          {'mage': 1, 'cleric': 1, 'thief': 2, 'warrior': 2},
                          spell_create_rose, merc.TAR_IGNORE, merc.POS_STANDING, None,
                          const.SLOT(511), 30, 12, "", "!Create Rose!", ""))
