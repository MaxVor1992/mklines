from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/aaa')
def hello_world():
    return 'Hello Flask!!!! 1'

if __name__ == '__main__':
    app.run()
