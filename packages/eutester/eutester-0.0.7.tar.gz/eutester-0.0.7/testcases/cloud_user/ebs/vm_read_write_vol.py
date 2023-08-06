#!/usr/bin/python

import time,sys
import argparse
import os
import select

parser = argparse.ArgumentParser( prog='write_volume.py', description='write data to file to verify data integrity')
parser.add_argument('-f', dest='testfile', help="file to read", default="/root/testfile")
parser.add_argument('-b', dest='bytes', help="bytes to write", default=1000)

args = parser.parse_args()
bytes= int(args.bytes)
testfile = args.testfile
readrate = "0"
writerate = "0"
lr=""
timeout=2
procfile = "/proc/sys/vm/drop_caches"
print "Starting read/write test, bytes:"+str(bytes)+", file:"+str(testfile)
time.sleep(1)
f=open(testfile, 'w')
try:
    while True:
        wlength = 0
        start = time.time()
        for x in xrange(0,bytes):
            print "\r\x1b[K Writing:"+str(x)+", Rate:"+writerate+" bytes/sec, Lastread:"+str(lr)+", READ Rate:"+readrate+" bytes/sec",
            xstr = x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x
	    xstr = str(xstr).lstrip('(').rstrip(')')+"\n"
	    sys.stdout.flush()
            f.write(xstr)
            wlength += len(str(xstr)) 
            if x and not x % 1:
                f.flush()
                os.fsync(f.fileno())
                time.sleep(.001)
                elapsed= time.time()-start
                writerate = str("%.2f" % (wlength / elapsed))
            f.flush()
            os.fsync(f.fileno())
        elapsed= time.time()-start
        writerate = str("%.2f" % (wlength / elapsed))
        elapsed = time.time() - start
        f.close()
        #Now do the read
        readin = ''
        leftover = ''
        length = 0
        last = 0
        proc = open(procfile,'w')
        proc.write('3')
        proc.flush()
        proc.close()
        #f = os.open(testfile, os.O_DIRECT | os.O_RD)
        f=open(testfile, 'r')
        readstart = start = time.time()
        while True:
            reads, _, _ = select.select([f.fileno()], [], [], 0)
            elapsed = int(time.time()-start)
            if elapsed >= timeout:
                    raise Exception("Could not read from file in timeout:"+str(elapsed))
            time.sleep(.1)
            
            if len(reads) > 0:
                start = time.time()
                readin  = f.read(1024)
                if not readin:
                    break
                while readin:
                    if not readin:
                        break    
                    length += len(readin)
                    readin = leftover + readin
                    #add any data not contained within a complete newline from last read() to this cycle...
                    leftover = readin.endswith('\n')
                    lines = readin.splitlines()
                    #if our last line wasn't a complete new line,save it for next read cycle...
                    if not leftover:
                        leftover = lines.pop()
                    for x in lines:
                        print "\r\x1b[K Reading:"+str(x)+",",
                        sys.stdout.flush()
                        cur = int(x.split(',')[0])
			lr = str(cur) 
                        if cur != 0 and cur != (last + 1):
                            raise Exception('bad incremented in value, last:'+str(last)+" vs cur:"+str(cur))
                        last = cur
                        cur = 0
                    readin = f.read(1024)
        if length != wlength:
            raise Exception("Read length:"+str(length)+" != written length:"+str(wlength)+",Diff:"+str(length-wlength))
        elapsed = time.time() - start
        readrate = str("%.2f" % (length / elapsed))
        rbuf = '\n\nREAD Rate:'+readrate +" bytes/sec\n\n"
        f.close()
        f=open(testfile, 'w')
finally:
    f.close()
