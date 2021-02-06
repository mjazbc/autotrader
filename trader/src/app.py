#!/usr/bin/env python
# encoding: utf-8
import json
from os import abort
from trader.src.trader_config import TraderConfig
from auto_trader import Trader
from trader_manager import TraderManager
from flask import Flask, request, jsonify
import db


app = Flask(__name__)

@app.route('/trader/<name>', methods=['POST'])
def create_bot(name):
    bot = json.loads(request.data)

    if db.load_trader_config(name):
        raise Exception('Trader with name %s already exists.'.format(name))
    
    config = TraderConfig(name, bot['wallet'], min_price_change = bot['strategy']['params']['price_change'])
    db.insert_trader_config(config, bot['owner_id'])

    t = Trader(config)
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

@app.route('/user/', methods=['POST'])
def create_user():
    user_data = json.loads(request.data)
    user_id = db.find_user(user_data['chat_id'])
    if not user_id:
        user_id = db.create_user(user_data['chat_id'])
    return jsonify({'id' : user_id, 'chat_id' : user_data['chat_id']})

tm = TraderManager()

tm.run_all()
app.run(host='0.0.0.0')