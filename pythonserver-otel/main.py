from flask import Flask, request, Response
import os

app = Flask(__name__)

@app.route("/smoke")
def smoke():
    return Response(status=200)

@app.route("/ping")
def ping():
    return "PONG!"

@app.route("/work")
def work():
    numbers = [i for i in range(10000)]
    numbers_str = ' '.join(map(str, numbers))
    return numbers_str

@app.route("/users", methods=['POST'])
def users():
    content = request.json
    return content

if __name__ == '__main__':
    print(f"Server running: port={8080} process_id={os.getpid()}")
    app.run(host="localhost", port=8080, debug=False)