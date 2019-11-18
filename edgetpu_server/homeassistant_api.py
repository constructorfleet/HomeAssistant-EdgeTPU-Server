import requests
import logging

_LOGGER = logging.getLogger(__name__)

ENDPOINT_POST_STATE_TEMPLATE = "{}/api/states/{}"
HEADER_AUTH_KEY = "Authorization"
HEADER_AUTH_VALUE = "Bearer {}"
HEADER_CONTENT_TYPE_KEY = "Content-Type"
HEADER_CONTENT_TYPE_VALUE = "application/json"


class HomeAssistantApi:
    """Class to interact with Home-Assistant API."""

    def __init__(self, config):
        self._config = config

    def set_entity_state(self, detection_entity):
        """Call the Home-Assistant API set state service."""
        headers = {
            HEADER_AUTH_KEY: self._get_auth_header(),
            HEADER_CONTENT_TYPE_KEY: HEADER_CONTENT_TYPE_VALUE
        }
        _LOGGER.info("Payload: %s",
                     detection_entity.as_api_payload)
        response = requests.post(
            self._get_endpoint(detection_entity.entity_id),
            json=detection_entity.as_api_payload(),
            headers=headers,
            timeout=1.0
        )

        response.raise_for_status()

    def _get_endpoint(self, entity_id):
        return ENDPOINT_POST_STATE_TEMPLATE.format(
            self._config.url,
            entity_id
        )

    def _get_auth_header(self):
        return HEADER_AUTH_VALUE.format(self._config.token)
