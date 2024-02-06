from websocket import create_connection
import json
def send_mssage(data, user):
    ws = create_connection("ws://localhost:8000/ws/chat/")
    message = data['message']
    # user_id = user
    info = {
        "message":message,
        "client":user
    }
    ws.send(json.dumps(info)) 
    result = ws.recv()
    print("Received '%s'" % result)
    ws.close()