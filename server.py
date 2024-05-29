from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import Resource, Reservation
import uuid
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

resources = {}
clients = []

@app.route('/login', methods=['POST'])
def login():
    client_name = request.json.get('name')
    if client_name:
        clients.append(client_name)
        resources_info = {res_id: res.to_dict() for res_id, res in resources.items()}
        return jsonify({'status': 'success', 'resources': resources_info}), 200
    return jsonify({'status': 'failure'}), 400

@app.route('/resources', methods=['GET'])
def get_resources():
    resources_info = {res_id: res.to_dict() for res_id, res in resources.items()}
    return jsonify({'resources': resources_info}), 200

def is_time_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

@app.route('/block_resource', methods=['POST'])
def block_resource():
    data = request.json
    resource_id = data.get('resource_id')
    client_name = data.get('client_name')
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%dT%H:%M:%S')

    if resource_id in resources:
        for reservation in resources[resource_id].reservations:
            existing_start = datetime.strptime(reservation.start_time, '%Y-%m-%dT%H:%M:%S')
            existing_end = datetime.strptime(reservation.end_time, '%Y-%m-%dT%H:%M:%S')
            if is_time_overlap(start_time, end_time, existing_start, existing_end):
                return jsonify({'status': 'failure', 'message': 'Time slot already reserved'}), 400

        reservation_id = str(uuid.uuid4())
        reservation = Reservation(reservation_id, resource_id, client_name, data.get('start_time'), data.get('end_time'))
        resources[resource_id].reservations.append(reservation)

        socketio.emit('resource_blocked', {'resource_id': resource_id, 'reservation': reservation.to_dict()})
        print(f'Resource {resource_id} blocked by {client_name} from {data.get("start_time")} to {data.get("end_time")}')
        return jsonify({'status': 'success', 'reservation_id': reservation_id}), 200

    return jsonify({'status': 'failure'}), 400

@app.route('/cancel_block', methods=['POST'])
def cancel_block():
    data = request.json
    reservation_id = data.get('reservation_id')
    resource_id = data.get('resource_id')

    if resource_id in resources:
        resource = resources[resource_id]
        resource.reservations = [res for res in resource.reservations if res.reservation_id != reservation_id]

        socketio.emit('block_canceled', {'resource_id': resource_id, 'reservation_id': reservation_id})
        print(f'Reservation {reservation_id} for resource {resource_id} canceled')
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 400

@app.route('/finalize_reservation', methods=['POST'])
def finalize_reservation():
    data = request.json
    reservation_id = data.get('reservation_id')
    resource_id = data.get('resource_id')

    if resource_id in resources:
        for res in resources[resource_id].reservations:
            if res.reservation_id == reservation_id:
                res.status = 'confirmed'

                socketio.emit('reservation_finalized', {'resource_id': resource_id, 'reservation': res.to_dict()})
                print(f'Reservation {reservation_id} for resource {resource_id} finalized')
                return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 400

@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to server'})
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    resources['1'] = Resource('1', 'Conference Room')
    resources['2'] = Resource('2', 'Projector')

    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
