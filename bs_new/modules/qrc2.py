import socket, threading, queue, time,json

class QRC:
    def __init__(self, host,callback):
        self.host = host
        self.port = 1710
        self.buffer = b''
        self.buffer_size = 4096
        self.callback = callback
        self.connected = False
        self.queue = queue.Queue()
        self.rt_queue = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        while not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
                threading.Thread(target=self.recv, daemon=True).start()
                threading.Thread(target=self.queue_send, daemon=True).start()
                # threading.Thread(target=self.noOp, daemon=True).start()
                print("qrc socket Connected\n")
                self.set_pa_callback()
            except Exception as e:
                print(f"qrc connect error {e}")
                self.connected = False
                time.sleep(5)
                
    def set_pa_callback(self):
        self.send('zone-status-configure', 'PA.ZoneStatusConfigure', { "Enabled": True })

    def send(self, id, method, params):
        obj = {"jsonrpc": "2.0", "method": method, "params": params, "id": id}
        self.queue.put(json.dumps(obj).encode('utf-8') + b'\x00')
        
    def queue_send(self):
        print("qrc_queue_send_thread_started\n")
        while True:
            try:
                if not self.connected:
                    self.connect()
                data = self.queue.get(timeout=0.1)
                self.sock.send(data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"qrc queue_send error {e}")
            finally:
                time.sleep(0.1)

    def recv(self):
        while True:
            try:
                data = self.sock.recv(self.buffer_size)
                if data:
                    self.rt_queue_send(data)
                else:
                    self.connected = False
                    print("qrc recv error: connection closed by the server\n")
                    self.connect()
                    break
            except Exception as e:
                if e.errno != 106:
                    self.connected = False
                    self.connect()
                break

    def _callback(self):
        try:
            while not self.rt_queue.empty() and self.connected:
                self.callback(self.rt_queue.get())
        except Exception as e:
            self.callback(f"qrc _callback error {e}")
            
    def rt_queue_send(self, data):
        try:
            data_parts = data.split(b'\x00')
            for i, part in enumerate(data_parts):
                if i == 0:
                    self.buffer += part
                else:
                    self.callback(json.loads(self.buffer.decode('utf-8')))
                    self.buffer = part
        except Exception as e:
            self.buffer = b''
            print(f"qrc rt_queue_send error {e}")
            
    def noOp(self):
        while True:
            time.sleep(50)
            if self.queue.empty():
                self.send('noOp', 'NoOp', {})

    def close(self):
        self.sock.close()

    def __del__(self):
        self.sock.close()