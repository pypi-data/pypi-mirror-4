from subprocess import Popen, PIPE

def _insert_ko(modprobe, modname):
    p = Popen([modprobe, modname], stderr=PIPE)
    p.wait()
    return (p.returncode, p.stderr.read(1024))

def _load_ko(modname):
    # this will return the full path for the modprobe binary
    proc = open("/proc/sys/kernel/modprobe")
    modprobe = proc.read(1024)
    if modprobe[len(modprobe) - 1] == '\n':
        modprobe = modprobe[:len(modprobe) - 1]
    return _insert_ko(modprobe, modname)

# Load a kernel module. If it is already loaded modprobe will just return 0.
def load_kernel(name):
    rc, err = _load_ko(name)
    if rc:
        if not err:
            err = "Failed to load the %s kernel module." % (name)
        if err[len(err) - 1] == "\n":
            err = err[:len(err) - 1]
        raise Exception(err)
