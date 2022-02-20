from numpy import nan
import pandas as pd


fields = ["Sıra", "Tarih", "No", "TC", "İsim", "Birim", "Kapı", "Mesaj", "Kart No"]
fields2 = ["Sıra", "Ad", "Soyad", "TC", "Numara", "Bölüm", "Dept", "Kart No", "Ünvan", "Çalıştığı yer"]


def read_files(file_names=["c atölye kimler girdi.xls", "c atölye kimler giriş yapabiliyor.xls"]):
    frame = pd.read_excel(file_names[0])
    frame2 = pd.read_excel(file_names[1])
    lst = []
    for i in range(1, len(frame)):
        t = frame.iloc[i]
        lst.append(dict(filter(lambda x: not pd.isna(x[1]), zip(fields, t))))
    lst2 = []
    for i in range(1, len(frame2)):
        t = frame2.iloc[i]
        lst2.append(dict(filter(lambda x: not pd.isna(x[1]), zip(fields2, t))))

    return lst, lst2
