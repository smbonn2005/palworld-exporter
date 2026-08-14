import logging
from threading import Event

import click
from click_loglevel import LogLevel
from prometheus_client import (GC_COLLECTOR, PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR, REGISTRY, start_http_server)

from palworld_exporter.collectors.rest_collector import RESTCollector
from palworld_exporter.collectors.save_meta_collector import SaveFileCollector
from palworld_exporter.collectors.util import find_save_directory
from palworld_exporter.providers.rest import RESTContext

# Unregister default/built-in Python collectors
# https://prometheus.github.io/client_python/collector/#disabling-default-collector-metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)


@click.command()
@click.option('--rest-host', default='localhost', help='Palworld REST API hostname or IP address', show_default=True, envvar='REST_HOST')
@click.option('--rest-port', default=8212, help='Palworld REST API port', show_default=True, envvar='REST_PORT', type=int)
@click.option('--rest-password', default='', help='Palworld REST API password (the server AdminPassword)', show_default='None', envvar='REST_PASSWORD')
@click.option('--rest-use-tls', is_flag=True, default=False, envvar='REST_USE_TLS', help='Use HTTPS when connecting to the REST API')
@click.option('--listen-address', default='0.0.0.0', help='Hostname or IP Address for exporter to listen on', envvar='LISTEN_ADDRESS', show_default=True)
@click.option('--listen-port', default=9877, help='Port for exporter to listen on', show_default=True, envvar='LISTEN_PORT', type=int)
@click.option('--save-directory', default=None, envvar='SAVE_DIRECTORY', help='Path to directory contain all .sav files (e.g. Pal/Saved/SaveGames)', show_default='None', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--log-level', type=LogLevel(), default='INFO', help='Set logging level', envvar='LOG_LEVEL', show_default=True)
@click.option('--version', is_flag=True, default=False, help='Print version of palworld-exporter and exit')
def main(rest_host: str,
         rest_port: int,
         rest_password: str,
         rest_use_tls: bool,
         listen_address: str,
         listen_port: int,
         save_directory: str,
         log_level: int,
         version: bool):

    if version:
        from palworld_exporter import __version__
        click.echo(__version__)
        return

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=log_level)

    # Register all the collectors
    if save_directory:
        try:
            actual_save_dir = find_save_directory(save_directory)
            REGISTRY.register(SaveFileCollector(actual_save_dir))
        except Exception as e:
            logging.error(e)
            return

    rest_ctx = RESTContext(rest_host, rest_port, rest_password, use_tls=rest_use_tls)
    REGISTRY.register(RESTCollector(rest_ctx))
    start_http_server(port=listen_port, addr=listen_address)

    logging.info(f'Listening on {listen_address}:{listen_port}')
    # Wait forever
    Event().wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting...")
