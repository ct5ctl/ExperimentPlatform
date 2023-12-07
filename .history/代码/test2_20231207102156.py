global data
from test import data
from multiprocessing import Manager

def pri():
    
    print(str(data.get_pos_current()))

while True:
    pri()   
