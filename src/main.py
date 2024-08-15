import os

from flask import Flask,request
from waiter.main import setWebhook, workOn

app = Flask(__name__)

@app.route("/")
def index():
    return "App Started"


@app.route('/bot', methods=['GET', 'POST'])
async def bot():
    app.logger.info("Request Received")
    if request.method == 'POST':
        data = request.get_json()
        if await workOn(data):
            return Response('Success',200)
        else:
            return "No response from client"
    else:
        print(request.base_url)
        return "<h1>Server is Working Fine</h1>"


@app.route("/reset")
def resethook():
    url = request.base_url
    return setWebhook((url.split(sep="/"))[2]+'/bot')

@app.route("/test")
def test():
    return request.base_url

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=int(os.environ.get("PORT", 8080)))
