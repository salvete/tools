'''
This is a utility used to locate the line of error based on panic
information.

Usage:
        python error_location.py  "path_openat+0x87/0x270" "fs/namei.o"

Output:
        /home/xxx/workplace/kernels/erofs-devel/fs/namei.c:3986
'''

import subprocess
import sys

def run_cmd(cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        if stderr:
                print('Exec command {} failed.', cmd[0])
                exit(-1)
        return stdout

def add(hex1, hex2):
        return hex(int(hex1, 16) + int(hex2, 16))

if __name__ == '__main__':
        if len(sys.argv) != 3:
                usage = '''
                        usage: python error_location.py <error_message> <compiled_object>
                        e.g.  python error_location.py  "path_openat+0x87/0x270" "fs/namei.o"
                        '''
                print(usage)
                sys.exit(1)
        disassemble = run_cmd(['objdump', '-d', sys.argv[2]])
        func_name = sys.argv[1][:sys.argv[1].find('+')]
        offset = sys.argv[1][sys.argv[1].find('+')+1:sys.argv[1].find('/')][2:]

        lines = disassemble.splitlines()
        base = None
        s = '<' + func_name + '>:'
        for line in lines:
                if s in line:
                        base = line[:line.find(' ')]

        if base is None:
                print('Can not find function `{}` in `{}`'.format(func_name, sys.argv[2]))
                sys.exit(1)

        print('[INFO] function_name:{}, base: 0x{}, offset: 0x{}'.format(func_name, base, offset))
        error_line = run_cmd(['addr2line', '-e', sys.argv[2], add(base, offset)])
        print('[ANSWER] The error line is: {}'.format(error_line))

