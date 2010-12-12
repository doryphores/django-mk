import math
EXTENDED_MAP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.'
EXTENDED_MAP_LENGTH = len(EXTENDED_MAP)

def chart_dataset(dataset):
	#function extendedEncode(arrVals, maxVal) {
	chart_data = ''
	
	max_value = 2000
	
	for value in dataset:
		# Scale the value to maxVal
		scaled_val = math.floor(EXTENDED_MAP_LENGTH * EXTENDED_MAP_LENGTH * value / max_value)
		
		if scaled_val > (EXTENDED_MAP_LENGTH * EXTENDED_MAP_LENGTH) - 1:
			chart_data += ".."
		elif scaled_val < 0:
			chart_data += '__'
		else:
			# Calculate first and second digits and add them to the output.
			quotient = int(math.floor(scaled_val / EXTENDED_MAP_LENGTH))
			remainder = int(scaled_val - EXTENDED_MAP_LENGTH * quotient)
			chart_data += EXTENDED_MAP[quotient] + EXTENDED_MAP[remainder]
		
	return chart_data