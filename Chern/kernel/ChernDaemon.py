#!/usr/bin/python3
import daemon
import time
from daemon import pidfile
import os
import sys
import subprocess
from Chern.utils import csys
from Chern.kernel.ChernDatabase import ChernDatabase
# from Chern.kernel.VImage import VImage
# from Chern.kernel.VContainer import VContainer
# from Chern.kernel.VJob import VJob

cherndb = ChernDatabase.instance()

def execute():
    waitting_jobs = cherndb.jobs("submitted")
    # print("List {0}".format(waitting_jobs), file=sys.stderr)
    for job in waitting_jobs:
        print("Running {0}".format(job), file=sys.stderr)
        flag = True
        for pred_object in job.predecessors():
            if pred_object == "container" and VContainer(pred_object.path).status() != "done":
                flag = False
                break
            if pred_object == "image" and VImage(pred_object.path).status() != "built":
                flag = False
                break
        if flag:
            job.execute()
            break
    del waitting_jobs

def status():
    daemon_path = csys.daemon_path()
    if os.path.exists(daemon_path+"/daemon.pid"):
        return "started"
        pid = open(daemon_path+"/daemon.pid").read().decode().strip()
    else:
        return "stopped"
    # subprocess.call("kill {}".format(open(daemon_path + "/daemon.pid").read()), shell=True)

def start():
    daemon_path = csys.daemon_path()
    with daemon.DaemonContext(
        working_directory="/",
        pidfile=pidfile.TimeoutPIDLockFile(daemon_path + "/daemon.pid"),
        stderr=open(daemon_path + "/log", "w+"),
        ):
        while True:
            time.sleep(1)
            try:
                execute()
            except Exception as e:
                print(e, file=sys.stderr)

def stop():
    if status() == "stop":
        return
    daemon_path = csys.daemon_path()
    subprocess.call("kill {}".format(open(daemon_path + "/daemon.pid").read()), shell=True)

if __name__ == "__main__":
    start()
