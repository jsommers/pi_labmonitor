#!/usr/bin/env python3

from subprocess import Popen, PIPE

def runcmd(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    output,errput = p.communicate()
    newoutput = ''
    for ch in output:
        if ch.isdigit() or ch == '.':
            newoutput += ch
    return float(newoutput)


# power1
power1 = runcmd("snmpget -mall -cpublic -v1 power1 -Ov .1.3.6.1.2.1.33.1.4.4.1.4.1")
print (power1)

# power3
power3 = runcmd("snmpget -mall -cpublic -v1 power3 -Ov .1.3.6.1.4.1.318.1.1.12.1.16.0")
print (power3)

# power4
power4 = runcmd("snmpget -mall -cpublic -v1 power4 -Ov .1.3.6.1.4.1.318.1.1.12.1.16.0")
print (power4)

# output volts/ac and amps -> compute watts directly
# power2
power2v = runcmd("snmpget -mall -cpublic -v1 power2 -Ov .1.3.6.1.4.1.850.10.2.3.1.1.7.1.62")
power2a = runcmd("snmpget -mall -cpublic -v1 power2 -Ov .1.3.6.1.4.1.850.10.2.3.1.1.7.1.69")
print (power2v*power2a)

