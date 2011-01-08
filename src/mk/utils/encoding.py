import math
EXTENDED_MAP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.'
EXTENDED_MAP_LENGTH = len(EXTENDED_MAP)

def chart_dataset(dataset):
	#function extendedEncode(arrVals, maxVal) {
	chart_data = ''
	
	max_value = 2000
	
	chart_value = '__'
	
	for value in dataset:
		if value is not None:
			# Scale the value to maxVal
			scaled_val = math.floor(EXTENDED_MAP_LENGTH * EXTENDED_MAP_LENGTH * value / max_value)
			
			if scaled_val > (EXTENDED_MAP_LENGTH * EXTENDED_MAP_LENGTH) - 1:
				chart_value = ".."
			elif scaled_val < 0:
				chart_value = '__'
			else:
				# Calculate first and second digits and add them to the output.
				quotient = int(math.floor(scaled_val / EXTENDED_MAP_LENGTH))
				remainder = int(scaled_val - EXTENDED_MAP_LENGTH * quotient)
				chart_value = EXTENDED_MAP[quotient] + EXTENDED_MAP[remainder]
		else:
			chart_value = '__'
				
		chart_data += chart_value
		
	return chart_data