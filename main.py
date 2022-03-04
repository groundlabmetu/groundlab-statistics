import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter
from collections import defaultdict
from helper import count_unique_iterable, filter_count, filter2, hashabledict, histogram, reverse_dict
from datetime import datetime
from simple_template import template
import pprint

plt.style.use("seaborn")

TOP_COUNT = 10
YONETIM = set([
    "ERDEM CANAZ",
    "TOLGA DEMİRDAL",
    "AHMET AKMAN",
    "BAŞAK BİRCAN",
    "BERA ALVAN",
    "BESTE ÖZTOP",
    "BURCU ŞAKIR",
    "DENİZ KARAKAY",
    "İLHAMİ	SELVİ",
    "IŞIK EMİR ALTUNKOY",
    "MEHMET CAN KAYASÖKEN",
    "YİĞİT SAYAR"
])


fields = ["Sıra", "Tarih", "No", "TC", "İsim", "Birim", "Kapı", "Mesaj", "Kart No"]
fields2 = ["Sıra", "Ad", "Soyad", "TC", "Numara", "Bölüm", "Dept", "Kart No", "Ünvan", "Çalıştığı yer"]
hooks = []


def hook(stat_func=None, flag=True, desc="", caption=""):
    def _fun(plot_func):
        hooks.append((desc, stat_func, plot_func, caption, flag))
        return plot_func
    return _fun


def generate():
    lst, lst2 = read_files()
    return template(open("template.ltex").read(), hooks=hooks, lst=lst, lst2=lst2, plt=plt)
    for desc, stat_func, plot_func, flag in hooks:
        stats = stat_func(lst, lst2)
        if flag:
            pprint.pprint(stats)
        plot_func(stats)
        plt.show()


def read_files(file_names=["c atölye kimler girdi.xls", "c atölye kimler giriş yapabiliyor.xls"]):
    frame = pd.read_excel(file_names[0])
    frame2 = pd.read_excel(file_names[1])
    lst = []
    for i in range(1, len(frame)):
        t = frame.iloc[i]
        lst.append(hashabledict(filter(lambda x: not pd.isna(x[1]), zip(fields, t))))
    lst2 = []
    for i in range(1, len(frame2)):
        t = frame2.iloc[i]
        lst2.append(hashabledict(filter(lambda x: not pd.isna(x[1]), zip(fields2, t))))

    return lst, lst2


def general_stats(lst, lst2):
    stats = {}
    stats["Toplam yetkili sayısı"] = len(lst2)
    stats["Toplam olay sayısı"] = len(lst)
    stats["Toplam giriş sayısı"] = filter_count(lst, "Mesaj", "İçeri Girdi")
    stats["Toplam çıkış sayısı"] = filter_count(lst, "Mesaj", "Butona Basılarak Dışarı Çıkıldı.")
    stats["Yetkisiz kart denemesi"] = filter_count(lst, "Mesaj", "Yetkisi Yok - Giremedi Kart No:", str.startswith)
    active_user_count = count_unique_iterable(map(itemgetter("İsim"), filter2(lst, "Mesaj", "İçeri Girdi")))
    stats["Aktif üye sayısı"] = active_user_count
    stats["Pasif üye sayısı"] = len(lst2) - active_user_count
    stats["Aktif üye oranı"] = active_user_count / len(lst2)
    return stats


@hook(general_stats, desc="Genel istatistikler", caption="Aktif ve pasif üye dağılımı grafiği")
def plot_general_stats(stats):
    plt.pie([stats["Aktif üye sayısı"], stats["Pasif üye sayısı"]], labels=["Aktif", "Pasif"], autopct="%1.1f%%")


def user_stats(lst, lst2):
    return histogram(map(itemgetter("İsim"), filter2(lst, "Mesaj", "İçeri Girdi")))


#hook(user_stats, desc="Kullanıcı istatistikleri")(None)


def histogram_stats(lst, lst2):
    return histogram(user_stats(lst, lst2).values())


@hook(histogram_stats, False, caption="Aktif üyelerin giriş sayısı histogramı")
def plot_histogram_stats(stats):
    plt.bar(list(sorted(map(str, stats.keys()), key=int)), list(stats.values()))


def range_hist_stats(lst, lst2, r=[0, 2, 5, 10, 20, 50, 100, 200]):
    stats = defaultdict(int)
    for k, v in histogram_stats(lst, lst2).items():
        for r_ in zip(r[:-1], r[1:]):
            if r_[0] < k <= r_[1]:
                stats[r_] += v
                break
    return stats


@hook(range_hist_stats, False, caption="Belli aralıklardaki giriş sayısı dağılımı")
def plot_range_hist_stats(stats):
    plt.pie(list(stats.values()), labels=list(map(str, stats.keys())), autopct="%1.1f%%")


def lesser_hist_stats(lst, lst2, r=[0, 2, 5, 10, 20, 50, 100, 200]):
    stats = defaultdict(int)
    for k, v in histogram_stats(lst, lst2).items():
        for r_ in r:
            if k <= r_:
                stats[r_] += v
    return dict(stats)


@hook(lesser_hist_stats, False, caption="Bir sayıdan az giriş sayısı dağılımı")
def plot_lesser_hist_stats(stats):
    plt.bar(list(map(str, stats.keys())), list(stats.values()))


def top_stats(lst, lst2):
    l = list(sorted(user_stats(lst, lst2).items(), key=itemgetter(1), reverse=True))
    limit = l[TOP_COUNT - 1][1]
    return list(filter(lambda x: x[1] >= limit, l))


@hook(top_stats, False, caption=f"En çok giriş yapan {TOP_COUNT} kullanıcının giriş sayıları")
def plot_top_stats(stats):
    plt.bar(list(range(len(stats))), list(map(itemgetter(1), stats)))


def user_entrance_stats(lst, lst2):
    stats = {}
    active_users = user_stats(lst, lst2)
    stats["Tüm üyelerin giriş ortalaması"] = sum(active_users.values()) / len(lst2)
    stats["Aktif üyelerin giriş ortalaması"] = sum(active_users.values()) / len(active_users)
    stats[f"En çok giriş yapan {TOP_COUNT} üyenin toplam giriş sayısı"] = sum(map(itemgetter(1), top_stats(lst, lst2)))
    stats["Diğer üyeler"] = filter_count(lst, "Mesaj", "İçeri Girdi") - sum(map(itemgetter(1), top_stats(lst, lst2)))
    return stats


@hook(user_entrance_stats, caption="En çok giriş yapan ve diğer üyelerin giriş dağılımı")
def plot_user_entrance_stats(stats):
    plt.pie([stats[f"En çok giriş yapan {TOP_COUNT} üyenin toplam giriş sayısı"], stats["Diğer üyeler"]], labels=[
            f"En çok giriş yapan {TOP_COUNT} üye", "Diğer üyeler"], autopct="%1.1f%%")


def yonetim_stats(lst, lst2):
    stats = {}
    top = set(map(itemgetter(0), top_stats(lst, lst2)))
    stats[f"En çok giriş yapan {TOP_COUNT} üyeden yönetimde olanların sayısı"] = len(top & YONETIM)
    stats[f"En çok giriş yapan {TOP_COUNT} üyeden yönetimde olmayanların sayısı"] = len(YONETIM) - len(top & YONETIM)
    return stats


@hook(yonetim_stats, desc="Yönetimde olan üyeler", caption="Yönetimde olan ve diğer üyelerin giriş sayıları")
def plot_yonetim_stats(stats):
    plt.pie([stats[f"En çok giriş yapan {TOP_COUNT} üyeden yönetimde olanların sayısı"],
             stats[f"En çok giriş yapan {TOP_COUNT} üyeden yönetimde olmayanların sayısı"]],
            labels=["Yönetimde", "Yönetimde Değil"], autopct="%1.1f%%")


def weekly_stats(lst, lst2):
    dates = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
                     map(itemgetter("Tarih"), filter2(lst, "Mesaj", "İçeri Girdi"))))
    return list(sorted(histogram(map(lambda date: f"{date.year}, \n{date.week}", map(datetime.isocalendar, dates))).items()))


@hook(weekly_stats, False, caption="Haftalık giriş sayıları")
def plot_weekly_stats(stats):
    plt.bar(list(map(itemgetter(0), stats)), list(map(itemgetter(1), stats)))


if __name__ == "__main__":
    print(generate(), file=open("out.tex", "w"))
