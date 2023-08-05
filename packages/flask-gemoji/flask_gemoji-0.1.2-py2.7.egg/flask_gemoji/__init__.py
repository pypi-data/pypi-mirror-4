import os
import pkg_resources

from flask import Blueprint, url_for


class Gemoji(object):

    @classmethod
    def init_app(self, app):
        app.config.setdefault('GEMOJI_CLASS', 'gemoji')
        gemoji_images_path = (pkg_resources
            .resource_filename(__package__, 'static/images/emoji'))
        names = map(lambda s: os.path.splitext(s)[0],
                    filter(lambda s: s.endswith('.png'),
                           os.listdir(gemoji_images_path)))

        gemoji = Blueprint('gemoji', __name__, static_folder='static')
        app.register_blueprint(gemoji, url_prefix='/gemoji')

        @app.template_filter('gemoji')
        def gemoji_filter(s, height='auto'):
            splits = s.split(':')
            splits_len = len(splits)
            out = ''
            for i, w in enumerate(splits):
                if w in names:
                    out = out[:-1]
                    out += '<img src="%s" alt="%s" class="%s" height="%s">' % (
                        url_for('gemoji.static',
                                filename='images/emoji/%s.png' % w),
                        w,
                        app.config['GEMOJI_CLASS'],
                        height,
                    )
                elif i + 1 < splits_len:
                    out += w + ':'
                else:
                    out += w

            return out
