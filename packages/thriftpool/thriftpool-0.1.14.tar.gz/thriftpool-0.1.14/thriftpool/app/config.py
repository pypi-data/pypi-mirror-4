from __future__ import absolute_import

import logging

from thriftpool.utils.structures import AggregatedView

__all__ = ['Configuration']

DEFAULT_SETTINGS = dict(
    DEBUG=True,
    DEFAULT_LOG_FMT="[%(asctime)s %(levelname)s] %(message)s",
    LOGGING_LEVEL=logging.DEBUG,
    LOG_REQUESTS=False,
    LOG_FILE=None,
    LOG_FORCE_COLORIZED=False,
    REDIRECT_STDOUT=True,
    SLOTS=[],
    PROCESS_NAME='thriftpool',
    MODULES=[],
    PROTOCOL_FACTORY_CLS='thrift.protocol.TBinaryProtocol'
                         ':TBinaryProtocolAcceleratedFactory',
    SERVICE_PORT_RANGE=(10000, 20000),
    WORKER_TYPE='sync',
    WORKERS=1,
    CONCURRENCY=1,
)


class Configuration(AggregatedView):
    """Default application configuration."""

    def __init__(self, config):
        super(Configuration, self).__init__(config)
        self.add_default(DEFAULT_SETTINGS)
