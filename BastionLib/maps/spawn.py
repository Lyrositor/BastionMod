# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from ..binary_file import BaseBinaryRepresentation, BinaryProperty, Types

P = BinaryProperty


class Spawn(BaseBinaryRepresentation):
    """
        Represents a spawn entry.
    """

    VERSION = 2

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),
        P('name', Types.STRING, param=1),
        P('num', Types.INT, default=1),
        P('max_attempts', Types.INT, default=100)
    )


class SpawnWave(BaseBinaryRepresentation):
    """
        Represents one map spawn wave.
    """

    VERSION = 2

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),
        P('min_interval', Types.FLOAT, default=1.0),
        P('max_interval', Types.FLOAT, default=1.0),
        P('spawns', Spawn, repeat=Types.INT),
        P('loop_to_wave', Types.INT),
        P('repeat_times', Types.INT),
        P('scale_count_scalar', Types.FLOAT, default=1.0),
        P('scale_interval_scalar', Types.FLOAT, default=1.0),
        P('first_spawn_min_interval', Types.FLOAT, default=-1.0),
        P('first_spawn_max_interval', Types.FLOAT, default=-1.0)
    )


class SpawnPoint(BaseBinaryRepresentation):
    """
        Represents a map's spawn point.
    """

    VERSION = 2

    _properties = (
        P('version', Types.INT, default=VERSION, equals=VERSION),
        P('name', Types.STRING, param=1),
        P('x_offset_min', Types.INT, default=-100),
        P('x_offset_max', Types.INT, default=100),
        P('y_offset_min', Types.INT, default=-100),
        P('y_offset_max', Types.INT, default=100),
        P('spawn_waves', SpawnWave, repeat=Types.INT),
        P('snap_horizontal', Types.BOOL, default=False),
        P('snap_vertical', Types.BOOL, default=False)
    )