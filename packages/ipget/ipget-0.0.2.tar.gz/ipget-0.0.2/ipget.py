
import commands

class ipget:
	def __init__(self):
	#def ipgeter(self):	
		i =0
		old = []
		ifcon =commands.getoutput("ip addr")
		outcom = ifcon.splitlines()
		for j in outcom:
			new = outcom[i].split(' ')
			while new.count("") > 0:
				new.remove("")
			#print new
			old = old + new
			i = i +1
		self.list = old
		#print self.list
	def ipaddr(self,st):
		st = st + ":"
		num1 = self.list.index(st)		
		num2 = self.list[num1:].index("inet") 	
		return self.list[num1+num2+1]
	def ipaddr6(self,st):
		st = st + ":"
		num1 = self.list.index(st)		
		num2 = self.list[num1:].index("inet6") 	
		return self.list[num1+num2+1]
	def mac(self,st):
		st = st + ":"
		num1 = self.list.index(st)		
		num2 = self.list[num1:].index("link/ether") 	
		return self.list[num1+num2+1]

