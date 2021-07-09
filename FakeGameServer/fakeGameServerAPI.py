from flask import Flask, json

api = Flask(__name__)

@api.route("/flags", methods=['PUT'])

def post_flag():
    print("Flag received")
    return json.dumps({"Success": True}), 200

if __name__ == '__main__':
    api.run()