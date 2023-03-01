from flask import Flask, request, render_template
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound
from handler import TrainInfoHandler
from datetime import datetime

app = Flask(__name__)
train_info_handler = TrainInfoHandler()


@app.route("/get_all_train_data")
def get_all_train_data():
    table = {
        uuid: train_info_handler.get_train_data(uuid)
        for uuid in train_info_handler.get_all_train_uuids()
    }

    return table, 200


@app.route("/store_train_data")
def store_train_data():
    datetime_string = request.args.get("datetime", type=str)
    destination = request.args.get("destination", type=str)
    platform = request.args.get("platform", type=int)
    expected = request.args.get("expected", type=int)

    if datetime_string is None \
            or destination is None \
            or platform is None \
            or expected is None:
        raise BadRequest()

    uuid = train_info_handler.new_train_data(
        datetime.fromisoformat(datetime_string),
        destination,
        platform,
        expected
    )

    return {"uuid": uuid}, 200


@app.route("/")
def home_page():
    return render_template("index.html"), 200


@app.errorhandler(BadRequest)
def handle_bad_request(_e):
    return {"error": "Bad request"}, 400


@app.errorhandler(InternalServerError)
def handle_bad_request(_e):
    return {"error": "Internal server error"}, 500

if __name__ == "__main__":
    app.run(threaded=True)
