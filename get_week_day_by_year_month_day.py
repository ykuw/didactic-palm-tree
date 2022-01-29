
def weekDay(year, month, day):
	offset = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
	week = [
		"Sunday",
		"Monday",
		"Tuesday",
		"Wednesday",
		"Thursday",
		"Friday",
		"Saturday",
	]
	afterFeb = 1
	if month > 2:
		afterFeb = 0
	aux = year - 1700 - afterFeb
	# dayOfWeek for 1700/1/1 = 5, Friday
	dayOfWeek = 5
	# partial sum of days betweem current date and 1700/1/1
	dayOfWeek += (aux + afterFeb) * 365
	# leap year correction
	dayOfWeek += aux // 4 - aux // 100 + (aux + 100) // 400
	# sum monthly and day offsets
	dayOfWeek += offset[month - 1] + (day - 1)
	dayOfWeek %= 7
	return week[dayOfWeek]


get_year = int(input("Enter year (4 digits): "))
get_month = int(input("Enter month (2 digit): "))
get_day = int(input("Enter day (2 digit): "))

print(weekDay(get_year, get_month, get_day))

# print (weekDay(1978, 10, 3) == (2, 'Tuesday'))
# print (weekDay(2013, 6, 15) == (6, 'Saturday'))
# print (weekDay(1969, 7, 20) == (0, 'Sunday'))
# print (weekDay(1945, 4, 30) == (1, 'Monday'))
# print (weekDay(1900, 1, 1)  == (1, 'Monday'))
# print (weekDay(1789, 7, 14) == (2, 'Tuesday'))
