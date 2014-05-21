# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from ..binary_file import BaseBinaryRepresentation, BinaryProperty, Types
from ..binary_stream import BinaryStream

from .spawn import *
from .map_thing import *

P = BinaryProperty


class TerrainLayer(BaseBinaryRepresentation):
    """
        Represents a map terrain layer.
    """

    VERSION = 7

    def __init__(self):
        """
            Sets the properties.

            Since of the properties references the class itself, they
            need to be declared here.
        """

        TerrainLayer._properties = (
            P('version', Types.INT, default=TerrainLayer.VERSION, equals=TerrainLayer.VERSION),
            P('name', Types.STRING, param=1),
            P('color', Types.COLOR, default=[0xFF, 0xFF, 0xFF, 0xFF]),
            P('tiles', MapThing, repeat=Types.INT),
            P('linked_layers', TerrainLayer, repeat=Types.INT),
            P('mask', Types.BOOL, default=False),
            P('blend_filter', Types.INT),
            P('shader', Types.INT),
            P('contrast', Types.FLOAT),
            P('saturation', Types.FLOAT, default=0.5)
        )
        super().__init__()


class BloomSettings(BaseBinaryRepresentation):
    """
        Represents a set of bloom effect settings.
    """

    PRESETS = {
        'Default': (0.25, 4, 1.25, 1.0, 1.0, 1.0),
        'Soft': (0.0, 3.0, 1.0, 1.0, 1.0, 1.0),
        'Desaturated': (0.5, 8.0, 2.0, 1.0, 0.0, 1.0),
        'Saturated': (0.25, 4.0, 2.0, 1.0, 2.0, 0.0),
        'Blurry': (0.0, 2.0, 1.0, 0.1, 1.0, 1.0),
        'Subtle': (0.5, 2.0, 1.0, 1.0, 1.0, 1.0),
        'Subtler': (0.5, 1.75, 0.75, 1.0, 1.0, 1.0),
        'Menu': (0.5, 4.5, 0.75, 0.25, 0.25, 0.75),
        'Off': (0.0, 0.0, 0.0, 1.0, 1.0, 1.0),
        'SubtleD': (0.5, 1.15, 0.75, 1.0, 1.0, 0.65),
        'SoftLight': (0.0, 2.0, 0.5, 1.0, 1.0, 1.0),
        'SaturatedLight': (0.25, 1.15, 2.0, 1.0, 1.3, 0.0),
        'DesaturatedLight': (0.5, 0.5, 1.5, 1.0, 0.0, 1.0),
        'Intro': (0.5, 10.0, 1.0, 0.0, 0.0, 1.0),
        'Stinkweed': (0.0, 1.55, 1.0, 0.1, 1.5, 1.5),
        'StinkweedLight': (0.0, 1.25, 1.0, 0.1, 1.5, 1.5),
        'Dream': (0.45, 2.0, 2.0, 1.0, 1.5, 0.0),
        'DreamLight': (0.55, 2.0, 2.0, 1.0, 1.0, 0.0),
        'DreamExtraLight': (0.75, 2.0, 1.4, 1.0, 1.0, 0.0),
        'DreamSubtleLight': (0.35, 1.25, 1.25, 1.0, 1.25, 0.0),
        'DreamSubtle': (0.45, 1.25, 1.25, 1.0, 1.25, 0.0),
        'Cloudy': (0.5, 8.0, 1.375, 1.0, 0.0, 1.0),
        'RainBlurSlight': (0.0, 1.5, 1.0, 0.1, 1.0, 1.0),
        'ZiaMoment': (0.85, 1.4, 1.4, 1.0, 1.0, 1.0),
        'Memory_01': (0.4, 8.0, 1.0, 1.0, 0.0, 0.7),
        'Memory_02': (0.4, 8.0, 1.0, 1.0, 0.0, 0.6),
        'Memory_03': (0.4, 8.0, 1.0, 1.0, 0.0, 0.5),
        'Memory_04': (0.4, 8.0, 1.0, 1.0, 0.0, 0.4),
        'Memory_05': (0.4, 8.0, 1.0, 1.0, 0.0, 0.3),
        'Memory_06': (0.4, 8.0, 1.0, 1.0, 0.0, 0.2)
    }

    _properties = (
        P('name', Types.STRING, param=1, default='Off'),
        P('bloom_threshold', Types.FLOAT, default=PRESETS['Off'][0]),
        P('blur_amount', Types.FLOAT, default=PRESETS['Off'][1]),
        P('bloom_intensity', Types.FLOAT, default=PRESETS['Off'][2]),
        P('base_intensity', Types.FLOAT, default=PRESETS['Off'][3]),
        P('bloom_saturation', Types.FLOAT, default=PRESETS['Off'][4]),
        P('base_saturation', Types.FLOAT, default=PRESETS['Off'][5])
    )


class MapFile(BaseBinaryRepresentation):
    """
        Represents a Bastion map file.
    """

    ENDIAN = BinaryStream.LITTLE_ENDIAN
    VERSION = 0x20

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),

        P('spawn_points', SpawnPoint, repeat=Types.INT),
        P('starting_cash', Types.INT),
        P('name', Types.STRING, param=1),
        P('loot_table_name', Types.STRING, param=1),
        P('pathfinder_bonus', Types.FLOAT, default=1.0),
        P('scroll_speed', Types.FLOAT),
        P('scroll_angle', Types.FLOAT),
        P('size', Types.INT, repeat=2),
        P('music_name', Types.STRING, param=1),
        P('ambience_name', Types.STRING, param=1),

        P('terrain_layers', TerrainLayer, repeat=Types.INT),

        P('script', Types.STRING_LIST, param=1),

        P('backdrop_tiles', Types.STRING_LIST, param=1),
        P('backdrop_columns', Types.INT),
        P('backdrop_color', Types.COLOR),
        P('backdrop_flyers', Types.STRING_LIST),
        P('backdrop_flyer_interval_min', Types.FLOAT),
        P('backdrop_flyer_interval_max', Types.FLOAT),
        P('backdrop_flyer_speed_min', Types.FLOAT),
        P('backdrop_flyer_speed_max', Types.FLOAT),
        P('backdrop_flyer_color', Types.COLOR),

        P('full_black_time', Types.FLOAT, default=1.0),
        P('fade_in_time', Types.FLOAT, default=2.0),

        P('backdrop_flyer_refract_rate', Types.FLOAT),
        P('backdrop_flyer_refract_amount', Types.FLOAT),
        P('backdrop_rows', Types.INT),
        P('backdrop_tile_refract_rate', Types.FLOAT),
        P('backdrop_tile_refract_amount', Types.FLOAT),

        P('backdrop_preplaced_flyers', MapThing, repeat=Types.INT),

        P('background_bloom_setting', BloomSettings),
        P('terrain_bloom_setting', BloomSettings),

        P('backdrop_flyer_parallax', Types.FLOAT),

        P('tile_assemble_sound', Types.STRING, param=1, default='MapAssemble'),
        P('terrain_type', Types.STRING, param=1),
        P('unexplored_color', Types.COLOR),

        P('thing_groups', MapThingGroup, repeat=Types.INT),

        P('brightness', Types.FLOAT, default=0.5),
        P('player_start_fall', Types.BOOL),
        P('unexplored_contrast', Types.FLOAT, default=0.0),
        P('unexplored_saturation', Types.FLOAT, default=0.5),
        P('tile_phase_in_time_min', Types.FLOAT, default=0.5),
        P('tile_phase_in_time_max', Types.FLOAT, default=1.0),
        P('terrain_light_texture', Types.STRING, param=1),
        P('terrain_light_velocity', Types.VECTOR2),
        P('keep_weapons', Types.BOOL, default=True),
        P('can_plant_seeds', Types.BOOL, default=False),
        P('title_id', Types.STRING, param=1),
        P('no_weapons', Types.BOOL, default=False),
        P('parallax', Types.FLOAT, default=10.0),

        P('backdrop_saturation', Types.INT),

        # Map Editor settings.
        P('camera_location', Types.VECTOR2),
        P('camera_zoom', Types.FLOAT)
    )