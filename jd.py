#coding=utf-8
import os
import sys
import zipfile
from multiprocessing import Pool
import string
import random
import subprocess
import time
import shutil

src = r'E:\Projects\penetration\test'
dist = 'dist'
tempdir = 'temp'
logfile = open('jd.log', 'a')
timeout = 100
workQueue = []
failjars = []

def walkdir(srcfolder):
    if not os.path.isdir(srcfolder): 
        raise Exception('source folder is not exist!')
        sys.exit()
    for filepath, dirs, files in os.walk(srcfolder):
        for f in files:
            if f.endswith('.jar'):
                workQueue.append(os.path.join(filepath, f))
            elif f.endswith('.war'):
                unpackwar(filepath, f)
        for d in dirs:
            if d == 'classes' and filepath.endswith('WEB-INF'):
                packjar(os.path.join(filepath, d))



def unpackwar(filepath, f):
    with zipfile.Zipfile(os.path.join(filepath, f), 'r') as z:
        namelist = [i for i in z.namelist() if i.endswith('.class')]
        if len(namelist):
            tempWarPath = os.path.join(tempdir, 'wars', idgenerator())
            z.extractall(tempWarPath, namelist)
            
            packjar(os.path.join(tempWarPath, 'WEB-INF', 'classes'))
            

        namelist = [i for i in z.namelist() if i.endswith('.jar')]
        if len(namelist):
            tempJarPath = os.path.join(temp, 'jars')
            z.extractall(tempJarPath, namelist)
            for i in namelist:
                workQueue.append(os.path.join(tempJarPath, i))

def packjar(path):
    directory = os.path.join(tempdir, 'jars')
    if not os.path.exists(directory):
        os.makedirs(directory)

    distjar = os.path.abspath(os.path.join(directory, idgenerator() + '.jar'))
    try:
        child = subprocess.Popen(['jar', 'cf', distjar, '*'], cwd=path, stdout=logfile, stderr=logfile)
        child.wait(timeout)
        workQueue.append(distjar)
        print('Successful to create jar: %s' % distjar)
    except:
        print('Fail to create jar: %s' % distjar)

def idgenerator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def decompile(jar):
    try:
        child = subprocess.Popen(['java', '-jar', 'jd-cli.jar', '-n','-od', dist, jar], stdout=logfile, stderr=logfile)
        child.wait(timeout)
        print('Decompile jar successfully: %s' % jar)
    except:
        print('Decompile jar fail: %s' % jar)
        failjars.append(jar)

def clean():
    if os.path.isdir(tempdir): shutil.rmtree(tempdir)


def main():
    begin = time.time()

    clean()
    walkdir(src)

    walktime = time.time()

    with Pool(processes = 4) as pool:
        pool.map(decompile, workQueue)

    # clean()
    logfile.close()
    end = time.time()
    print('Cost %s seconds to walk the source folder.' % (walktime - begin))
    print('Cost %s seconds to run the task.' % (end - begin))

if __name__ == '__main__':
    main()