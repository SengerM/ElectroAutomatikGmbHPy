# ElectroAutomatikGmbHPy

Control devices from Electro Automatik GmbH from Python easily. This package was developed for and only tested with an [EA-PS 5040-20 A](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/dc-laboratory-power-supplies/series-ps-5000-br-160-up-to-640-w/705/laboratory-power-supply-0..40v/0..20a/320w) connected via USB to a Ubuntu 20.04 computer. 

![Picture of the power supply that I am working with](https://elektroautomatik.com/shop/media/image/44/da/7b/ps5000a.jpg)

## Installation

Should be as easy as 
```
pip install git+https://github.com/SengerM/ElectroAutomatikGmbHPy
```

You also need to install a modified version of the minimalmodbus package, see [About ModBus protocol and Electro Automatik equipment](#about-modbus-protocol-and-electro-automatik-equipment).

## Usage

The following script performs some common tasks:

```Python
from ElectroAutomatikGmbHPy.ElectroAutomatikGmbHPowerSupply import ElectroAutomatikGmbHPowerSupply
import time
	
ps = ElectroAutomatikGmbHPowerSupply(port='/dev/ttyACM3') # https://unix.stackexchange.com/a/144735/317682

ps.enable_output(False) # Switch off the output.
time.sleep(1) # Wait for transients.

print(f'Connected with {ps.idn}') # Prints the name of the device.
print(f'Is remote control enabled? {ps.is_remote}') # Should be, because it is automatically changed to remote when the connection is open.
print(f'Switching to manual mode...') # Just for testing purposes.
ps.remote_mode(False)
print(f'Is remote control enabled? {ps.is_remote}') # Should print "False".
print(f'Going back to remote...')
ps.remote_mode(True)
print(f'Is remote control enabled? {ps.is_remote}')
voltage = 1.2
current = 1.5
print(f'Setting voltage to {voltage} V and current to {current} A...')
ps.set_voltage_value = voltage # Change the `set voltage`.
ps.set_current_value = current # Change the `set current`.
print(f'Set voltage is {ps.set_voltage_value:.2f} V and set current is {ps.set_current_value:.2f} A.') # Should print the values just set.
print(f'Measured voltage and current is: {ps.measured_voltage:.2f} V, {ps.measured_current:.2f} A, output is {ps.output}.') # Should print 0 because the output is off.
input(f'Press enter to turn the output on...')
ps.enable_output(True) # Turn the output on.
time.sleep(1) # Wait for transients.
print(f'Measured voltage and current is: {ps.measured_voltage:.2f} V, {ps.measured_current:.2f} A, output is {ps.output}.') # Should print some values.
print(f'Turning output off...')
ps.enable_output(False) # Turn output off again.
time.sleep(1) # Wait for transients.
print(f'Measured voltage and current is: {ps.measured_voltage:.2f} V, {ps.measured_current:.2f} A, output is {ps.output}.') # Should print 0.
```

## About ModBus protocol and Electro Automatik equipment

The [EA-PS 5040-20 A](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/dc-laboratory-power-supplies/series-ps-5000-br-160-up-to-640-w/705/laboratory-power-supply-0..40v/0..20a/320w) power supply (the one that I am using) communicates using the [ModBus RTU](https://en.wikipedia.org/wiki/Modbus#Modbus_RTU_frame_format_(primarily_used_on_asynchronous_serial_data_lines_like_RS-485/EIA-485)) protocol through USB interface. There are [a number of packages available in Python to work with the ModBus protocol](https://stackoverflow.com/questions/17081442/python-modbus-library). For simplicity I decided to work with [minimalmodbus](https://pypi.org/project/minimalmodbus/). Unfortunately the manufacturer of this power supply is not 100 % within the ModBus protocol; and in section 4.1 of the programming guide¹ they say

> With the release of certain KE firmware versions in 2020 there has been a modification to make our devices fully compliant to the ModBus specification. In order to remain compatible to already existing softwares on the control side (PC, PLC etc.) the compliance can be switched with register 10013 between "Full" and "Limited" (default), whereas "Limited" is the condition of the previous
firmwares, so there is no unexpected impact after an update. Differences:
> 
> • "Full" supports slave addresses 0 and 1 and returns READ COIL functions correctly
> 
> • "Limited" only supports address 0, so activating mode "Full" requires to send the message
> 
> to address 0
> 
> [...]
> 
> A message or telegram as defined by the ModBus RTU protocol consists of hexadecimal bytes of which the first byte, the ModBus (slave) address, can only be 0 or 1 because our devices don't need an adjustable address. The 1 is furthermore only accepted by the device if compliance mode "Full" has been activated. If not, it only supports address 0 is supported for compatibility to older firmwares, so 0 must be used then. The first byte of a telegram is used to distinguish between ModBus and SCPI. A value between 2 and 41 in the first byte will cause a ModBus communication error, whereas from 42 (ASCII character: *) the telegram is considered as text message, means as an SCPI command.

This makes it harder to control the devices with *KE firmware versions* prior to 2020 (mine is 2017). I have found a workaraound by doing some small modifications to the [minimalmodbus](https://pypi.org/project/minimalmodbus/) package to work, but this is non standard and has to be taken into account in case of future development. I have made [my own fork of minimalmodbus](https://github.com/SengerM/minimalmodbus) and the commit with wich this is working is [ef2f0fdaf791d626c7942dd3770d9a430bd182c7](https://github.com/SengerM/minimalmodbus/tree/ef2f0fdaf791d626c7942dd3770d9a430bd182c7).

## References

¹ File *Programming_ModBus_SCPI_REV20_EN.pdf* within [this zip file](https://elektroautomatik.com/shop/media/archive/41/cb/55/Programming_Guide_USB_IF-AB-XX_de_en.zip) downloadable from [the website of the manufacturer](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/dc-laboratory-power-supplies/series-ps-5000-br-160-up-to-640-w/705/laboratory-power-supply-0..40v/0..20a/320w). Document title *Programming Guide, ModBus & SCPI For USB, GPIB, Ethernet and AnyBus modules*, Doc ID: PGMBEN, Revision: 20, Date: 10-25-2021.
