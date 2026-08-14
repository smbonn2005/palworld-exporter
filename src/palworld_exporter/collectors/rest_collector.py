import logging
from typing import Iterable

import requests
from prometheus_client.metrics_core import (GaugeMetricFamily,
                                            InfoMetricFamily, Metric)
from prometheus_client.registry import Collector

from palworld_exporter.providers.rest import (MetricsProvider, PlayersProvider,
                                              RESTContext, ServerInfoProvider)


class RESTCollector(Collector):
    def __init__(self, rest_ctx: RESTContext):
        self._server_info_provider = ServerInfoProvider(rest_ctx)
        self._players_provider = PlayersProvider(rest_ctx)
        self._metrics_provider = MetricsProvider(rest_ctx)

    def collect(self) -> Iterable[Metric]:
        result = []
        success = False

        try:
            info = self._server_info_provider.fetch()
            info_metric = InfoMetricFamily('palworld_server', 'Palworld server information', value={
                                           'version': info.version, 'name': info.name})
            result.append(info_metric)

            players = self._players_provider.fetch()
            player_count_metric = GaugeMetricFamily(
                'palworld_player_count', 'Current player count', len(players))
            result.append(player_count_metric)

            players_metric = GaugeMetricFamily('palworld_player', 'Palworld player information', labels=[
                                               'name', 'user_id', 'player_uid'])
            for player in players:
                players_metric.add_metric(
                    labels=[player.name, player.user_id, player.player_uid], value=1)
            result.append(players_metric)

            metrics = self._metrics_provider.fetch()
            result.append(GaugeMetricFamily(
                'palworld_server_fps', 'Current server FPS', metrics.server_fps))
            result.append(GaugeMetricFamily(
                'palworld_server_frametime_milliseconds', 'Current server frame time in milliseconds', metrics.server_frame_time_ms))
            result.append(GaugeMetricFamily(
                'palworld_uptime_seconds', 'Server uptime in seconds since last restart', metrics.uptime_seconds))
            result.append(GaugeMetricFamily(
                'palworld_world_days', 'Elapsed in-game days', metrics.days))
            result.append(GaugeMetricFamily(
                'palworld_player_max', 'Maximum player capacity configured on the server', metrics.max_player_num))

            # We made it through the whole scrape
            success = True
        except requests.exceptions.ConnectionError:
            logging.warning("Error connecting to REST API")
        except requests.exceptions.HTTPError as e:
            logging.error(e)
        except Exception as e:
            logging.exception(e)

        up_metric = GaugeMetricFamily(
            'palworld_up', 'Was the last scrape of the REST API successful', int(success))
        result.append(up_metric)
        return result
