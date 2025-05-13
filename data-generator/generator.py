import socket
import json
import time
import random

HOST = '0.0.0.0'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Listening on {HOST}:{PORT}")
conn, addr = server_socket.accept()
print(f"Connection from {addr}")

accounts = [1, 2, 3, 4, 5]

while True:
    account_id = random.choice(accounts)
    amount = random.uniform(10, 10000)
    location = random.choice(["HN", "HCM", "DN"])
    timestamp = int(time.time())

    transaction = {
        "account_id": account_id,
        "transaction_id": random.randint(1000, 9999),
        "amount": amount,
        "location": location,
        "timestamp": timestamp
    }
    msg = json.dumps(transaction) + "\n"
    conn.sendall(msg.encode('utf-8'))
    print("Sent:", msg.strip())
    time.sleep(0.2)






































# import socket
# import json
# import time
# import random

# HOST = '0.0.0.0'
# PORT = 9999

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((HOST, PORT))
# server_socket.listen(1)

# print(f"Listening on {HOST}:{PORT}")
# conn, addr = server_socket.accept()
# print(f"Connection from {addr}")

# while True:
#     transaction = {
#         "transaction_id": random.randint(1000, 9999),
#         "amount": random.uniform(10, 10000),
#         "location": random.choice(["HN", "HCM", "DN"]),
#         "timestamp": int(time.time())
#     }
#     msg = json.dumps(transaction) + "\n"
#     conn.sendall(msg.encode('utf-8'))
#     print("Sent:", msg.strip())
#     time.sleep(1)
