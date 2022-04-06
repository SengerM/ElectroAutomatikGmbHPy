# ElectroAutomatikGmbHPy

Control devices from Electro Automatik GmbH from Python easily. This package was developed for and only tested with an [EA-PS 5040-20 A](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/dc-laboratory-power-supplies/series-ps-5000-br-160-up-to-640-w/705/laboratory-power-supply-0..40v/0..20a/320w) connected via USB to a Ubuntu 20.04 computer. 

![Picture of the power supply that I am working with](https://elektroautomatik.com/shop/media/vector/cb/g0/17/ea-elektroautomatik_section_bg_01.svg)

## Installation

Should be as easy as 
```
pip install git+https://github.com/SengerM/ElectroAutomatikGmbHPy
```

## Usage

The following script performs some common tasks:

```Python
from ElectroAutomatikGmbHPy.ElectroAutomatikGmbHPowerSupply import ElectroAutomatikGmbHPowerSupply
import time
	
ps = ElectroAutomatikGmbHPowerSupply(port='/dev/ttyACM3') # https://unix.stackexchange.com/a/144735/317682
# Check also the function find_elektro_automatik_devices defined in the __init__.py file to automatize the port-finding.

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
