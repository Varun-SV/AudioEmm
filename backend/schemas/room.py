from __future__ import annotations
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


SurfaceName = Literal["floor", "ceiling", "wall_front", "wall_back", "wall_left", "wall_right"]
MaterialName = Literal["drywall", "hardwood", "carpet", "curtain", "concrete", "glass"]


class SurfaceMaterial(BaseModel):
    surface: SurfaceName
    material: MaterialName


class Speaker(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    x: float = Field(ge=0.0)
    y: float = Field(ge=0.0)
    z: float = Field(ge=0.0)
    label: str = "Speaker"


class Listener(BaseModel):
    x: float = Field(ge=0.0)
    y: float = Field(ge=0.0)
    z: float = Field(ge=0.0)


RoomObjectType = Literal[
    "curtain", "window", "door", "sofa", "bookshelf", "desk"
]


class RoomObjectConfig(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    type: RoomObjectType
    wall_surface: SurfaceName
    pos_u: float = Field(default=0.5, ge=0.0, le=1.0)
    pos_v: float = Field(default=0.5, ge=0.0, le=1.0)
    width: float = Field(default=1.0, ge=0.1, le=10.0)
    height: float = Field(default=1.5, ge=0.1, le=10.0)


class RoomConfig(BaseModel):
    length: float = Field(default=5.0, ge=1.0, le=30.0)
    width: float = Field(default=4.0, ge=1.0, le=30.0)
    height: float = Field(default=3.0, ge=1.5, le=10.0)
    surfaces: list[SurfaceMaterial] = Field(default_factory=list)
    speakers: list[Speaker] = Field(default_factory=list)
    listener: Listener = Field(default_factory=lambda: Listener(x=2.5, y=2.0, z=1.2))
    rt60_preview: float | None = None
    room_objects: list[RoomObjectConfig] = Field(default_factory=list)


ROOM_PRESETS: dict[str, dict] = {
    "living_room": {
        "length": 5.0, "width": 4.0, "height": 3.0,
        "surfaces": [
            {"surface": "floor", "material": "hardwood"},
            {"surface": "ceiling", "material": "drywall"},
            {"surface": "wall_front", "material": "drywall"},
            {"surface": "wall_back", "material": "drywall"},
            {"surface": "wall_left", "material": "drywall"},
            {"surface": "wall_right", "material": "drywall"},
        ],
        "speakers": [{"id": "sp1", "x": 1.0, "y": 2.0, "z": 1.0, "label": "Speaker L"},
                     {"id": "sp2", "x": 4.0, "y": 2.0, "z": 1.0, "label": "Speaker R"}],
        "listener": {"x": 2.5, "y": 1.0, "z": 1.2},
    },
    "bedroom": {
        "length": 4.0, "width": 3.5, "height": 2.8,
        "surfaces": [
            {"surface": "floor", "material": "carpet"},
            {"surface": "ceiling", "material": "drywall"},
            {"surface": "wall_front", "material": "drywall"},
            {"surface": "wall_back", "material": "drywall"},
            {"surface": "wall_left", "material": "curtain"},
            {"surface": "wall_right", "material": "drywall"},
        ],
        "speakers": [{"id": "sp1", "x": 0.5, "y": 1.75, "z": 1.0, "label": "Speaker"}],
        "listener": {"x": 2.0, "y": 1.75, "z": 1.2},
    },
    "office": {
        "length": 4.0, "width": 3.0, "height": 2.8,
        "surfaces": [
            {"surface": "floor", "material": "concrete"},
            {"surface": "ceiling", "material": "drywall"},
            {"surface": "wall_front", "material": "drywall"},
            {"surface": "wall_back", "material": "drywall"},
            {"surface": "wall_left", "material": "glass"},
            {"surface": "wall_right", "material": "drywall"},
        ],
        "speakers": [{"id": "sp1", "x": 1.0, "y": 1.5, "z": 0.8, "label": "Monitor L"},
                     {"id": "sp2", "x": 3.0, "y": 1.5, "z": 0.8, "label": "Monitor R"}],
        "listener": {"x": 2.0, "y": 1.5, "z": 1.2},
    },
    "studio": {
        "length": 6.0, "width": 5.0, "height": 3.5,
        "surfaces": [
            {"surface": "floor", "material": "concrete"},
            {"surface": "ceiling", "material": "curtain"},
            {"surface": "wall_front", "material": "curtain"},
            {"surface": "wall_back", "material": "curtain"},
            {"surface": "wall_left", "material": "curtain"},
            {"surface": "wall_right", "material": "curtain"},
        ],
        "speakers": [{"id": "sp1", "x": 1.5, "y": 2.5, "z": 1.2, "label": "Monitor L"},
                     {"id": "sp2", "x": 4.5, "y": 2.5, "z": 1.2, "label": "Monitor R"}],
        "listener": {"x": 3.0, "y": 1.5, "z": 1.2},
    },
}
