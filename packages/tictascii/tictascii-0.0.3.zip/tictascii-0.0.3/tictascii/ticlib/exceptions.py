class IllegalMarker(Exception):
    pass


class MarkerExists(IllegalMarker):
    pass


class MarkerOutOfRange(IllegalMarker):
    pass
