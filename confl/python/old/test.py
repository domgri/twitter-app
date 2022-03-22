
import time
import asyncio
import threading


#https://stackoverflow.com/questions/63856166/python-asyncio-run-infinite-loop-in-background-and-access-class-variable-from-th
#https://realpython.com/python-async-features/
#https://docs.python.org/3/library/asyncio.html

#https://jeffknupp.com/blog/2012/03/31/pythons-hardest-problem/
# https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python

# Synchronous functions, works depending on a break time.
# Intension to use inf loop for 15min and then go to dbfunctions and repeat the process.

data = []

async def infinityLoop():

    timeout = time.time() + 10 # 10s
    while  time.time() < timeout:
        print("Loop")
        data.append("1")
        time.sleep(2)

    # while True:
    #     print("Loop")
    #     time.sleep(10)
    #     continue
    

async def dbfuntions():

    print("Try")
    await asyncFunction()
    print("Try2")
    await asyncFunction2()
    print("Sleep Time - 10s")


async def asyncFunction():
    time.sleep(2)
    print("Asynch function")
    print(data)

async def asyncFunction2():
    time.sleep(3)
    print("Asynch function 2")
    print(data)

async def main():

    #loop = asyncio.get_event_loop()
    #loop.call_later(5, stop)
    #task = loop.create_task(asyncFunction)

    
    while True:

        try:

            #loop = asyncio.get_event_loop()

            #task1 = loop.create_task(infinityLoop())
            #task2 = loop.create_task(dbfuntions())

            # loop = asyncio.new_event_loop()
            #threading.Thread(target=loop.run_forever).start()
            #future = asyncio.run_coroutine_threadsafe(infinityLoop(), loop)

            # task2 = loop.create_task(dbfuntions())
            # loop.run_until_complete(task2)

            # while True:
            #     print("loop")
            #     #await task1
            #     await task2

            task1 = asyncio.create_task(infinityLoop())
            task2 = asyncio.create_task(dbfuntions())

            await asyncio.gather(
                task1,
                task2
            )
        
        
            
            
            
        except Exception as e:
            print(str(e))
            #loop.call_soon_threadsafe(loop.stop)
            pass





asyncio.run(main())
