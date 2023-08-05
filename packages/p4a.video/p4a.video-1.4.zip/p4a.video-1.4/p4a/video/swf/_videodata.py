from p4a.video import utils

def _safe(v):
    if isinstance(v, list) or isinstance(v, tuple):
        if len(v) >= 1:
            return v[0]
        else:
            return None
    return v

VIDEO_TYPE = u'Flash'

class SWFVideoDataAccessor(utils.AbstractDataAccessor):
    video_type = VIDEO_TYPE
