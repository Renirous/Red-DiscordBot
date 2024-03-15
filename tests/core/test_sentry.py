from core import sentry_setup
import logging


def test_sentry_capture():
    log = logging.getLogger(__name__)
    sentry_setup.init_sentry_logging(log)

    assert sentry_setup.client is not None

    sentry_setup.client.captureMessage("Message from test_sentry module.")