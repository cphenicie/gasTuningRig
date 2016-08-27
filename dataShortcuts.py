import csv

# Write a CSV file composed of 2 columns of data
def writeCSV(fileName, data, labels):
    dataFile = open(fileName, 'wb')
    writer = csv.writer(dataFile)
    writer.writerow(labels)
    for row in range(len(data[1])):
        writer.writerow(tuple(col[row] for col in data))
    dataFile.close()