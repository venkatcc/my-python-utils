# Requires Python 3+
import threading
import datetime
import queue
import time
import os, sys, subprocess

q = queue.Queue()
start = time.time()

def worker(tname):
    while True:
        dirname = q.get()
        # print("%s: %s" % ((tname), dirname))
        p1 = subprocess.Popen(["svn", "status", "-uq", "--depth=files", dirname],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        p2 = subprocess.Popen(["grep", "-v", "xrdb"], stdin = p1.stdout,
                stdout = subprocess.PIPE)
        p1.stdout.close()
        for line in p2.stdout:
            if ("Status against revision" not in str(line)):
                sys.stdout.writelines(str(line.rstrip())[2:-1])
                sys.stdout.writelines("\n")
        # print("Queue size: %d" % q.qsize())
        q.task_done()


if __name__ == '__main__':
    for root, dirs, files in os.walk(sys.argv[1], topdown = False):
        if '.svn' not in root:
            q.put(root)

    print("svn status program: %d (queue size)" % q.qsize())

    for id in range(10):
        tname = str("Thread-") + str(id)
        t = threading.Thread(target = worker, args = (str(tname),))
        t.daemon = True
        t.start()

    q.join()
    print("Exiting program: %d (queue size)" % q.qsize())
    print("Elapsed Time: %s s" % (time.time() - start))



