import sys

if __name__ == '__main__':
    if len(sys.argv)<2:
        print('No args passed')

    elif len(sys.argv) == 2:
        print(f'Running using > {sys.argv[1]}')