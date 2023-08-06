import sys
import kernel
import os
from deiman.deiman import Deiman


def main():
    args = ('start', 'stop', 'status', 'logfile', 'test', 'help')
    app_name = 'raid_guard'
    d = Deiman("/tmp/%s.pid" % app_name)
    if len(sys.argv) == 1 or sys.argv[1] not in args:
        print("Usage: %s %s" % (app_name,list(args)))
        sys.exit(2)
    opt = sys.argv[1]
    
    if opt == 'start':
        d.start()
        print('Check status with: raid_guard status')
        g = kernel.Guard()
        g.start_daemon()
        
    elif opt== 'stop':
        d.stop()
        sys.exit(0)
        
    elif opt == 'status':
        print('daemon status is:')
        d.status()
        print('')
        print('For more information use: raid_guard logfile')
        print('Get help with: raid_guard help')
        sys.exit(0)
        
    elif opt == 'test':
        kernel.run_test()
        sys.exit()
        
    elif opt == 'help':
        print(os.system('cat /usr/share/raid_guard/README.rst'))
        sys.exit()
        
    elif opt == 'logfile':
        if os.path.isfile('/var/log/raid_guard.log'):
            print(os.system('cat /var/log/raid_guard.log'))
        else:
            print('Actual no log file.')
        sys.exit()