import requests
from datetime import datetime, timedelta
from pprint import pprint

SERVER_URL = 'http://localhost:5000'

def login(name):
    response = requests.post(f'{SERVER_URL}/login', json={'name': name})
    return response.json()

def get_resources():
    response = requests.get(f'{SERVER_URL}/resources')
    return response.json()

def block_resource(resource_id, client_name):
    start_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    response = requests.post(f'{SERVER_URL}/block_resource', json={
        'resource_id': resource_id,
        'client_name': client_name,
        'start_time': start_time,
        'end_time': end_time
    })
    return response.json()

def cancel_block(resource_id, reservation_id):
    response = requests.post(f'{SERVER_URL}/cancel_block', json={
        'resource_id': resource_id,
        'reservation_id': reservation_id
    })
    return response.json()

def finalize_reservation(resource_id, reservation_id):
    response = requests.post(f'{SERVER_URL}/finalize_reservation', json={
        'resource_id': resource_id,
        'reservation_id': reservation_id
    })
    return response.json()

if __name__ == '__main__':
    name = input('Enter your name: ')
    login_response = login(name)
    pprint(login_response)

    if login_response['status'] == 'success':
        while True:
            print("\nOptions:")
            print("1. Get resources")
            print("2. Block resource")
            print("3. Cancel block")
            print("4. Finalize reservation")
            print("5. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                resources = get_resources()
                pprint(resources)

            elif choice == '2':
                resource_id = input("Enter resource ID: ")
                block_response = block_resource(resource_id, name)
                pprint(block_response)
                # Check the resources again to see if the reservation is made
                resources = get_resources()
                pprint(resources)

            elif choice == '3':
                resource_id = input("Enter resource ID: ")
                reservation_id = input("Enter reservation ID: ")
                cancel_response = cancel_block(resource_id, reservation_id)
                pprint(cancel_response)
                # Check the resources again to see if the reservation is canceled
                resources = get_resources()
                pprint(resources)

            elif choice == '4':
                resource_id = input("Enter resource ID: ")
                reservation_id = input("Enter reservation ID: ")
                finalize_response = finalize_reservation(resource_id, reservation_id)
                pprint(finalize_response)
                # Check the resources again to see if the reservation is finalized
                resources = get_resources()
                pprint(resources)

            elif choice == '5':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")
