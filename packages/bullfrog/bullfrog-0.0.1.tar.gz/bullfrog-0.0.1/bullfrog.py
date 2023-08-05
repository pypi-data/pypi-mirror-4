from flask import Flask
from werkzeug.routing import BaseConverter

app = Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route(r'/<regex(".*?"):path>')
def ribbet(path):
    return 'Ok'


def run():
    app.run

if __name__ == '__main__':
    app.run()
