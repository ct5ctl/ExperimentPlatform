from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟数据
data = {
    'SteeringWheelDirection': 111,
    'SteeringWheelAngle': 111,
    'ThrottleDepth': 111,
    'BrakeDepth': 111,
    'Speed': 111,
    'DoorStatus': 111
}

# GET 请求处理
@app.route('/api', methods=['GET'])
def get_data():
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='172.0.0.1', port=902)
