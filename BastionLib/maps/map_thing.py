# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from ..binary_file import BaseBinaryRepresentation, BinaryProperty, Types

P = BinaryProperty


class MapThing(BaseBinaryRepresentation):
    """
        Represents a map thing.
    """

    VERSION = 35

    TYPE_UNKNOWN = 'UNKNOWN'
    TYPE_OBSTACLE = 'OBSTACLE'
    TYPE_GENERATOR = 'GENERATOR'
    TYPE_UNIT = 'UNIT'
    TYPE_PROJECTILE = 'PROJECTILE'
    TYPE_DAMAGE_FIELD = 'DAMAGE_FIELD'
    TYPE_SPAWN_POINT = 'SPAWN_POINT'
    TYPE_LOOT = 'LOOT'
    TYPE_MAP_AREA = 'MAP_AREA'
    TYPE_TERRAIN_TILE = 'TERRAIN_TILE'
    TYPE_BACKDROP_FLYER = 'BACKDROP_FLYER'
    TYPE_WEAPON = 'WEAPON'
    TYPE_ANIMATION = 'ANIMATION'

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),
        P('data_type', Types.STRING, param=1),
        P('name', Types.STRING, param=1),
        P('location', Types.INT, repeat=2),
        P('active', Types.BOOL, default=True),
        P('activate_when_seen', Types.BOOL, default=True),
        P('end_location', Types.INT, repeat=2),
        P('id', Types.INT),
        P('activate_on_enter_id', Types.INT),
        P('activate_on_enter_name', Types.STRING, param=1),
        P('activate_on_enter_names', Types.STRING_LIST, param=1),
        P('requires_solid_ground', Types.BOOL, default=False),
        P('group_name', Types.STRING, param=1),
        P('use_target_ai', Types.BOOL, default=False),
        P('use_move_ai', Types.BOOL, default=False),
        P('use_attack_ai', Types.BOOL, default=False),
        P('flip_effect', Types.INT),
        P('flip_horizontal', Types.BOOL, default=False),
        P('flip_vertical', Types.BOOL, default=False),
        P('activate_on_enter_ids', Types.INT_LIST),
        P('drop_loot', Types.BOOL, default=True),
        P('sort_modifier', Types.INT, default=1),
        P('color', Types.COLOR, default=[0xFF, 0xFF, 0xFF, 0xFF]),
        P('scale', Types.FLOAT, default=1.0),
        P('use_unexplored_hue', Types.BOOL, default=False),
        P('health_fraction', Types.FLOAT, default=1.0),
        P('walkable', Types.BOOL, default=True),
        P('invulnerable', Types.BOOL, default=False),
        P('use_as_fx', Types.BOOL, default=False),
        P('rotation_speed', Types.FLOAT, default=1.0),
        P('draw_layer', Types.STRING, default='DECAL', param=1),
        P('offset_z', Types.FLOAT),
        P('angle', Types.FLOAT),
        P('fall_in', Types.BOOL, default=True),
        P('attach_to_id', Types.INT),
        P('activation_range', Types.FLOAT, default=600.0),
        P('help_text_id', Types.STRING, param=1),
        P('flying', Types.BOOL, default=False),
        P('group_names', Types.STRING_LIST, param=1),
        P('give_xp', Types.BOOL, default=True),
        P('friendly', Types.BOOL, default=True),
        P('parallax', Types.BOOL, default=False),
        P('ignore_grid_manager', Types.BOOL, default=False),
        P('wobble', Types.BOOL, default=True)
    )


class MapThingGroup(BaseBinaryRepresentation):
    """
        Represents a group of map things.
    """

    VERSION = 1

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),
        P('name', Types.STRING, param=1, default='Default'),
        P('things', MapThing, repeat=Types.INT),
        P('visible', Types.BOOL, default=True),
        P('selectable', Types.BOOL, default=True)
    )
    
    def __init__(self, name=None):
        """
            Creates a new empty group.
        """
        
        super().__init__()
        if name:
            self.name = name