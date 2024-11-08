from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(data=None, isRead=True)


if __name__ == "__main__":
    # app.run(port=8888)

    a = ['a', 'b', 'c', 'd', 'e']
    for ind, alf in enumerate(reversed(a)):
        print(len(a)-ind, alf)
