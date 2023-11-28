@echo off

start cmd /k python server.py

for /L %%x in (1, 1, 6) do (
    start cmd /k python client.py
)