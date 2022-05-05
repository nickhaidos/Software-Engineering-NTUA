import subprocess
import os

file_path = os.path.dirname(__file__)
command = f'py -m pip install -r "{file_path}\\requirements.txt"'
#command = f'py -m pip install -r requirements.txt'
#print(command)
#subprocess.run([command], stdout=subprocess.PIPE)
os.system(command)
