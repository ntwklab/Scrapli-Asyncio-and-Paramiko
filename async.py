#!/usr/bin/env python

import asyncio
from operator import contains
import os
from async_inv import DEVICES
from rich import print
from scrapli.logging import enable_basic_logging
from scrapli_cfg import AsyncScrapliCfg
import time


# Enable logging. Create a log file in base.
basedir = os.path.abspath(os.path.dirname(__file__))
scrapli_log = basedir + "/scrapli_cfg.log"
enable_basic_logging(file=scrapli_log, level="debug")

# declare function as a coroutine via async keyword
async def gather_version(device):

    # Create async connection. Set as awaitable
    async_conn = device.pop("driver")(**device)
    try:
        # Open async connection - Set as awaitable
        await async_conn.open()

        # Create Scrapli Cfg async connection
        async_cfg_conn = AsyncScrapliCfg(conn=async_conn, ignore_version=True)

        # Prepare Scrapli Cfg async connection - Set as awaitable
        await async_cfg_conn.prepare()

        # Get device prompt and version - Set as awaitables
        prompt_result = await async_conn.get_prompt()
        version_result = await async_cfg_conn.get_version()

        # Close connection - Set as awaitable
        await async_conn.close()
    
    except:
        prompt_result = device['host']
        version_result = "Failed to Connect"

    # Return results
    return prompt_result, version_result,



# declare function as a coroutine via async keyword
async def main():
    
    error_ips = []
    # Create list of coroutines
    coroutines = [gather_version(device) for device in DEVICES]

    # Run coroutines concurrently - Set as awaitable
    results = await asyncio.gather(*coroutines)

    print("\n")
    print("*"*60)
    # Print results
    for result in results:
        if result[1] != "Failed to Connect":
            print(f"Hostname: {result[0]} ---> {result[1].result}")
        else:
            error_ips.append(result[0])
            # print(f"IP: {result[0]} {result[1]}")
    
    print("\n")
    if error_ips != []:
        for ip in error_ips:
            print(f"Error connecting to {ip}")
    print("*"*60)


if __name__ == "__main__":
    startTime = time.time()

    # Create event loop and run main()
    asyncio.get_event_loop().run_until_complete(main())

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
