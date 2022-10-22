from dirsync import sync
import os
import re

src = list()
tgt = list()

def push_to_src(added_src):
    global src
    src.append(added_src)

def push_to_tgt(added_tgt):
    global tgt
    tgt.append(added_tgt)

def do_diff():
    run_sync(0)

def do_sync():
    run_sync(1)

def run_sync(mode):
    if len(src) != len(tgt):
        print(f"item number is not equal between src and tgt")
        exit()
    
    for i in range(len(src)):
        mount_dir = list()
        mount_dir.append(src[i])
        mount_dir.append(tgt[i])

        for j in range(len(mount_dir)):
            do_mount(mount_dir[j])

        if mode == 0:
            sync(src[i], tgt[i], r'diff')
        if mode == 1:
            sync(src[i], tgt[i], r'sync', verbose=True, purge=True, force=True)

        for j in range(len(mount_dir)):
            do_umount(mount_dir[j])

def do_mount(dir):
    result = chk_mntc_dir(dir)
    if (result):
        print(f"mount {result}")
        os.system(f"mount {result}")

def do_umount(dir):
    result = chk_mntc_dir(dir)
    if (result):
        print(f"umount {result}")
        os.system(f"umount {result}")

def chk_mntc_dir(dir):
    match = re.search(r'^\/mnt\/\w+', dir)
    if (match):
        if (match.group(0) != r'/mnt/c'):
            return match.group(0)
        else:
            return False
    else:
        return False
