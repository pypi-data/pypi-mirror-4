
#import commands
import subprocess

class ipget:
	def __init__(self):
	#def ipgeter(self):	
		i =0
		old = []
		a = []
		try :
			ifcon = subprocess.check_output(['ip', 'addr']).decode('utf-8')
		except OSError:
			ifcon = subprocess.check_output(['ifconfig']).decode('utf-8')			
		#ifcon =commands.getoutput("ip addr")
		outcom = ifcon.splitlines()
		#print (outcom)
		for j in (outcom):
			a = outcom[i].split(" ")
			while a.count("") > 0:
				a.remove("")
			#print new
			old = old + a
			i = i +1
		self.list = old
		#print self.list
	def ipaddr(self,st)	:
		try :
			st = st + ":"
			num1 = self.list.index(st)		
			num2 = self.list[num1:].index("inet") 	
			return self.list[num1+num2+1]
		except ValueError:
			return "0.0.0.0/0"
	def ipaddr6(self,st):
		try :		
			st = st + ":"
			num1 = self.list.index(st)		
			num2 = self.list[num1:].index("inet6") 	
			return self.list[num1+num2+1]
		except ValueError:
			return "0:0:0:0:0:0:0:0/0"
	def mac(self,st):
		try :		
			st = st + ":"
			num1 = self.list.index(st)		
			num2 = self.list[num1:].index("link/ether") 	
			return self.list[num1+num2+1]
		except ValueError:
			return "00:00:00:00:00:00"
