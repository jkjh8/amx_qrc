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
        self.send_someting = False
        
    def connect(self):
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.connected = True
                threading.Thread(target=self.recv, daemon=True).start()
                threading.Thread(target=self.queue_send, daemon=True).start()
                threading.Thread(target=self.noOp, daemon=True).start()
                print("qrc socket Connected\n")
                self.set_pa_callback()
                break
            except Exception as e:
                print(f"qrc connect error {e}")
                if e.errno == 106:
                    self.connected = True
                    threading.Thread(target=self.recv, daemon=True).start()
                    break
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
                print(f"qrc queue_send {data}")
                self.send_someting = True
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
                print (f"qrc recv {data}")
                if data:
                    self.rt_queue_send(data)
                else:
                    print("qrc recv error: connection closed by the server\n")
                    self.sock.close()
                    time.sleep(5)
                    self.connected = False
                    self.connect()
                    break
            except Exception as e:
                print(f"qrc recv error {e}")
                # if e.errno != 106:
                self.connected = False
                self.connect()
                break

    def _callback(self):
        try:
            while not self.rt_queue.empty() and self.connected:
                rt = self.rt_queue.get()
                print(f"qrc _callback {rt}")
                self.callback(rt)
        except Exception as e:
            print(f"qrc _callback error {e}")
            
    def rt_queue_send(self, data):
        try:
            data_parts = data.split(b'\x00')
            for i, part in enumerate(data_parts):
                if i == 0:
                    self.buffer += part
                else:
                    self.callback(json.loads(self.buffer.decode('utf-8')))
                    self.send_someting = True
                    self.buffer = part
        except Exception as e:
            self.buffer = b''
            print(f"qrc rt_queue_send error {e}")
            
    def noOp(self):
        while True:
            if self.send_someting:
                self.send('noOp', 'NoOp', {})
                self.send_someting = False
            time.sleep(50)

    def close(self):
        self.sock.close()

    def __del__(self):
        self.sock.close()