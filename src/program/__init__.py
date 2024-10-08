import os


DATA_PATH:str = f"{os.getenv('APPDATA', '')}/HeatSeekers"
CONNECTION_DATA_PATH:str = f"{DATA_PATH}/mqtt"

from .program import Program
print("SRC __init__")


__all__ = [
    'Program',
]
