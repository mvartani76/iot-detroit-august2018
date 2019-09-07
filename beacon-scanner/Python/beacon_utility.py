# function that accumulates the number of pings seen for different beacon minors
def accumulate_beacons(accumulation_dict, beacon_dict):
	for k, v in beacon_dict.items():
		if k in accumulation_dict:
			accumulation_dict[k] = accumulation_dict[k] + beacon_dict[k]
		else:
    			accumulation_dict[k] = v

	return accumulation_dict
