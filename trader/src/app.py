#!/usr/bin/env python
# encoding: utf-8
import json
from auto_trader import Trader
from trader_manager import TraderManager
from flask import Flask, request, jsonify


app = Flask(__name__)
@app.route('/')
def index():
    return json.dumps({'name': 'alice',
                       'email': 'alice@outlook.com'})

@app.route('/trader/<name>', methods=['POST'])
def create_bot(name):
    bot = json.loads(request.data)

    #TODO check if bot with same name already exists

    t = Trader(wallet = bot['wallet'], min_price_change = bot['strategy']['params']['price_change'], name=name)
    tm.add_trader(t, auto_start=True)
    
    return jsonify(bot)

@app.route('/trader/<name>', methods=['GET'])
def get_bot(name):
    tm._bots[name]
    return jsonify(tm._bots[name])

@app.route('/trader/<name>/wallet', methods=['GET'])
def get_bot_wallet(name):
    bot = tm._bots[name]
    w = {key: value for (key, value) in zip(bot.tokens, bot.values)}
    return jsonify(w)


tm = TraderManager()

tm.run()
app.run(host='0.0.0.0')