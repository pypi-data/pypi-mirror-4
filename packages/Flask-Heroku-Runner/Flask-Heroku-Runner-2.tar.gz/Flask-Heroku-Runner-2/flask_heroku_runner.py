import os
import flask


class HerokuApp(flask.Flask):
    def run(self, *positional, **keywords):
        if 'PORT' in os.environ:
            keywords.setdefault('port', int(os.environ['PORT']))
        if 'HOST' in os.environ:
            keywords.setdefault('host', os.environ['HOST'])
        if 'DEBUG' in os.environ:
            val = str(os.environ['DEBUG']).lower()
            if val in ('yes', 'true', '1'):
                keywords.setdefault('debug', True)
            elif val in ('no', 'false', '0'):
                keywords.setdefault('debug', False)
        super(HerokuApp, self).run(*positional, **keywords)
