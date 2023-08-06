from Products.Five import BrowserView


class ThumbnailImageView(BrowserView):

    def __call__(self):
        field = self.context.getField('thumbnailImage')
        return field.download(self.context)