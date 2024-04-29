import csv
import convertapi
def table_for_converting(list, path):

    with open(f'export.csv', encoding='utf-8', mode='w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['time', 'subject', 'place'])
        for i in list:
            writer.writerow(i)
    convertapi.api_secret = 'm79kk5eVwEENi0pB'
    convertapi.convert('pdf', {
        'File': 'export.csv'
    }, from_format='csv').save_files(path)
    print('converted')