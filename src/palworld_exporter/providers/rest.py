from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

import requests

from palworld_exporter.providers.data import Player, ServerInfo, ServerMetrics
from palworld_exporter.providers.util import hex_uid_to_decimal


class RESTContext:
    """
    Holds connection details for the Palworld REST API and reuses a single
    requests.Session (HTTP Basic Auth, username is always "admin") across calls.

    Unlike RCONContext, this isn't a context manager: HTTP is stateless per
    request, so there's no connect/close handshake to wrap - the session just
    gives us connection pooling.

    For example:

    myctx = RESTContext('localhost', 8212, 'topsecret')
    myctx.get('/v1/api/metrics')
    """

    def __init__(self, host, port, password, timeout=10, use_tls=False):
        scheme = 'https' if use_tls else 'http'
        self._base_url = f'{scheme}://{host}:{port}'
        self._timeout = timeout
        self._session = requests.Session()
        self._session.auth = ('admin', password)

    def get(self, path: str) -> dict:
        resp = self._session.get(
            f'{self._base_url}{path}', timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()


T = TypeVar('T')


class RESTProvider(ABC, Generic[T]):
    @abstractmethod
    def fetch(self) -> T:
        raise NotImplementedError


class ServerInfoProvider(RESTProvider[ServerInfo]):
    """
    Get Server information including name and version.
    """

    def __init__(self, rest_ctx: RESTContext):
        self._rest_ctx = rest_ctx

    def _cmd_info(self) -> dict:
        return self._rest_ctx.get('/v1/api/info')

    def fetch(self) -> ServerInfo:
        data = self._cmd_info()
        return ServerInfo(name=data['servername'], version=data['version'])


class PlayersProvider(RESTProvider[List[Player]]):
    """
    Get active Player information.
    """

    def __init__(self, rest_ctx: RESTContext):
        self._rest_ctx = rest_ctx

    def _cmd_players(self) -> dict:
        return self._rest_ctx.get('/v1/api/players')

    def fetch(self) -> List[Player]:
        data = self._cmd_players()
        players = []
        for p in data.get('players', []):
            players.append(Player(
                name=p['name'],
                player_uid=hex_uid_to_decimal(p['playerId']),
                user_id=p['userId'],
            ))
        return players


class MetricsProvider(RESTProvider[ServerMetrics]):
    """
    Get live server performance metrics: FPS, frame time, uptime, in-game days.
    """

    def __init__(self, rest_ctx: RESTContext):
        self._rest_ctx = rest_ctx

    def _cmd_metrics(self) -> dict:
        return self._rest_ctx.get('/v1/api/metrics')

    def fetch(self) -> ServerMetrics:
        data = self._cmd_metrics()
        return ServerMetrics(
            server_fps=data['serverfps'],
            current_player_num=data['currentplayernum'],
            server_frame_time_ms=data['serverframetime'],
            max_player_num=data['maxplayernum'],
            uptime_seconds=data['uptime'],
            days=data['days'],
        )
