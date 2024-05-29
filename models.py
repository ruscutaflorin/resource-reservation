from datetime import datetime

class Resource:
    def __init__(self, resource_id, name):
        self.resource_id = resource_id
        self.name = name
        self.reservations = []

    def to_dict(self):
        return {
            'resource_id': self.resource_id,
            'name': self.name,
            'reservations': [res.to_dict() for res in self.reservations]
        }

class Reservation:
    def __init__(self, reservation_id, resource_id, client_name, start_time, end_time):
        self.reservation_id = reservation_id
        self.resource_id = resource_id
        self.client_name = client_name
        self.start_time = start_time
        self.end_time = end_time
        self.status = 'pending'

    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'resource_id': self.resource_id,
            'client_name': self.client_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status
        }
