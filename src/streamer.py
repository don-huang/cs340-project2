# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP

# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct


class Streamer:
    HEADER_FORMAT = "!I"  # 4-byte unsigned int (sequence number)
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAX_PAYLOAD_SIZE = 1472 - HEADER_SIZE

    def __init__(self, dst_ip, dst_port, src_ip=INADDR_ANY, src_port=0):
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

        self.send_seq = 0
        self.expected_seq = 0
        self.recv_buffer = {}  # buffer for out-of-order packets

    def send(self, data_bytes: bytes) -> None:
        for i in range(0, len(data_bytes), self.MAX_PAYLOAD_SIZE):
            chunk = data_bytes[i : i + self.MAX_PAYLOAD_SIZE]
            header = struct.pack(self.HEADER_FORMAT, self.send_seq)
            self.socket.sendto(header + chunk, (self.dst_ip, self.dst_port))
            self.send_seq += 1

    def recv(self) -> bytes:
        while True:
            if self.expected_seq in self.recv_buffer:
                data = self.recv_buffer.pop(self.expected_seq)
                self.expected_seq += 1
                return data

            data, addr = self.socket.recvfrom()
            if len(data) < self.HEADER_SIZE:
                continue  # drop malformed packet

            (seq,) = struct.unpack(self.HEADER_FORMAT, data[: self.HEADER_SIZE])
            payload = data[self.HEADER_SIZE :]

            if seq == self.expected_seq:
                self.expected_seq += 1
                return payload
            elif seq > self.expected_seq and seq not in self.recv_buffer:
                self.recv_buffer[seq] = payload

    def close(self) -> None:
        pass
