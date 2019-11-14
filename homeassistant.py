import json
import logging
import queue
import time

import requests

LOGGER = logging.getLogger(__name__)

ATTR_MATCHES = "matches"
ATTR_SUMMARY = "summary"
ATTR_TOTAL_MATCHES = "total_matches"
DOMAIN = "image_processing"
ENDPOINT_POST_STATE_TEMPLATE = "{}/api/states/{}"
HEADER_AUTH_KEY = "Authorization"
HEADER_AUTH_VALUE = "Bearer {}"
HEADER_CONTENT_TYPE_KEY = "Content-Type"
HEADER_CONTENT_TYPE_VALUE = "application/json"
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

    def __eq__(self, other):
        if isinstance(other, StateRequest):
            return self.entity_id == other.entity_id \
                    and json.dumps(self.attributes) == json.dumps(other.attributes)
        return False

    def __hash__(self):
        return hash("%s%s" % (self.entity_id, json.dumps(self.attributes)))


class HomeAssistantApi:
    _url = None
    _token = None
    _queue = queue.Queue()
    _last_request = None

    def __init__(self, url, token):
        self._url = url
        self._token = token

    def add_request(self, name, matches, total_matches):
        req = StateRequest(name, matches, total_matches)
        if self._last_request == req:
            return
        self._queue.put(req)

    def run(self):
        while True:
            try:
                req = self._queue.get(timeout=5)
            except queue.Empty:
                time.sleep(0.5)
                continue

            if not req:
                time.sleep(0.5)
                continue

            try:
                self._perform_request(req)
            except requests.HTTPError as e:
                print("Error updating state for {} {}".format(req.entity_id, e))

    def _get_endpoint(self, entity_id):
        return ENDPOINT_POST_STATE_TEMPLATE.format(self._url, entity_id)

    def _get_auth_header(self):
        return HEADER_AUTH_VALUE.format(self._token)

    def _perform_request(self, state_request):
        headers = {
            HEADER_AUTH_KEY: self._get_auth_header(),
            HEADER_CONTENT_TYPE_KEY: HEADER_CONTENT_TYPE_VALUE
        }
        # print("Endpoint %s" % self._get_endpoint(state_request.entity_id))
        # print("Headers %s" % str(headers))
        # print("Body %s" % json.dumps(state_request.body))
        response = requests.post(
            self._get_endpoint(state_request.entity_id),
            json=state_request.body,
            headers=headers
        )

        print("Response %s" % str(response.text))

        response.raise_for_status()
