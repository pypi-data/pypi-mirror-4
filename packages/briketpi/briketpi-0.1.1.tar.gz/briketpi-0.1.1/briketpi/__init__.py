#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
from timeout import timeout, TimeoutError
import yaml
import logging

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# to use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BCM) # Using GPIO input numbers
GPIO.setwarnings(False)

# logging
log = logging.getLogger('briket')

class Briket(object):

	def __init__(self, ioconfig):
		log.debug('__init__')
		self.config			= ioconfig
		self.porta			= Component(self.config['porta'])
		self.pisto			= Component(self.config['pisto'])
		self.premsa			= Component(self.config['premsa'])
		self.alimentador	= Component(self.config['alimentador'])

		# inicialitzem posicio
		log.debug('__init__.tirar_enrere')
		self.tirar_enrere()
		time.sleep(1)
		log.debug('__init__.baixar_porta')
		self.baixar_porta()
		time.sleep(1)

	def __repr__(self):
		return '<Briketadora Pi>'
		
	def __str__(self):
		return 'Briket'

	def stop(self):
		self.porta.stop()
		self.pisto.stop()
		self.premsa.stop()
		self.alimentador.stop()

	@property
	def estat(self):
		return """
Estat de la briquetadora:
	Porta: %s
	Pistó: %s
	Premsa: %s
	Alimentador: %s
""" % (self.porta.estat, self.pisto.estat, self.premsa.estat, self.alimentador.estat)

	def baixar_porta(self):
		self.porta.tancar()
		
	def pujar_porta(self):
		self.porta.obrir()
		
	def tirar_enrere(self):
		self.pisto.obrir()
		
	def mini_tirar_enrere(self):
		self.pisto.obrir(timeout=1)
		
	def empenyer_briketa(self, delay=None):
		self.pisto.tancar(delay)
		
	def premsar_briketa(self):
		self.premsa.tancar(delay=4)
		
	def tirar_virutes(self):
		self.alimentador.obrir(timeout=3)
		
	def mas_madera(self):
		self.tirar_enrere()
		time.sleep(1)
		self.tirar_virutes()
		self.premsar_briketa()
		time.sleep(1)
		
	def mainloop(self, runconfig):
		
		if not runconfig:
			raise NoRunConfigException

		num_briquetes = runconfig['num_briquetes']
		
		self.baixar_porta()
		time.sleep(1)
		
		#if not netejar:
		#	self.tirar_virutes()
		self.tirar_virutes()
					
		self.premsar_briketa()
		time.sleep(1)
		
		for _ in range(num_briquetes-1):
			self.mas_madera()
		
		self.mini_tirar_enrere()
		time.sleep(1)
		
		self.pujar_porta()
		time.sleep(1)
		
		self.empenyer_briketa(num_briquetes-1)
		time.sleep(1)
		
		self.baixar_porta();		
		time.sleep(1)
		
		self.tirar_enrere();
		time.sleep(1)		
	
	
class Component(object):
	
	def __init__(self, input_config):
		self.config				= input_config
		self.nom 				= input_config['nom']
		self.endswitch_obert	= input_config['port_finaldelinia_obert']
		self.endswitch_tancat	= input_config['port_finaldelinia_tancat']
		self.actuador_obrir		= input_config['port_actuador_obrir']
		self.actuador_tancar	= input_config['port_actuador_tancar']

		# definim endswitches com a IN
		GPIO.setup(self.endswitch_obert, GPIO.IN)
		GPIO.setup(self.endswitch_tancat, GPIO.IN)
		# # definim actuadors com a OUT
		GPIO.setup(self.actuador_obrir, GPIO.OUT)
		GPIO.setup(self.actuador_tancar, GPIO.OUT)
		# # No se si és necessari, pero per si de cas resettejem la sortida
		GPIO.output(self.actuador_obrir, True)  # Els pins estan muntats al reves
		GPIO.output(self.actuador_tancar, True) # Els pins estan muntats al reves

	def __repr__(self):
		return '<Briket Component: %s>' % self.nom

	def __str__(self):
		return '%s' % self.nom

	def stop(self):
		GPIO.output(self.actuador_obrir, True)  # Els pins estan muntats al reves
		GPIO.output(self.actuador_tancar, True) # Els pins estan muntats al reves

	def obrir(self, timeout = None, delay = None):
		self.actuar(tout=timeout, delay=delay, finsque='self.obert', actuador=self.actuador_obrir)
	
	def tancar(self, timeout = None, delay = None):
		self.actuar(tout=timeout, delay=delay, finsque='self.tancat', actuador=self.actuador_tancar)

	def actuar(self, tout, delay, finsque, actuador):
		# print 'estat: %s: %s' % (finsque, eval(finsque))
		if eval(finsque):
			return
		@timeout(tout)
		def doloop(self):
			try:
				GPIO.output(actuador, False)  # test, al reves
				log.debug('esperant %s %s' % (self.nom, finsque))
				while not eval(finsque):
					# print 'estat: %s' % self.estat
					pass
			except TimeoutError:
				pass
			finally:
				log.debug('condicions satisfetes')
				if delay:
					log.debug('aplicant delay de %s s' % delay)
					time.sleep(delay)
				GPIO.output(actuador, True) # test, al reves
		doloop(self)
		
	@property
	def is_endswitch_obert(self):
		return True if GPIO.input(self.endswitch_obert) else False
		# return True if self.endswitch_obert else False

	@property
	def is_endswitch_tancat(self):
		return True if GPIO.input(self.endswitch_tancat) else False
		# return True if self.endswitch_tancat else False
		
	@property
	def obert(self):
		return self.is_endswitch_obert and not self.is_endswitch_tancat
		
	@property
	def tancat(self):
		return not self.is_endswitch_obert and self.is_endswitch_tancat

	@property
	def estat(self):
		if self.is_endswitch_obert:
			if not self.is_endswitch_tancat:
				return 'Obert'
			return 'Obert i Tancat'
		elif self.is_endswitch_tancat:
			return 'Tancat'
		else:
			return 'Ni Obert ni Tancat'
		
		
class NoRunConfigException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def main():
	ioconfig = yaml.safe_load(open('ioconfig.yaml'))
	brik = Briket(ioconfig)

	print brik.pisto
	print brik.premsa.estat

if __name__ == '__main__':
	main()
