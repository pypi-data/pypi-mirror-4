from p4a.video import utils
from p4a.fileimage import utils as fileutils

def write_video_image(id3tags, video_image):
    size = video_image.get_size()
    mime_type = video_image.content_type
    desc = u''

    tempfilename = fileutils.write_to_tempfile(video_image)
    frame = frames.ImageFrame.create(frames.ImageFrame.FRONT_COVER, 
                                     tempfilename,
                                     desc)

    imgs = id3tags.getImages()
    if len(imgs) == 0:
        id3tags.frames.append(frame)
    else:
        # find the frame index of the first image so we can
        # replace it with our new image frame
        for i in id3tags.frames:
            if i == imgs[0]:
                index = id3tags.frames.index(i)
                id3tags.frames[index] = frame
                break

VIDEO_TYPE = u'Windows Video (wmv)'

class WMVVideoDataAccessor(utils.AbstractDataAccessor):
    video_type = VIDEO_TYPE
