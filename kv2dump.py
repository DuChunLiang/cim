

#data = open('kvaser_fmg.log')
data = open('CAN_ERR_DATA.txt')

count = 0
for line in data:

	s = line.split()

	channel = s[0]
	can_id_str = s[1]
	can_id = int(can_id_str, 16)


	if(can_id ==0) :
		continue	#Skip Error Frame

	if(can_id&0x000000ff == 0x01):
		continue	#Skip source address is 0x01

	len = int(s[3])
	idx_time = len + 4

	# s[4] is data[0]
	out = "(" + s[idx_time] + ")" +" "
	out = out + "can" + channel + " " + can_id_str + "#"

	for i in range(0, len):
		out = out + s[4+i]

	count = count +1
#	print count

	print(out)

