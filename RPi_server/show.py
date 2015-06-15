import datetime

with open('sensor_1.dat', 'r') as f:
    for line in f:
        print datetime.datetime.fromtimestamp(int(
                           float(line.split('\t')[0])))
