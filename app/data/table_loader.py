import csv
def view(abspath):
    with open(abspath, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        return list(reader)
