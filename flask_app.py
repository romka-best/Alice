import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'current': 'слон'
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    session = sessionStorage[user_id]

    CORRECT_ANSWERS = ['ладно',
                       'куплю',
                       'покупаю',
                       'хорошо']
    for answer in CORRECT_ANSWERS:
        if answer in req['request']['original_utterance'].lower():
            if session['current'] == 'слон':
                res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!\n' \
                                          'А теперь купи кролика!'
                sessionStorage[user_id] = session
            else:
                res['response']['text'] = 'Кролика можно найти также на Яндекс.Маркете!'
                res['response']['end_session'] = True
            return

    if session['current'] == 'слон':
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    else:
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        cur = 'слон' if session['current'] == 'слон' else 'кролик'
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={cur}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
