import logging
import os

from pygain_lib.util import core as core_util
from pygain_lib.core import constants as core_constants
from pygain_lib.core.config import reload_config


def init():
    log_level = logging.INFO
    logging.getLogger().setLevel(log_level)

    os.environ["GAIN_APP_ROOT_PATH"] = os.path.dirname(os.path.realpath(__file__))
    # Reloading the config to guard against out of order execution issues
    reload_config()

    if core_util.env() == core_constants.ENV_PROD:
        # logging for stackdriver
        # import google.cloud.logging
        #
        # client = google.cloud.logging.Client()
        # client.setup_logging(log_level=log_level)

        try:
            if os.environ.get("DD_SERVICE"):
                gae_version = os.environ.get("GAE_VERSION", "unknown")
                os.environ["DD_VERSION"] = gae_version
                from ddtrace import patch_all, tracer, filters

                patch_all()
                # logging.getLogger('ddtrace.tracer').setLevel(logging.DEBUG)
                # logging.getLogger('ddtrace.profiling.profiler').setLevel(logging.DEBUG)
                tracer.configure(
                    settings={
                        "FILTERS": [
                            filters.FilterRequestsOnUrl(
                                [r"https?://[0-9a-z-\\.]+/$", r"https?://[0-9a-z-\\.]+/_ah/.*"]
                            ),
                        ],
                    },
                )
                # this import turns on datadog profiling
                import ddtrace.profiling.auto  # noqa
        except Exception as e:
            logging.exception("error starting ddtrace")
            logging.exception(e)
