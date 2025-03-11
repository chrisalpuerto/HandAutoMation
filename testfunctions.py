import cv2
import mediapipe as mp
import numpy as np
from pythonosc import udp_client


client = udp_client.SimpleUDPClient("127.0.0.1",12345)
client.send_message("/live/track/reverb", 1)