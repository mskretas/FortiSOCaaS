import socket
import sys


HOST = "0.0.0.0"
PORT = 5514


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Listening for UDP syslog on {HOST}:{PORT}", flush=True)

    while True:
        data, address = sock.recvfrom(65535)
        message = data.decode("utf-8", errors="replace").strip()
        print(f"{address[0]}:{address[1]} {message}", flush=True)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
