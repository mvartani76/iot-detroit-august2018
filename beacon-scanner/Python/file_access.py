import os

class FileAccess(object):
	def __init__(self):
		self.exitcode = 9999
		self.exitfile = "exit_file.txt"

	# Initialize FileAccess Object
	def init_file_access(self):
		exitcode = 0
	# Function that checks to see if exit file exists and if it does, sets the appropriate code
	def readExitFileAndSetCode(self):
		print(self.exitfile)
		if os.path.isfile(self.exitfile):
			exit_file = open(self.exitfile,"r")
			self.exitcode = exit_file.readline()
			exit_file.close()
		else:
			self.exitcode = 0
	# Function that writes the appropriate exit code depending on where the code exited
	def writeExitCode(self, exitcode):
		exit_file = open(self.exitfile,"w")
		exit_file.write(str(exitcode))
		exit_file.close()

