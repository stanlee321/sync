from subprocess import call
from time import sleep
from datetime import datetime

if __name__ == '__main__':
	# Log file
	datestring = datetime.now().__format__('%Y-%m-%d_%I%p')

    f = open('processLOG.txt', 'a')
    f.write('Starting HDR sequence.\n')
	f.write('Current Time: ' + datetime.now().isoformat())

	# Create the time lapse

    call(["python", "main.py",)
    f.write('Initialized Camera.\n')
    
    f.write('Wrote video\n.')
	f.write('Current Time: ' + datetime.now().isoformat())