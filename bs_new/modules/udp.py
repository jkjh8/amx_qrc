import socket, threading
class UdpServer:
    BUFFER_SIZE = 1024

    def __init__(self, port, callback=None):
        self.port = port
        self.callback = callback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", self.port))

    def run(self):
        self.server_thread = threading.Thread(target=self.handle, daemon=True)
        self.server_thread.start()
        # print("UDP server thread has started\n")

    def handle(self):
        print(f"UDP server is starting @ port: {self.port}")
        while True:
            try:
                data, addr = self.socket.recvfrom(self.BUFFER_SIZE)
                print(f"Received message: {data=} from {addr=}")
                if self.callback is not None:
                    self.callback(data=data, addr=addr)
            except Exception as e:
                print(f"An error occurred: {e}")
                if not self.running:
                    break