from django.forms import Textarea

class FullScreenTextarea(Textarea):

    def __init__(self, attrs=None):
        default_attrs = {'class': 'fullscreen'}
        if attrs is None:
            attrs = default_attrs 
        attrs.update(default_attrs)
        super(FullScreenTextarea, self).__init__(attrs)

    class Media:
        css = {
            'screen': (
                'https://fonts.googleapis.com/css?family=Lato',
                'writingfield/writingfield.css',)
        }
        js = (
            'writingfield/mousetrap.min.js',
            'writingfield/writingfield.js',
        )
