import requests

from edgetpu_server import HomeAssistantConfig
from edgetpu_server.services import Service
from edgetpu_server.services.signals.frame_processed import FrameProcessedSignal

ENDPOINT_POST_STATE_TEMPLATE = "{}/api/states/{}"
HEADER_AUTH_KEY = "Authorization"
HEADER_AUTH_VALUE = "Bearer {}"
HEADER_CONTENT_TYPE_KEY = "Content-Type"
HEADER_CONTENT_TYPE_VALUE = "application/json"


class StatePublishService(Service):
    """Service to publish entity state changes."""

    def __init__(
            self,
            name: str,
            home_assistant_config: HomeAssistantConfig,
            processed_signal: FrameProcessedSignal,
    ):
        """Initialize a new instance of this service."""
        super().__init__(name)
        self._base_url = home_assistant_config.url
        self._headers = {
            HEADER_AUTH_KEY: HEADER_AUTH_VALUE.format(home_assistant_config.token),
            HEADER_CONTENT_TYPE_KEY: HEADER_CONTENT_TYPE_VALUE,
        }
        self._processed_signal = processed_signal

    def run(self):
        """Service entrypoint."""
        while True:
            try:
                result = self._processed_signal.receive_results()
                endpoint = ENDPOINT_POST_STATE_TEMPLATE.format(
                    self._base_url,
                    result.entity_id
                )
                response = requests.post(
                    endpoint,
                    json=result,
                    headers=self._headers,
                    timeout=1.0
                )

                response.raise_for_status()
            except Exception:
                # TODO : He's dead Jim
                return
