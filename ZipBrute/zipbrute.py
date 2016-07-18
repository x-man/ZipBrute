#!/usr/bin/env python
#--coding:utf-8--

import zipfile,threading,os,time,sys,Queue
from optparse import OptionParser
from lib.consle_width import getTerminalSize

is_found = False
pwd = ''

class ZipBrute(object):
	def __init__(self,target,threads_sum):
		self.target = target
		self.thread_count = self.threads_sum = threads_sum
		self.found = False
		self.getPass()
		self.lock = threading.Lock()
		self.console_width = getTerminalSize()[0] - 2    # Cal terminal width when starts up

	def getPass(self):
		self.queue = Queue.Queue()
		with open('pass.txt') as f:
			for line in f:
				self.queue.put(line.strip())
		self.total = self.queue.qsize()

	def print_progress(self):
		self.lock.acquire()
		msg = 'total %s | remaining %s | try %s in %.2f seconds' %(self.total,self.queue.qsize(),self.total-self.queue.qsize(),time.time() - self.start_time)
		sys.stdout.write('\r' + '-' * (self.console_width -len(msg)) + msg)
		sys.stdout.flush()
		self.lock.release()

	def brute(self):
		global is_found,pwd
		while self.queue.qsize()>0 and not self.found:
			self.print_progress()
			zip = zipfile.ZipFile(self.target, "r",zipfile.zlib.DEFLATED)
			try:
				password = self.queue.get(timeout=1.0)
				zip.extractall(path='',members=zip.namelist(),pwd=password)
				zip.close()
				is_found = self.found = True
				pwd = password
				return None
			except Exception,e:
				pass

	def run(self):
		self.start_time = time.time()
		for i in range(self.threads_sum):
			t = threading.Thread(target=self.brute,name=str(i))
			t.setDaemon(True)
			t.start()

if __name__=='__main__':
	print 'Zip File brute tool v1.0'

	parser = OptionParser('usage: %prog [options] target.com')
	parser.add_option('-t','--threads',dest='threads_sum',default=60,type='int',help='number of threads.default is 60')
	(options,args) = parser.parse_args()
	
	if len(args)<1:
		parser.print_help()
		sys.exit(0)

	z = ZipBrute(target=args[0],threads_sum=options.threads_sum)
	z.run()
	while threading.activeCount()>1:
		time.sleep(0.1)
	if is_found==True:
		print
		print '-----success,The password is %s' %pwd
	else:
		print
		print '-----failed,no password for the zip file'