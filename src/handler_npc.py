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
import copy
import os
import hashlib
import time
import logging

logger = logging.getLogger()

import living
import pyprogs
import bit
import merc
import tables
import handler_item
import json
import settings
import instance


class Npc(living.Living):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        #self.is_npc = True
        self.vnum = 0  # Needs to come before the template to setup the instance
        self.is_pc = False
        self.memory = None
        self.spec_fun = None
        self.new_format = True
        self.area = ""
        self.act = bit.Bit(merc.PLR_NOSUMMON, flagset_name="act_flags")
        self.off_flags = bit.Bit(flagset_name="off_flags")
        self.damage = [0, 0, 0]
        self.start_pos = 0
        self.default_pos = 0
        self.hit_dice = [0, 0, 0]
        self.mana_dice = [0, 0, 0]
        self.dam_dice = [0, 0, 0]
        self.template_wealth = 0
        self.count = 0
        self.killed = 0
        self.pShop = None
        self.listeners = {}
        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]
        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.instancer()
        if self.environment:
            if self._environment not in instance.global_instances.keys():
                self.environment = None
        if self.inventory:
            for instance_id in self.inventory[:]:
                handler_item.Items.load(instance_id=instance_id)
        for item_id in self.equipped.values():
            if item_id:
                handler_item.Items.load(instance_id=item_id)
        if self.instance_id:
            self.instance_setup()
            Npc.instance_count += 1
        else:
            Npc.template_count += 1
        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            logger.trace("Freeing %s" % str(self))
            if self.instance_id:
                Npc.instance_count -= 1
                if instance.characters.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Npc.template_count -= 1
        except:
            return

    def __repr__(self):
        if self.instance_id:
            return "<NPC Instance: %s ID %d template %d>" % (self.short_descr, self.instance_id, self.vnum)
        else:
            return "<NPC Template: %s:%s>" % (self.short_descr, self.vnum)

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.npcs[self.instance_id] = self
        instance.characters[self.instance_id] = self
        if self.vnum not in instance.instances_by_npc.keys():
            instance.instances_by_npc[self.vnum] = [self.instance_id]
        else:
            instance.instances_by_npc[self.vnum] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_npc[self.vnum].remove(self.instance_id)
        del instance.npcs[self.instance_id]
        del instance.characters[self.instance_id]
        del instance.global_instances[self.instance_id]

    register_signal = pyprogs.register_signal
    absorb = pyprogs.absorb

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ('desc', 'send'):
                continue
            elif str(k) in ('_last_saved', '_md5'):
                continue
            else:
                tmp_dict[k] = v

        cls_name = '__class__/' + __name__ + '.' + self.__class__.__name__
        return {cls_name: outer_encoder(tmp_dict)}

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = '__class__/' + __name__ + '.' + cls.__name__
        if cls_name in data:
            tmp_data = outer_decoder(data[cls_name])
            return cls(**tmp_data)
        return data

    def save(self, force: bool=False):
        if self._last_saved is None:
            self._last_saved = time.time() - settings.SAVE_LIMITER - 2
        if not force and time.time() < self._last_saved + settings.SAVE_LIMITER:
            return

        if self.instance_id:
            top_dir = settings.INSTANCE_DIR
            number = self.instance_id
        else:
            top_dir = settings.AREA_DIR
            number = self.vnum
        if self.in_area.instance_id:
            area_number = self.in_area.instance_id
        else:
            area_number = self.in_area.index
        pathname = os.path.join(top_dir, '%d-%s' % (area_number, self.in_area.name), 'npcs')

        os.makedirs(pathname, 0o755, True)
        if settings.SAVE_FORMAT['Pickle'][0]:
            filename = os.path.join(pathname, '%d-npc%s' % (number, settings.SAVE_FORMAT['Pickle'][1]))
        elif settings.SAVE_FORMAT['JSON'][0]:
            filename = os.path.join(pathname, '%d-npc%s' % (number, settings.SAVE_FORMAT['JSON'][1]))
        else:
            filename = os.path.join(pathname, '%d-npc.json' % (number,))
        logger.info('Saving %s', filename)
        js = json.dumps(self, default=instance.to_json, sort_keys=True)
        md5 = hashlib.md5(js.encode('utf-8')).hexdigest()
        if self._md5 != md5:
            self._md5 = md5
            if settings.SAVE_FORMAT['JSON'][0]:
                #json version
                with open(filename, 'w') as fp:
                    fp.write(js)
            else:
                #pickle version
                import pickle
                with open(filename, 'wb') as fp:
                    pickle.dump(js, fp, pickle.HIGHEST_PROTOCOL)

        if self.inventory:
            for item_id in self.inventory[:]:
                if item_id not in instance.items:
                    logger.error('Item %d is in NPC %d\'s inventory, but does not exist?', item_id, self.instance_id)
                    continue
                item = instance.items[item_id]
                item.save(in_inventory=True, force=force)
        for item_id in self.equipped.values():
            if item_id:
                if item_id not in instance.items:
                    logger.error('Item %d is in NPC %d\'s equipment, but does not exist?', item_id, self.instance_id)
                    continue
                item = instance.items[item_id]
                item.save(is_equipped=True, force=force)

    @classmethod
    def load(cls, vnum: int=None, instance_id: int=None):
        if instance_id:
            if instance_id in instance.characters:
                logger.warn('Instance %d of npc already loaded!', instance_id)
                return
            pathname = settings.INSTANCE_DIR
            number = instance_id
        elif vnum:
            pathname = settings.AREA_DIR
            number = vnum
        else:
            raise ValueError('To load an NPC, you must provide either a VNUM or an Instance_ID!')

        if settings.SAVE_FORMAT['Pickle'][0]:
            target_file = '%d-item%s' % (number, settings.SAVE_FORMAT['Pickle'][1])
        elif settings.SAVE_FORMAT['JSON'][0]:
            target_file = '%d-item%s' % (number, settings.SAVE_FORMAT['JSON'][1])
        else:
            target_file = '%d-item.json' % (number,)
        filename = None
        for a_path, a_directory, i_files in os.walk(pathname):
            if target_file in i_files:
                filename = os.path.join(a_path, target_file)
                break
        if not filename:
            raise ValueError('Cannot find %s' % target_file)
        jso = ''
        if settings.SAVE_FORMAT['JSON'][0]:
            #json version
            with open(filename, 'r+') as f:
                #this reads in one line at a time from stdin - way faster. Syn
                for line in f:
                    jso += line
        else:
            #pickle version
            import pickle
            with open(filename, 'rb') as f:
                jso = pickle.load(f)
        obj = json.loads(jso, object_hook=instance.from_json)
        if isinstance(obj, Npc):
            # This just ensures that all items the player has are actually loaded.
            if obj.inventory:
                for item_id in obj.inventory[:]:
                    handler_item.Items.load(instance_id=item_id)
            return obj
        else:
            logger.error('Could not load npc data for %d', number)
            return None
