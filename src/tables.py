"""
/***************************************************************************
 *  Original Diku Mud copyright (C) 1990, 1991 by Sebastian Hammer,        *
 *  Michael Seifert, Hans Henrik St{rfeldt, Tom Madsen, and Katja Nyboe.   *
 *                                                                         *
 *  Merc Diku Mud improvments copyright (C) 1992, 1993 by Michael          *
 *  Chastain, Michael Quan, and Mitchell Tse.                              *
 *                                                                         *
 *  In order to use any part of this Merc Diku Mud, you must comply with   *
 *  both the original Diku license in 'license.doc' as well the Merc       *
 *  license in 'license.txt'.  In particular, you may not remove either of *
 *  these copyright notices.                                               *
 *                                                                         *
 *  Much time and thought has gone into this software and you are          *
 *  benefitting.  We hope that you share your changes too.  What goes      *
 *  around, comes around.                                                  *
 ***************************************************************************/

/***************************************************************************
*   ROM 2.4 is copyright 1993-1998 Russ Taylor                             *
*   ROM has been brought to you by the ROM consortium                      *
*       Russ Taylor (rtaylor@hypercube.org)                                *
*       Gabrielle Taylor (gtaylor@hypercube.org)                           *
*       Brian Moore (zump@rom.org)                                         *
*   By using this code, you have agreed to follow the terms of the         *
*   ROM license, in the file Rom24/doc/rom.license                         *
***************************************************************************/
/************
 * Ported to Python by Davion of MudBytes.net
 * Using Miniboa https://code.google.com/p/miniboa/
 * Now using Python 3 version https://code.google.com/p/miniboa-py3/
 ************/
"""
from collections import OrderedDict, namedtuple
import logging

logger = logging.getLogger()

clan_type = namedtuple('clan_type', 'name, who_name, hall, independent')
clan_table = OrderedDict()

position_type = namedtuple('position_type', 'name, short_name')
position_table = OrderedDict()

sex_table = OrderedDict()

# for sizes */
size_table = []

# various flag tables */
flag_type = namedtuple('flag_type', 'name, bit, settable')
act_flags = OrderedDict()
plr_flags = OrderedDict()
affect_flags = OrderedDict()
off_flags = OrderedDict()
imm_flags = OrderedDict()
form_flags = OrderedDict()
part_flags = OrderedDict()
comm_flags = OrderedDict()
exit_flags = OrderedDict()
vuln_flags = OrderedDict()

wiznet_type = namedtuple('wiznet_type', 'name bit level')
wiznet_table = OrderedDict()


bit_flags = OrderedDict()
bit_flags["act_flags"] = act_flags
bit_flags["plr_flags"] = plr_flags
bit_flags["affect_flags"] = affect_flags
bit_flags["off_flags"] = off_flags
bit_flags["imm_flags"] = imm_flags
bit_flags["form_flags"] = form_flags
bit_flags["part_flags"] = part_flags
bit_flags["comm_flags"] = comm_flags
bit_flags["exit_flags"] = exit_flags
bit_flags["vuln_flags"] = vuln_flags
bit_flags["wiznet_table"] = wiznet_table

