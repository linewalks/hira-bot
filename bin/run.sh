#!/bin/bash
> nohup.out
nohup python3 -u nhiss_bot.py&
echo "[HiraBot] Running on pid $!" >> nohup.out
tail -f nohup.out


