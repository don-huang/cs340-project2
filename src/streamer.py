# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP

# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct
import threading
import time


class Streamer:
    HEADER_FORMAT = "!IB"  # 4-byte seq num, 1-byte type (0=data, 1=ack, 2=fin)
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAX_PAYLOAD_SIZE = 1472 - HEADER_SIZE

    TYPE_DATA = 0
    TYPE_ACK = 1
    TYPE_FIN = 2

    def __init__(self, dst_ip, dst_port, src_ip=INADDR_ANY, src_port=0):
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

        self.send_seq = 0
        self.expected_seq = 0
        self.recv_buffer = {}
        self.ack_received = threading.Event()
        self.ack_seq = None

        self.closed = False
        self.executor = threading.Thread(target=self.listener, daemon=True)
        self.executor.start()

    def send(self, data_bytes: bytes) -> None:
        for i in range(0, len(data_bytes), self.MAX_PAYLOAD_SIZE):
            chunk = data_bytes[i : i + self.MAX_PAYLOAD_SIZE]
            while True:
                header = struct.pack(self.HEADER_FORMAT, self.send_seq, self.TYPE_DATA)
                self.socket.sendto(header + chunk, (self.dst_ip, self.dst_port))

                self.ack_received.clear()
                success = self.ack_received.wait(timeout=0.25)

                if success and self.ack_seq == self.send_seq:
                    break  # ACK received, proceed to next seq

            self.send_seq += 1

    def recv(self) -> bytes:
        while True:
            if self.expected_seq in self.recv_buffer:
                data = self.recv_buffer.pop(self.expected_seq)
                self.expected_seq += 1
                return data

    def listener(self):
        while not self.closed:
            try:
                data, addr = self.socket.recvfrom()
                if len(data) < self.HEADER_SIZE:
                    continue

                seq, msg_type = struct.unpack(
                    self.HEADER_FORMAT, data[: self.HEADER_SIZE]
                )
                payload = data[self.HEADER_SIZE :]

                if msg_type == self.TYPE_ACK:
                    self.ack_seq = seq
                    self.ack_received.set()

                elif msg_type == self.TYPE_DATA:
                    # Always ACK back
                    ack_header = struct.pack(self.HEADER_FORMAT, seq, self.TYPE_ACK)
                    self.socket.sendto(ack_header, (self.dst_ip, self.dst_port))

                    if seq == self.expected_seq:
                        self.recv_buffer[seq] = payload
                    elif seq > self.expected_seq and seq not in self.recv_buffer:
                        self.recv_buffer[seq] = payload

                elif msg_type == self.TYPE_FIN:
                    fin_ack = struct.pack(self.HEADER_FORMAT, seq, self.TYPE_ACK)
                    self.socket.sendto(fin_ack, (self.dst_ip, self.dst_port))
                    self.fin_received = True

            except Exception as e:
                print("listener died")
                print(e)

    def close(self) -> None:
        # Send FIN and wait for ACK
        fin_seq = self.send_seq
        while True:
            fin_packet = struct.pack(self.HEADER_FORMAT, fin_seq, self.TYPE_FIN)
            self.socket.sendto(fin_packet, (self.dst_ip, self.dst_port))

            self.ack_received.clear()
            success = self.ack_received.wait(timeout=0.25)

            if success and self.ack_seq == fin_seq:
                break

        time.sleep(2)
        self.closed = True
        self.socket.stoprecv()
        self.executor.join(timeout=1)
