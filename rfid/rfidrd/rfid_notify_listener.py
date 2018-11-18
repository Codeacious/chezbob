#!/usr/bin/env python3
import argparse
import socket
import subprocess
from xml.etree import ElementTree as ET

MSG_FRAME_BYTE=b'\x00'


def parse_args():
    parser = argparse.ArgumentParser(description="Listening server for RFID tags")
    parser.add_argument("-i", "--ip", type=str, default='0.0.0.0',
                        help="IP Address to listen for RFID reader on")
    parser.add_argument("-p", "--port", type=int, default=4567,
                        help="Port to listen for RFID reader on")
    parser.add_argument("-t", "--timeout", type=int, default=60,
                        help="Timeout for client socket for RFID reader")
    return parser.parse_args()


def get_tag_list_from_update(update_str):
    xml_tree = ET.fromstring(update_str)
    taglist = xml_tree.find("Alien-RFID-Tag-List")
    tag_list = []
    for tag in taglist:
        tag_id = tag.find("TagID").text
        tag_list.append(tag_id)
    return tag_list


def make_listen_socket(args):
    print("Binding server socket to %s:%d..." % (args.ip, args.port))
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.bind((args.ip, args.port))
    sk.listen(2)
    sk.settimeout(args.timeout)
    return sk


def client_loop(server_sk, timeout=60):
    client_sk, client_addr = server_sk.accept()
    print("Connected client socket")
    client_sk.settimeout(timeout)
    remainder_buf = b""

    while True:
        recvd = client_sk.recv(2**13)
        if not recvd:
            client_sk.close()
            print("Client socket closed")
            return

        remainder_buf += recvd
        frames = remainder_buf.split(MSG_FRAME_BYTE)
        updates = frames[:-1]
        remainder_buf = frames[-1]
        for update_frame in updates:
            update_str = update_frame.decode()
            tag_list = get_tag_list_from_update(update_str)
            print("Tag list update:\n%s" % str(tag_list))


if __name__ == "__main__":
    args = parse_args()
    server_sk = make_listen_socket(args)
    while True:
        try:
            client_loop(server_sk, timeout=args.timeout)
        except Exception as e:
            print(str(e))
            continue
    server_sk.close()
