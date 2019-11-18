class EntityStream:
    """Data structure for holding entity and stream information."""
    __slots__ = ['entity_id', 'stream_url']

    def __init__(self, entity_id, stream_url):
        self.entity_id = entity_id
        self.stream_url = stream_url
