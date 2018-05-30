import os
import datetime
from flask import Flask, jsonify
from flask.json import JSONEncoder
from flask_cors import CORS
from api import get_account

# create app instance
app = Flask(__name__)

# enable cors headers
CORS(app)

# custom json encoder that converts datetime objects to iso 8601-compliant
# strings
class DatetimeJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
            return super().default(o)

app.json_encoder = DatetimeJsonEncoder

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
