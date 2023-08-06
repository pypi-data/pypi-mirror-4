#!/usr/local/bin/python
from fcntl import ioctl
from ctypes import *
import struct

#from sys/ioccom.h
IOC_VOID=0x20000000
IOCPARM_SHIFT=13
IOCPARM_MASK=(1<<IOCPARM_SHIFT)-1
#define SESIOC_GETNOBJ    _IO(SESIOC, 1)
def _IOC(inout,group,num,length):
	return inout|((length & IOCPARM_MASK)<<16)|(group<<8)|num
def _IO(g,n):
	return _IOC(IOC_VOID,g,n,0)

#from cam/scsi/scsi_ses.h
SESIOC=ord('s')-0o40
SESIOC_GETNOBJ   =_IO(SESIOC, 1)
SESIOC_GETOBJMAP =_IO(SESIOC, 2)
SESIOC_GETENCSTAT=_IO(SESIOC, 3)
SESIOC_SETENCSTAT=_IO(SESIOC, 4)
SESIOC_GETOBJSTAT=_IO(SESIOC, 5)
SESIOC_SETOBJSTAT=_IO(SESIOC, 6)
SESIOC_GETTEXT   =_IO(SESIOC, 7)
SESIOC_INIT      =_IO(SESIOC, 8)

OBJSTAT={
	0:'UNSUPPORTED',
	1:'OK',
	2:'CRITICAL',
	3:'NONCRITICAL',
	4:'UNRECOVERABLE',
	5:'NOTINSTALLED',
	6:'UNKNOWN',
	7:'UNAVAILABLE',
}

SESTYP={
	0x00:'UNSPECIFIED',
	0x01:'DEVICE',
	0x02:'POWER',
	0x03:'FAN',
	0x04:'THERM',
	0x05:'DOORLOCK',
	0x06:'ALARM',
	0x07:'ESCC',
	0x08:'SCC',
	0x09:'NVRAM',
	0x0b:'UPS',
	0x0c:'DISPLAY',
	0x0d:'KEYPAD',
	0x0e:'ENCLOSURE',
	0x0f:'SCSIXVR',
	0x10:'LANGUAGE',
	0x11:'COMPORT',
	0x12:'VOM',
	0x13:'AMMETER',
	0x14:'SCSI_TGT',
	0x15:'SCSI_INI',
	0x16:'SUBENC',
	0x17:'ARRAY',
	0x18:'SASEXPANDER',
	0x19:'SASCONNECTOR',
}
ENCSTAT={
	0x0:'OK',
	0x1:'UNRECOVERABLE',
	0x2:'CRITICAL',
	0x4:'NONCRITICAL',
	0x8:'INFO',
}
class Object(object):
	"""SES2 object - represents things like array slots, fans, sensors, power supplies, etc"""
	def __init__(self,data,sesdev):
		self.obj_id,self.subencid,self.object_type,null,null=data
		self.sesdev=sesdev

	@property
	def type(self):
		"""the type of ses object (ARRAY, FAN, etc)"""
		return SESTYP[self.object_type]

	def __str__(self):
		return "<%-12s %2d %2d (0x%02x 0x%02x 0x%02x 0x%02x)>"%(
			self.type,
			self.obj_id,
			self.subencid,
			self.statdata[0]
			,self.statdata[1],
			self.statdata[2],
			self.statdata[3]
		)

	def updatestatus(self):
		"""refresh all of this object's status information"""
		self.statdata=self.sesdev.getobjstat(self.obj_id)[1:]

	@property
	def status(self):
		"""general ses object status - returns array of statuses"""
		return OBJSTAT[self.statdata[0]&0xF]
	
	@property
	def ident(self):
		return not self.statdata[2]&0x02==0

	@ident.setter
	def ident(self,value=True):
		"""control the led indicator on an object (currently only ARRAY objects)"""
		if self.type=='ARRAY':
			if value=="toggle":
				self.updatestatus()
				self.sesdev.setobjstat(self.obj_id,(0x80,0x00,self.statdata[2]^0x02,0x00))
			elif value:
				self.sesdev.setobjstat(self.obj_id,(0x80,0x00,0x02,0x00))
			else:
				self.sesdev.setobjstat(self.obj_id,(0x80,0x00,0x00,0x00))
		else:
			return False

		self.updatestatus()
		return True

	@property
	def fanrpm(self):
		"""speed of a FAN element in RPM"""
		if self.type!='FAN':
			return None
		return ((self.statdata[1]&0x07)<<8)+(self.statdata[2]&0xFF)*10
	
	@property
	def fanspeed(self):
		"""requested speed of a FAN element (range 0-7)"""
		if self.type!='FAN':
			return None
		return self.statdata[3]&0x07

	#TODO: currently seems to just shut off the fans for a few seconds, then back to full speed
	#@fanspeed.setter
	#def fanspeed(self,speed):
	#	if self.type!='FAN':
	#		raise Exception('Set fan speed on device that is not a fan')
	#	if speed>0x07 or speed<0:
	#		raise Exception('Invalid fan speed specified')
	#	self.sesdev.setobjstat(self.obj_id,(0x80,self.statdata&0x80,0x00,speed))

	@property
	def temperature(self):
		"""temperature of a THERM element (in celcius)"""
		if self.type!='THERM':
			return None
		return self.statdata[2]-20



class Enclosure(object):
	"""main SES2 enclosure device"""
	def __init__(self,device='/dev/ses0'):
		self.devfile=device
		self.open()
	
	def open(self):
		"""open the device file (uses device specified in constructor, or the devfile property)"""
		self.dev=open(self.devfile,'wb')

	def close(self):
		"""close the device file"""
		self.dev.close()

	@property
	def obj_count(self):
		"""number of ses objects on this device"""
		return struct.unpack("I",ioctl(self.dev,SESIOC_GETNOBJ,struct.pack('I',0)))[0]

	@property
	def status(self):
		"""overall status of the enclosure"""
		s=struct.unpack("B",ioctl(self.dev,SESIOC_GETENCSTAT,struct.pack('B',0)))[0]
		r=[]
		for i in ENCSTAT:
			if i&s:
				r.append(ENCSTAT[i])
		if not r:
			r.append(ENCSTAT[0])
		return r

	def getobjstat(self,obj_id):
		"""get raw object status data (used by ses Object)"""
		objstat_struct='iBBBB'
		return struct.unpack(objstat_struct,ioctl(
			self.dev,
			SESIOC_GETOBJSTAT,
			struct.pack(objstat_struct,obj_id,0,0,0,0))
		)
	
	def setobjstat(self,obj_id,data):
		"""set raw object status data (used by ses Object)"""
		data=struct.pack('iBBBB',obj_id,data[0],data[1],data[2],data[3])
		ioctl(self.dev,SESIOC_SETOBJSTAT,data)

	@property
	def objects(self):
		"""list of objects (with current status)"""
		#get ses object data
		nobj=self.obj_count
		sesobj_struct='iBBBB'
		sesobj_size=struct.calcsize(sesobj_struct)
		data=ioctl(self.dev,SESIOC_GETOBJMAP,struct.pack(sesobj_struct,0,0,0,0,0)*nobj)

		r=[]
		for i in range(0,nobj):
			objdata=struct.unpack(sesobj_struct,data[i*sesobj_size:i*sesobj_size+sesobj_size])
			obj=Object(objdata,self)
			obj.updatestatus()
			r.append(obj)
		return r

#def main():
#	enc=Enclosure()
#	print enc.status
#	obj=enc.objects
#	obj[0].ident("toggle")
#	obj[0].updatestatus()
#	for i in obj:
#		print i,i.status,i.fanrpm,i.temperature

#if __name__=='__main__':
#	main()
