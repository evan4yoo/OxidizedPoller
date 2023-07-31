import platform
import subprocess
import paramiko
import socket
import os
import shutil
import asyncio
import concurrent.futures
from datetime import datetime, date
from config import secrets, networks, directory

hostname = socket.gethostname()
ip_addr = socket.gethostbyname(hostname)


oxifile = "router.db"
logfile = "debug.log"

user = secrets.get('user')
passw = secrets.get('pass')
oxiuser = secrets.get('oxiuser')
oxisecret = secrets.get('oxisecret')


def log(host, siteid):
    with open(oxifile, 'a') as routerfile:
        routerfile.write(f"{siteid}:{host}:routeros:{oxiuser}:{oxisecret}\n")


def hostchecker(host):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(host, username=user, password=passw, banner_timeout=5)

        stdin, stdout, stderr = ssh.exec_command("/system identity print")
        output = stdout.read().decode("utf-8")
        parsespace = output.replace(" ", "").replace(",", "").replace(":", "")
        parsed = parsespace[5:].strip()
        log(host, parsed)

    except paramiko.AuthenticationException:
        # Authentication failed, write to logfile
        with open(logfile, "a") as auditlog:
            auditlog.write(f"Auth failed for host {host}\n")

    except paramiko.ssh_exception.NoValidConnectionsError:
        # No valid connections, write to logfile
        with open(logfile, "a") as auditlog:
            auditlog.write(f"SSH Failed No Valid Connections for {host}\n")

    except paramiko.ssh_exception.SSHException as e:
        # Error reading SSH protocol banner, write to logfile and print error message
        with open(logfile, "a") as auditlog:
            auditlog.write(f"{host}: {str(e)}\n")

    except TimeoutError:
        # Timeout error, write to logfile
        with open(logfile, "a") as auditlog:
            auditlog.write(f"Connection timed out for host {host}\n")

    except Exception as e:
        # Other exception, log the error message
        with open(logfile, "a") as auditlog:
            auditlog.write(f"Unexpected error for host {host}: {str(e)}\n")

    finally:
        ssh.close()


async def hostpool(host):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, hostchecker, host)


async def ping(host):
    if system == "Windows":
        try:
            ping_cmd = ["ping", "-n", "1", "-w", "400", host]
        except TimeoutError:
            pass
    else:
        try:
            ping_cmd = ["ping", "-c", "1", "-W", "2", "-q", host]
        except TimeoutError:
            pass

    with open(os.devnull, 'w') as null:
        result = subprocess.call(ping_cmd, stdout=null, stderr=null)

    if result == 0:
        await hostpool(host)
    else:
        pass
    return



def init():
    backupdir = directory + "/backup"
    if system == "Windows":
        if not os.path.exists(backupdir):
            os.mkdir(backupdir)

        if os.path.exists(oxifile):
            newfile = "router" + str(date.today()) + ".db"
            os.rename(oxifile, newfile)
            shutil.move(newfile, os.path.join(backupdir, "router" + str(date.today()) + ".db"), copy_function=shutil.copy2)
            print(f"{oxifile} was renamed and moved to {directory}/backup")

        if os.path.exists(logfile):
            newfile = "debug" + str(date.today()) + ".log"
            os.rename(logfile, newfile)
            shutil.move(newfile, os.path.join(backupdir, "debug" + str(date.today()) + ".log"), copy_function=shutil.copy2)
            print(f"{logfile} was renamed and moved to {directory}/backup")

    else:
        if not os.path.exists(backupdir):
            os.mkdir(backupdir)

        if os.path.exists(oxifile):
            newfile = "router" + str(date.today()) + ".db"
            os.rename(oxifile, newfile)
            shutil.move(newfile, os.path.join(backupdir, "router" + str(date.today()) + ".db"), copy_function=shutil.copy2)
            print(f"{oxifile} was renamed and moved to {directory}/backup")

        if os.path.exists(logfile):
            newfile = "debug" + str(date.today()) + ".log"
            os.rename(logfile, newfile)
            shutil.move(newfile, os.path.join(backupdir, "debug" + str(date.today()) + ".log"), copy_function=shutil.copy2)
            print(f"{logfile} was renamed and moved to {directory}/backup")
        return


async def main():
    print(f"OS found: " + system)
    print(f"Local IP Set: " + ip_addr)
    print(f"System Time: " + str(date.today()))
    init()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = []
        # iterate through networks
        for network in networks:
            # iterate through network hosts inside each network
            for host in network.hosts():
                tasks.append(asyncio.create_task(ping(str(host))))

        await asyncio.gather(*tasks)


    end_time = datetime.now()
    # add counters for devices pinged successfully, devices failed to login to, devices added to oxidized
    print('Runtime Duration: {}'.format(end_time - start_time))
    return


start_time = datetime.now()
system = platform.system()
asyncio.run(main())