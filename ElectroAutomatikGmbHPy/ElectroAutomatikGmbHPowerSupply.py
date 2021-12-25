import minimalmodbus
import pandas

# [1] Programming Guide ModBus & SCPI For USB, GPIB, Ethernet and AnyBus modules, Programming_ModBus_SCPI_KE220_REV15_EN.pdf.

def calculate_crc(packet_without_crc):
	"""Calculates the Modbus CRC bits that have to be added to the packet."""
	packet_encoded = ''.join([chr(c) for c in packet_without_crc])
	crc_as_string = minimalmodbus._calculate_crc_string(packet_encoded)
	return list(bytes(crc_as_string.encode('latin1')))

def create_modbus_packet(function: int, register_address: int, data: list):
	if function not in {1,3,5,6}:
		raise ValueError(f'`function` is not a valid value. Received {repr(function)}.')
	if not isinstance(register_address, int) or not 0 <= register_address < 2**16:
		raise ValueError(f'`register_address` must be an integer number between 0 and 2**16, received {repr(register_address)} of type {type(register_address)}.')
	if not isinstance(data, list) or any([not isinstance(d,int) for d in data]) or any([not 0 <= d < 2**8 for d in data]):
		raise ValueError(f'`data` must be a list containing 8 bit integers, i.e. integers between 0 and 2**8. Received {data} which contains elements not satisfying this.')
	packet = [0x00] # Must always be 0, see [1].
	packet += [function]
	packet += [register_address>>8, register_address&0xff]
	packet += data
	packet += calculate_crc(packet)
	return packet

class ElectroAutomatikGmbHPowerSupply:
	def __init__(self, port: str):
		self.power_supply = minimalmodbus.Instrument(
			port = port,
			slaveaddress = 0,
			# ~ debug = True,
			allow_broadcast_address = True,
		)
		self.register_list_df = pandas.read_csv('register_list.csv').set_index('description')
		self.remote_mode(True)

	def read(self, description: str):
		"""Read data from the device."""
		if description not in self.register_list_df.index:
			raise ValueError(f'{repr(description)} not found in the available registers. Available options are: {sorted(self.register_list_df.index)}.')
		data_type = self.register_list_df.loc[description, 'data type']
		if data_type == 'char':
			return self.power_supply.read_string(
				registeraddress = int(self.register_list_df.loc[description, 'modbus address']), 
				number_of_registers = int(self.register_list_df.loc[description, 'data length in bytes']/2),
			)
		elif data_type == 'uint16':
			return self.power_supply.read_register(
				registeraddress = int(self.register_list_df.loc[description, 'modbus address']),
			)
		elif data_type == 'uint32':
			return self.power_supply.read_long(
				registeraddress = int(self.register_list_df.loc[description, 'modbus address']),
			)
		elif data_type == 'float':
			return self.power_supply.read_float(
				registeraddress = int(self.register_list_df.loc[description, 'modbus address']),
			)
		else:
			raise NotImplementedError(f'Not implemented read data of type {repr(data_type)}.')
	
	def write(self, description: str, data):
		"""Write data to the device."""
		if description not in self.register_list_df.index:
			raise ValueError(f'{repr(description)} not found in the available registers. Available options are: {sorted(self.register_list_df.index)}.')
		data_type = self.register_list_df.loc[description, 'data type']
		if data_type == 'uint16':
			if not isinstance(data, int) or not 0 <= data < 2**16:
				raise ValueError(f'{repr(description)} is of type `uint16` but received {repr(data)} which does not match this data type.')
			self.power_supply.write_register(
				registeraddress = int(self.register_list_df.loc[description, 'modbus address']),
				value = data,
				functioncode = 0x06, # [1] § 4.8.3.
			)
		else:
			raise NotImplementedError(f'Not implemented read data of type {repr(data_type)}.')
	
	def write_single_coil(self, register_address: int, value: bool):
		"""Write 0x0000 (False) or 0xff00 (True) to a single coil."""
		# See [1] § 4.8.3, unfortunately these guys are out of the ModBus standard so this cannot be done with minimalmodbus package.
		if value not in {True, False}:
			raise ValueError(f'`value` must be either True or False.')
		if not isinstance(register_address, int) or not 0 <= register_address < 2**16:
			raise ValueError(f'`register_address` must be an integer number between 0 and 2**16, received {repr(register_address)} of type {type(register_address)}.')
		packet = create_modbus_packet(
			function = 5, # [1] § 4.8.4.
			register_address = register_address,
			data = [0xff,0x00] if value==True else [0x00,0x00],
		)
		self.power_supply.serial.write(packet)
	
	def remote_mode(self, enable: bool):
		"""Enable or disable remote control."""
		if enable not in {True, False}:
			raise ValueError(f'`enable` must be True or False.')
		self.write_single_coil(
			register_address = int(self.register_list_df.loc['remote mode', 'modbus address']),
			value = enable,
		)
	
	@property
	def idn(self):
		"""Returns a string with information about the manufacturer, device model and serial number."""
		return self.read('manufacturer') + ', ' + self.read('device type') + ', serial No. ' + self.read('serial number')
	
	@property
	def nominal_voltage(self):
		"""Returns the nominal voltage in Volt as a float number."""
		return self.read('nominal voltage')
	
	@property
	def nominal_current(self):
		"""Returns the nominal current in Ampere as a float number."""
		return self.read('nominal current')
	
	@property
	def measured_voltage(self):
		"""Returns the measured voltage in Volt as a float number."""
		return self.nominal_voltage*self.read('actual voltage')/0xcccc # [1] § 4.4.
	
	@property
	def measured_current(self):
		"""Returns the measured current in Ampere as a float number."""
		return self.nominal_current*self.read('actual current')/0xcccc # [1] § 4.4.
	
	@property
	def set_voltage_value(self):
		"""Returns the set voltage in Volt as a float number."""
		return self.nominal_voltage*self.read('set voltage value')/0xcccc # [1] § 4.4.
	@set_voltage_value.setter
	def set_voltage_value(self, Volt):
		"""Set the set voltage in Volt."""
		if not isinstance(Volt, (float, int)):
			raise TypeError(f'`Volt` must be a float number, received object of type {type(Volt)}.')
		if not 0 <= Volt <= self.nominal_voltage:
			raise ValueError(f'`Volt` must be between 0 and {self.nominal_voltage:.2f} V. Received {Volt}.')
		self.write(
			description = 'set voltage value',
			data = int(0xcccc*Volt/self.nominal_voltage),
		)
	
	@property
	def set_current_value(self):
		"""Returns the set current in Ampere as a float number."""
		return self.nominal_current*self.read('set current value')/52428 # [1] § 4.4.
	@set_current_value.setter
	def set_current_value(self, Ampere):
		"""Set the set current in Ampere."""
		if not isinstance(Ampere, (float, int)):
			raise TypeError(f'`Ampere` must be a float number, received object of type {type(Ampere)}.')
		if not 0 <= Ampere <= self.nominal_current:
			raise ValueError(f'`Ampere` must be between 0 and {self.nominal_current:.2f} A. Received {Ampere}.')
		self.write(
			description = 'set current value',
			data = int(0xcccc*Ampere/self.nominal_current),
		)
	
	@property
	def is_remote(self):
		"""Returns True if remote control is enabled, false otherwise."""
		return True if (self.read('device state') & 1<<11) != 0 else False

if __name__ == '__main__':
	ps = ElectroAutomatikGmbHPowerSupply('/dev/ttyACM3')
	
	print(ps.register_list_df)
	
	print(f'Connected with {ps.idn}')
	print(f'Is remote control enabled? {ps.is_remote}')
	print(f'Switching to manual mode...')
	ps.remote_mode(False)
	print(f'Is remote control enabled? {ps.is_remote}')
	print(f'Going back to remote...')
	ps.remote_mode(True)
	print(f'Is remote control enabled? {ps.is_remote}')
	voltage = 1.2
	current = 1.5
	print(f'Setting voltage to {voltage} V and current to {current} A...')
	ps.set_voltage_value = voltage
	ps.set_current_value = current
	print(f'Set voltage is {ps.set_voltage_value:.2f} V and set current is {ps.set_current_value:.2f} A.')
	
