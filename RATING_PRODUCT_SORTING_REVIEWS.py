# RATİNG PRODUCT & SORTİNG REVİEWS İN AMAZON

###############################################################
# PROJE AŞAMALARI
###############################################################
import pandas as pd
import datetime as dt
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_csv("datasets/amazon_review.csv")
df.head()
df.info()

#############################################
# GÖREV 1: Average Rating’i güncel yorumlara göre hesaplama ve var olan average rating ile kıyaslama:
#############################################

df["overall"].mean()  # ürünlerin rating ortalaması

df["reviewTime"].max()

# Puan Zamanlarına Göre Ağırlıklı Ortalama için:
df['reviewTime'] = pd.to_datetime(df['reviewTime'])  # inceleme zamanı
current_date = pd.to_datetime(str(df['reviewTime'].max())) # analiz tarihi
df["days"] = (current_date - df['reviewTime']).dt.days   # gün cinsinden bir yorum tarihi
df.head()

df["DAYS_SEGMENT"] = pd.qcut(df["days"], q=[0, .25, .5, .75, 1], labels=["A", "B", "C","D"])  # en uzak mesafe olana düşük oran
df["DAYS_SEGMENT"].value_counts()

df.loc[df["DAYS_SEGMENT"] == "A", "overall"].mean() * 28 / 100 + \
df.loc[df["DAYS_SEGMENT"] == "B", "overall"].mean() * 26 / 100 + \
df.loc[df["DAYS_SEGMENT"] == "C", "overall"].mean() * 24 / 100 + \
df.loc[df["DAYS_SEGMENT"]== "D", "overall"].mean() * 22 / 100

def time_based_weighted_average(dataframe, w1=28, w2=26, w3=24, w4=22):
    return dataframe.loc[dataframe["DAYS_SEGMENT"] == "A", "overall"].mean() * w1 / 100 + \
           dataframe.loc[dataframe["DAYS_SEGMENT"] == "B", "overall"].mean() * w2 / 100 + \
           dataframe.loc[dataframe["DAYS_SEGMENT"] == "C", "overall"].mean() * w3 / 100 + \
           dataframe.loc[dataframe["DAYS_SEGMENT"] == "D", "overall"].mean() * w4 / 100

time_based_weighted_average(df)  # 4.595593165128118
# df["overall"].mean(): 4.587589013224822

#############################################
# GÖREV 2: Ürün için ürün detay sayfasında görüntülenecek 20 review’i belirleme:
#############################################

# Ürün sayfasında görüntülenecek ilk 20 yorumu belirlemek istiyorsak kullanıcılar için en faydalı ve bilgilendirici içeriğin seçilmesi gerekir.
# Bunun için “helpful” değişkenini temsil ettiği şekilde “helpful_yes” ve “helpful_no” olarak ayrılması gerekiyor.
# Bu iki değişken sayesinde verilen toplam “total_vote” oy sayısını bulunur.

# 1. YOL:
def new(dataframe):
    new_helpful = dataframe["helpful"].str.split(pat=",", expand=True).astype("string")
    dataframe["helpful_yes"] = new_helpful[0].str.lstrip("[").astype("int")
    dataframe["total_vote"] = new_helpful[1].str.rstrip("]").astype("int")
    dataframe["helpful_no"] = dataframe["total_vote"] - dataframe["helpful_yes"]
    return dataframe["total_vote"], dataframe["helpful_yes"], dataframe["helpful_no"]
new(df)


# 2.YOL:
def new1(dataframe):
    from ast import literal_eval
    dataframe["helpful_yes"] = dataframe["helpful"].apply(lambda x: literal_eval(str(x).split(', ')[0].strip('['))).astype(int)
    dataframe["total_vote"] = dataframe["helpful"].apply(lambda x: literal_eval(str(x).split(', ')[1].strip(']'))).astype(int)
    dataframe["helpful_no"] = dataframe["total_vote"] - dataframe["helpful_yes"]
    return dataframe["helpful_no"], dataframe["total_vote"], dataframe["helpful_yes"]
new1(df)


# Score = (up ratings) − (down ratings)
def score_up_down_diff(up, down):
    return up - down

# score_pos_neg_diff
df["score_pos_neg_diff"] = df.apply(lambda x: score_up_down_diff(x["helpful_yes"], x["helpful_no"]), axis=1)

# Score = Average rating = (up ratings) / (all ratings)
def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up + down)

# score_average_rating
df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)


def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    # güven aralığı
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

# wilson_lower_bound
df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

a = df.sort_values("wilson_lower_bound", ascending=False).head(20)
a.iloc[:, [4, 5, 10, 11, 14, 15, 16, 17]]  # gerekli olan sütunlar seçildi.

#                                             reviewText  overall  helpful_yes  total_vote  helpful_no  score_pos_neg_diff  score_average_rating  wilson_lower_bound
# 2031  [[ UPDATE - 6/19/2014 ]]So my lovely wife boug...  5.00000         1952        2020          68                1884               0.96634             0.95754
# 3449  I have tested dozens of SDHC and micro-SDHC ca...  5.00000         1428        1505          77                1351               0.94884             0.93652
# 4212  NOTE:  please read the last update (scroll to ...  1.00000         1568        1694         126                1442               0.92562             0.91214
# 317   If your card gets hot enough to be painful, it...  1.00000          422         495          73                 349               0.85253             0.81858
# 4672  Sandisk announcement of the first 128GB micro ...  5.00000           45          49           4                  41               0.91837             0.80811
# 1835  Bought from BestBuy online the day it was anno...  5.00000           60          68           8                  52               0.88235             0.78465
# 3981  The last few days I have been diligently shopp...  5.00000          112         139          27                  85               0.80576             0.73214
# 3807  I bought this card to replace a lost 16 gig in...  3.00000           22          25           3                  19               0.88000             0.70044
# 4306  While I got this card as a "deal of the day" o...  5.00000           51          65          14                  37               0.78462             0.67033
# 4596  Hi:I ordered two card and they arrived the nex...  1.00000           82         109          27                  55               0.75229             0.66359
# 315   Bought this card to use with my Samsung Galaxy...  5.00000           38          48          10                  28               0.79167             0.65741
# 1465  I for one have not bought into Google's, or an...  4.00000            7           7           0                   7               1.00000             0.64567
# 1609  I have always been a sandisk guy.  This cards ...  5.00000            7           7           0                   7               1.00000             0.64567
# 4302  So I got this SD specifically for my GoPro Bla...  5.00000           14          16           2                  12               0.87500             0.63977
# 4072  I used this for my Samsung Galaxy Tab 2 7.0 . ...  5.00000            6           6           0                   6               1.00000             0.60967
# 1072  What more can I say? The 64GB micro SD works f...  5.00000            5           5           0                   5               1.00000             0.56552
# 2583  I bought this Class 10 SD card for my GoPro 3 ...  5.00000            5           5           0                   5               1.00000             0.56552
# 121   Update: providing an update with regard to San...  5.00000            5           5           0                   5               1.00000             0.56552
# 1142  As soon as I saw that this card was announced ...  5.00000            5           5           0                   5               1.00000             0.56552
# 1753  Puchased this card right after I received my S...  5.00000            5           5           0                   5               1.00000             0.56552


# Bütüne bakıp hangi değişken hangi türde bunu görerek bir yorum yapılması gerekiyor.
# Burada wilson_lower_bound, score_avg_ratingi kırptı. Çünkü olasılıksal bir sonuç olarak güven aralığında min değeri belirlemeli.
# Kırpmasaydı min değer o değer kabul edilmiş olacaktı.
# Bu da güven aralığına aykırı, score_avg_rating ortalama bir değer ama güven aralığının alt sınırını vermiyor.
# Wlb güveni sağlıyor ve %95 güven ile sonuç veriyor.

