from scrapli.driver.core import IOSXEDriver, NXOSDriver
from scrapli_cfg import ScrapliCfg
from test2_MT_cfg_inv import switches
import time
from rich import print
import queue
from threading import Thread


def config(switch, genie_list, error_ips):

    while True:
        switch = q.get()
        host = switch["host"]

        try: 
            cli = switch.pop("driver")(**switch)
            cli.open()
            
            cfg_conn = ScrapliCfg(conn=cli,  ignore_version=True)
            cfg_conn.prepare()

            prompt_result =  cli.get_prompt()
            ver_result =  cfg_conn.get_version()

            genie_dict = {"IP Address":host,
                        "Hostname":prompt_result,
                        "Version":ver_result.result} 
            genie_list.append(genie_dict) 

        except:
            error_ips_dict = {"IP Address":host} 
            error_ips.append(error_ips_dict)  

        q.task_done()


if __name__ == '__main__':

    startTime = time.time()

    q = queue.Queue()
    genie_list = []
    error_ips = []
    for thread_no in range(8):
        worker = Thread(target=config, args=(q, genie_list, error_ips, ), daemon=True)
        worker.start()

    for switch in switches:
            q.put(switch)

    q.join()



    print("\n")
    print("*"*60)
    # Print Successes
    for device in genie_list:
        # print(device)
        print(f"device: {device['Hostname']} ---> Version: {device['Version']}")
        # print("\n")

    # Print IPs with errors
    print("\n")
    if error_ips != []:
        for ip in error_ips:
            print(f"Error connecting to {ip['IP Address']}")
            # with open ("Scrapli_Connection_Error_IPs.txt", "a") as f:
            #     f.write(ip + "\n")
    print("*"*60)

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
