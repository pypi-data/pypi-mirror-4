from __future__ import absolute_import, unicode_literals

import anyjson
import requests

from thebot import Plugin, on_command


class Plugin(Plugin):
    @on_command('translate (?P<some_text>.+)')
    @on_command('translate (?P<some_text>.+) (?P<from_to>..-..)')
    def translate(self, request, some_text, from_to='en-ru'):
        """Translates given text from one language to another."""

        if from_to not in self.get_directions():
            request.respond(u'Supported translation directions are: ' + u', '.join(
                sorted(list(self.get_directions()))
            ))
            return

        response = requests.get(
            'http://translate.yandex.net/api/v1/tr.json/translate',
            params=dict(
                lang=from_to,
                text=some_text,
            )
        )
        if response.status_code == 200:
            data = anyjson.deserialize(response.content)
            request.respond(u'\n'.join(data['text']))
        else:
            request.respond('Bad response from the server: {}, {}'.format(
                response.status_code,
                response.content
            ))

    def get_directions(self):
        if not hasattr(self, '_directions'):
            response = requests.get('http://translate.yandex.net/api/v1/tr.json/getLangs')
            data = anyjson.deserialize(response.content)
            self._directions = set(data['dirs'])

        return self._directions

