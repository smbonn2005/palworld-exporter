from dataclasses import dataclass


@dataclass
class Player:
    name: str
    player_uid: str
    user_id: str


@dataclass
class ServerInfo:
    name: str
    version: str


@dataclass
class SaveInformation:
    filename: str
    file_size: int
    last_modified: int


@dataclass
class ServerMetrics:
    server_fps: int
    current_player_num: int
    server_frame_time_ms: float
    max_player_num: int
    uptime_seconds: int
    days: int
