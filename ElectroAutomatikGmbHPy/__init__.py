import serial.tools.list_ports

def find_elektro_automatik_devices():
	"""Automatically finds all serial port devices by the manufacturer
	"Elektro-Automatik" and returns a list of dictionaries of the form
	```
	[
		{'manufacturer': str, 'description': str, 'port': str, 'serial_number': str}, # Device 1
		{'manufacturer': str, 'description': str, 'port': str, 'serial_number': str}, # Device 2
		...
	]
	```
	"""
	return [{'manufacturer': p.manufacturer, 'description': p.description, 'port': p.device, 'serial_number': p.serial_number} for p in serial.tools.list_ports.comports() if 'Elektro-Automatik' in p.manufacturer]
