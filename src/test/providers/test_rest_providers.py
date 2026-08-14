from unittest.mock import patch

from palworld_exporter.providers.rest import (MetricsProvider, PlayersProvider,
                                              RESTContext, ServerInfoProvider)


def fake_ctx():
    return RESTContext('localhost', 8212, 'topsecret')


@patch('palworld_exporter.providers.rest.PlayersProvider._cmd_players')
def test_PlayersProvider(mock_players):
    mock_players.return_value = {'players': [
        {'name': 'Mr Rogers', 'playerId': '3C291D4D000000000000000000000000',
         'userId': 'steam_987654321'},
    ]}
    pp = PlayersProvider(fake_ctx())
    players = pp.fetch()
    assert len(players) == 1
    assert players[0].name == 'Mr Rogers'
    assert players[0].player_uid == '1009327437'
    assert players[0].user_id == 'steam_987654321'


@patch('palworld_exporter.providers.rest.PlayersProvider._cmd_players')
def test_PlayersProvider_NoPlayers(mock_players):
    mock_players.return_value = {'players': []}
    pp = PlayersProvider(fake_ctx())
    players = pp.fetch()
    assert len(players) == 0


@patch('palworld_exporter.providers.rest.PlayersProvider._cmd_players')
def test_PlayersProvider_Korean(mock_players):
    # I don't know Korean :( I'm sorry if this is stupid
    name = '트리나'
    mock_players.return_value = {'players': [
        {'name': name, 'playerId': 'FBB2E40C000000000000000000000000',
         'userId': 'steam_123456789'},
    ]}
    pp = PlayersProvider(fake_ctx())
    players = pp.fetch()
    assert len(players) == 1
    assert name == players[0].name


@patch('palworld_exporter.providers.rest.ServerInfoProvider._cmd_info')
def test_ServerInfoProvider(mock_info):
    mock_info.return_value = {
        'version': 'v0.1.4.0',
        'servername': 'http://palworld.lol 1 | OPEN 24/7 Dedicated',
        'description': '',
        'worldguid': 'A7E97BAA767DB9029EF013BB71E993A0',
    }
    sip = ServerInfoProvider(fake_ctx())
    serverInfo = sip.fetch()
    assert serverInfo.version == 'v0.1.4.0'
    assert serverInfo.name == 'http://palworld.lol 1 | OPEN 24/7 Dedicated'


@patch('palworld_exporter.providers.rest.MetricsProvider._cmd_metrics')
def test_MetricsProvider(mock_metrics):
    mock_metrics.return_value = {
        'serverfps': 57,
        'currentplayernum': 10,
        'serverframetime': 16.7671,
        'maxplayernum': 32,
        'uptime': 3600,
        'days': 1,
    }
    mp = MetricsProvider(fake_ctx())
    metrics = mp.fetch()
    assert metrics.server_fps == 57
    assert metrics.current_player_num == 10
    assert metrics.server_frame_time_ms == 16.7671
    assert metrics.max_player_num == 32
    assert metrics.uptime_seconds == 3600
    assert metrics.days == 1
