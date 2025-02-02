import socketio
import json


sio = socketio.Client()


@sio.event
def connect():
    print("connected")


node_id = None


@sio.event
def add_node(node):
    global node_id
    print("node added")
    # print(node)
    node_id = node.get("id")


@sio.event
def add_arc(arc):
    print("arc added")
    print(arc)


@sio.event
def transmission_finished():
    print("transmission finished!")


sio.connect("http://localhost:5000")

sio.emit("request_timeline", "Battle of hastings")

input()

print(f"extending from {node_id}...")
sio.emit("extend_timeline", node_id)

sio.wait()