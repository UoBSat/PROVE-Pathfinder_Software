#!/usr/bin/env python
import psutil
import time
import datetime

while(1):
    print(f'[{datetime.datetime.now().timestamp()}] CPU: {psutil.cpu_percent()} %')
    print(f'[{datetime.datetime.now().timestamp()}] RAM: {psutil.virtual_memory().percent} %')
    time.sleep(1)
