from typing import Tuple, List

from edgetpu_server.utils import flatten


class ClassificationCoordinates:
    """Cartesian coordinates for a match."""

    def __init__(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
    ):
        """Initialize a new coordinate data structure."""
        self._coordinates = [
            (x1, y1),
            (x2, y2)
        ]

    @property
    def coordinates(self) -> List[Tuple[int, int]]:
        """Get the pair of coordinates that constitute this match."""
        return self._coordinates

    @property
    def coordinate_list(self) -> List[int]:
        """Get the coordinates as a flat array."""
        return flatten(self._coordinates)


class ClassificationLabel:
    """Label metadata."""

    def __init__(
            self,
            label: str,
            index: int,
    ):
        """Initialize a new label data structure."""
        self._label = label
        self._index = index

    @property
    def label(self) -> str:
        """The label."""
        return self._label

    @property
    def id(self) -> int:
        """The label identifier."""
        return self._index


class Classification:
    """Labeled match with bounding box."""

    def __init__(
            self,
            label: ClassificationLabel,
            coordinates: ClassificationCoordinates,
            score: int,

    ):
        """Initialize a new data structure."""
        self._label = label
        self._coordinates = coordinates
        self._score = score

    @property
    def label(self) -> str:
        """Get the label for this matched classification."""
        return self._label.label

    @property
    def label_id(self) -> int:
        """Get the label id for this matched classification."""
        return self._label.id

    @property
    def bounding_box(self) -> ClassificationCoordinates:
        """Get the coordinates of the matched classification."""
        return self._coordinates

    @property
    def confidence(self) -> int:
        """Get the confidence of the match."""
        return self._score
