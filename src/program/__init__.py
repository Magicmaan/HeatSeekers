import os
from .program import Program

DATA_PATH:str = f"{os.getenv('APPDATA', '')}/HeatSeekers"
CONNECTION_DATA_PATH:str = f"{DATA_PATH}/mqtt"

print("SRC __init__")

__all__ = [
    'Program',
]