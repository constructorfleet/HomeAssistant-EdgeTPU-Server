import logging
import queue

import requests

LOGGER = logging.getLogger(__name__)

ATTR_MATCHES = "matches"
ATTR_SUMMARY = "summary"
ATTR_TOTAL_MATCHES = "total_matches"
DOMAIN = "image_processing"
ENDPOINT_POST_STATE_TEMPLATE = "{}/api/states/{}"
HEADER_AUTH_KEY = "Authorization"
HEADER_AUTH_VALUE = "Bearer {}"
KEY_STATE = "state"
KEY_ATTRIBUTES = "attributes"


def slugify(name):
    return str(name).replace(" ", "_").replace("-", "_").lower()


def get_entity_id(name):
    return "{}.{}".format(DOMAIN, slugify(name))


class StateRequest:
    entity_id = None
    matches = {}
    total_matches = 0

    def __init__(self, name, matches, total_matches):
        self.entity_id = slugify(name)
        self.matches = matches
        self.total_matches = total_matches

    @property
    def attributes(self):
        return {
            ATTR_MATCHES: self.matches,
            ATTR_SUMMARY: {
                category: len(values) for category, values in self.matches.items()
            },
            ATTR_TOTAL_MATCHES: self.total_matches,
        }

    @property
    def body(self):
        return {
            KEY_STATE: self.total_matches,
            KEY_ATTRIBUTES: self.attributes
        }


class HomeAssistantApi:
    _url = None
    _token = None
    _queue = queue.Queue()

    def __init__(self, url, token):
        self._url = url
        self._token = token

    def add_request(self, name, matches, total_matches):
        self._queue.put(StateRequest(name, matches, total_matches))

    def run(self):
        while True:
            try:
                req = self._queue.get(timeout=5)
            except queue.Empty:
                continue

            if not req:
                continue

            try:
                self._perform_request(req)
            except requests.HTTPError:
                LOGGER.error("Error updating state for {}".format(req.entity_id))

    def _get_endpoint(self, entity_id):
        return ENDPOINT_POST_STATE_TEMPLATE.format(self._url, entity_id)

    def _get_auth_header(self):
        return HEADER_AUTH_VALUE.format(self._token)

    def _perform_request(self, state_request):
        response = requests.post(
            self._get_endpoint(state_request.entity_id),
            data=state_request,
            headers={
                HEADER_AUTH_KEY: self._get_auth_header()
            }
        )

        response.raise_for_status()
