import os
from flask import Flask, jsonify
from flask_cors import CORS
from api import get_account

# create app instance
app = Flask(__name__)

# enable cors headers
CORS(app)

# main route for accessing account information
@app.route('/account/<account_num>')
def account(account_num):
    event = {
        'pathParameters': {
            'account_num': account_num,
        },
    }
    r = get_account(event, None)

    return jsonify(r)
