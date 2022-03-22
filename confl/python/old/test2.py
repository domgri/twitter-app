from multiprocessing import Pool, cpu_count, Array
import time
from random import randrange
from ctypes import c_char_p

# https://jeffknupp.com/blog/2012/03/31/pythons-hardest-problem/
# https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python

# https://stackoverflow.com/questions/44660676/python-using-multiprocessing

# RABITHOLE.........

def infinityLoop(data):
    print("infinity")

    # timeout = time.time() + 10 # 10s
    # while  time.time() < timeout:
    #     print("Loop")
    #     time.sleep(2)

    while True:
        print("Loop")
        print(len(data))
        print(data)
        data[0] = randrange(10)
        time.sleep(1)
        continue
    

def dbfuntions(data):
    print("dbfunctions")

    while True:
        asyncFunction(data)
        asyncFunction2(data)
        time.sleep(5)


def asyncFunction(data):
    time.sleep(3)
    print("Asynch function")
    if len(data) > 0:
        print("Last added: " + data[len(data) - 1])

def asyncFunction2(data):
    time.sleep(2)
    print("Asynch function 2")
    if len(data) > 0:
        print("Last added: " + data[len(data) - 1])



def main():
    print("main")
    data = Array(c_char_p, 1000)

    try:

        pool = Pool(processes=(cpu_count() - 1))
        res = pool.apply_async(infinityLoop(data))
        res = pool.apply_async(dbfuntions(data))
        pool.close()
        pool.join()
    except Exception as e:
        print("Main Loop exception: " + str(e))
    
    print("end of main")


    
main()