from datetime import datetime


date_format = '%d.%m.%Y %H:%M:%S'

with open('data/2024_07_lvs_new.csv', 'w') as fout:
    for dataline in open('data/2024_07_lvs_data.csv', 'r').readlines()[1:]:
        #print(dataline.split(";")[1])
        timestamp = datetime.strptime(dataline.split(";")[1], date_format).timestamp()
        dataline = f"{timestamp:.0f};{";".join(dataline.split(";")[1:])}"

        fout.write(dataline)