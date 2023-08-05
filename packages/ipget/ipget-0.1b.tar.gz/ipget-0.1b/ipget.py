
#import commands
import subprocess

class ipget:
	def __init__(self):
	#def ipgeter(self):	
		i =0
		old = []
		a = []
		self.flag = 0
		try :
			ifcon = subprocess.check_output(['ip', 'addr']).decode('utf-8')
			self.flag = 1
		except OSError:
			ifcon = subprocess.check_output(['ifconfig']).decode('utf-8')			
			self.flag = 2
		#ifcon =commands.getoutput("ip addr")
		outcom = ifcon.splitlines()
		#print (outcom)
		for j in (outcom):
			a = outcom[i].split(" ")
			while a.count("") > 0:
				a.remove("")
			#print a
			old = old + a
			i = i +1
		self.list = old
		#print self.list
	def ipaddr(self,st)	:
		st = st + ":"
		if self.flag == 1 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("inet") 	
				return self.list[num1+num2+1]
			except ValueError:
				return "0.0.0.0/0"
		elif self.flag == 2 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("\tinet") 	
				return self.list[num1+num2+1]
			except ValueError:
				return "0.0.0.0/0"
			return "0.0.0.0/0"
		else :
			return "0.0.0.0/0"
		
	def ipaddr6(self,st):
		st = st + ":"
		if self.flag == 1 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("inet6") 	
				return self.list[num1+num2+1]
			except ValueError:
				return "0:0:0:0:0:0:0:0/0"
		elif self.flag == 2 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("\tinet6") 	
				return self.list[num1+num2+1]
			except ValueError:
				return  "0:0:0:0:0:0:0:0/0"
		else :
			return "0:0:0:0:0:0:0:0/0"
	def mac(self,st):
		st = st + ":"
		if self.flag == 1 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("link/ether") 	
				return self.list[num1+num2+1]
			except ValueError:
				return "00:00:00:00:00:00"
		elif self.flag == 2 :	
			try :
				num1 = self.list.index(st)		
				num2 = self.list[num1:].index("\tether") 	
				return self.list[num1+num2+1]
			except ValueError:
				return  "00:00:00:00:00:00"
		else :
			return "00:00:00:00:00:00"
