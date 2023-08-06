import random
import base64
import time
import sys

print base64.b64decode('SGFwcHkgMjQsIERvbWFzaCEgV2FpdCwgd2FpdCBmb3IgaXQuLi4='),
try:
    while True:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(random.random())
except KeyboardInterrupt:
    print base64.b64decode('CkRvbid0IHdhc3RlIHlvdXIgdGltZS4gTGlmZSdzIHRvbyBzaG9ydCBmb3Igbm9uLWxlZ2VuZGFyeSB0aGluZ3MKLS0gZi4K')


