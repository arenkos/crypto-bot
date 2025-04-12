import time
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import talib as ta
import math

symbol = "BTC/USDT"
symbolName = "BTC"

"""
Eski
# API CONNECT
exchange = ccxt.binance({
    "apiKey": 'UxOGz3LdaWBfnviCQKcYJu2S2X4HTTPf5ojZiJqGri5niYTjgwQsrtEvkpTJwOr5',
    "secret": 'CTF2uovc7pm4NeGwBqzKZaT5Qk5ohiGXp3HqYrx16lfKPQM67v8TRvZkk0UBd4Re',

    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})
"""

# API CONNECT
exchange = ccxt.binance({
    "apiKey": 'G2dI1suDiH3bCKo1lpx1Ho4cdTjmWh9eQEUSajcshC1rcQ0T1yATZnKukHiqo6IN',
    "secret": 'ow4J1QLRTXhzuhtBcFNOUSPq2uRYhrkqHaLri0zdAiMhoDCfJgEfXz0mSwvgpnPx',

    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})



def lim_olustur(zamanAraligi):
    lst = []
    lim = 0
    for i in zamanAraligi:
        lst.append(i)

    def convert(s):
        # initialization of string to ""
        new = ""

        # traverse in the string
        for x in s:
            new += x

            # return string
        return new

    periyot = ""
    mum = ""
    if lst[len(lst) - 1] == 'm':
        list = convert(lst)
        a = list.split("m")
        mum = a[0]
        lim = 365 * (float(mum) * 60 * 24)
        bekleme = int(a[0]) * 60
        periyot = "%M"
    elif lst[len(lst) - 1] == 'h':
        list = convert(lst)
        a = list.split("h")
        mum = a[0]
        lim = 365 * (float(mum) * 24)
        bekleme = int(a[0]) * 60 * 60
        periyot = "%H"
    elif lst[len(lst) - 1] == 'd':
        list = convert(lst)
        a = list.split("d")
        mum = a[0]
        lim = 365 * float(mum)
        bekleme = int(a[0]) * 60 * 60 * 24
        periyot = "%d"
    elif lst[len(lst) - 1] == 'w':
        list = convert(lst)
        a = list.split("w")
        mum = a[0]
        lim = 52 * float(mum)
        bekleme = int(a[0]) * 60 * 60 * 24 * 7
    lim = lim * 1
    return lim

adf_1m = [[0 for x in range(1441)] for y in range(366)]
adf_3m = [[0 for x in range(481)] for y in range(366)]
adf_5m = [[0 for x in range(289)] for y in range(366)]
adf_15m = [[0 for x in range(97)] for y in range(366)]
adf_30m = [[0 for x in range(49)] for y in range(366)]
adf_1h = [[0 for x in range(25)] for y in range(366)]
adf_2h = [[0 for x in range(13)] for y in range(366)]
adf_4h = [[0 for x in range(7)] for y in range(366)]
adf_1d = [[0 for x in range(2)] for y in range(366)]

df_1m = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_3m = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_5m = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_15m = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_30m = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_1h = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_2h = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_4h = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
df_1d = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

a = 0
start_date = int(datetime(2022, 7, 15, 3, 0, 0).timestamp() * 1000)
while a < 365:
    print(a)
    bars = exchange.fetch_ohlcv(symbol, timeframe="1m", since=start_date, limit=1440)
    adf_1m[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="3m", since=start_date, limit=480)
    adf_3m[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="5m", since=start_date, limit=288)
    adf_5m[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="15m", since=start_date, limit=96)
    adf_15m[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="30m", since=start_date, limit=48)
    adf_30m[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="1h", since=start_date, limit=24)
    adf_1h[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="2h", since=start_date, limit=12)
    adf_2h[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="4h", since=start_date, limit=6)
    adf_4h[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    bars = exchange.fetch_ohlcv(symbol, timeframe="1d", since=start_date, limit=1)
    adf_1d[a] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"]) 
    start_date = start_date + 86400000
    a = a + 1

a = 0
while a < 365:
    df_1m = pd.concat([df_1m, adf_1m[a]], ignore_index=True)
    df_3m = pd.concat([df_3m, adf_3m[a]], ignore_index=True)
    df_5m = pd.concat([df_5m, adf_5m[a]], ignore_index=True)
    df_15m = pd.concat([df_15m, adf_15m[a]], ignore_index=True)
    df_30m = pd.concat([df_30m, adf_30m[a]], ignore_index=True)
    df_1h = pd.concat([df_1h, adf_1h[a]], ignore_index=True)
    df_2h = pd.concat([df_2h, adf_2h[a]], ignore_index=True)
    df_4h = pd.concat([df_4h, adf_4h[a]], ignore_index=True)
    df_1d = pd.concat([df_1d, adf_1d[a]], ignore_index=True)
    a = a + 1
    
bars = exchange.fetch_ohlcv(symbol, timeframe="1w", since=None, limit=int(lim_olustur("1w")))
df_1w = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

def deneme(zamanAraligi, df):
    print("Supertrend ve Hacim BOT\n\n")
    alinacak_miktar = 0
    bekleme = 0
    bakiye = 100.0
    leverage_ust = 50
    lev_ust = 50
    yuzde_ust = 50
    yuz_ust = 50
    islemsonu = [[0 for x in range(yuz_ust * 2 + 1)] for y in range(lev_ust + 1)]
    son = 0
    islem = 0
    basarili = 0
    basarili_islem = [[0 for x in range(yuz_ust * 2 + 1)] for y in range(lev_ust + 1)]
    basarisiz = 0
    basarisiz_islem = [[0 for x in range(yuz_ust * 2 + 1)] for y in range(lev_ust + 1)]
    yuzde = 0.5
    sonuclar = []
    tahmin = []
    
    lim = int(len(df["open"]))
        
    kesisim = False
    longPozisyonda = False
    shortPozisyonda = False
    pozisyondami = False
    likit = 0
    yuzde = 0.5
    a = 0
    def generateSupertrend(close_array, high_array, low_array, atr_period, atr_multiplier):
        try:
            atr = ta.ATR(high_array, low_array, close_array, atr_period)
        except ccxt.BaseError as Error:
            print("[ERROR] ", Error)

        previous_final_upperband = 0
        previous_final_lowerband = 0
        final_upperband = 0
        final_lowerband = 0
        previous_close = 0
        previous_supertrend = 0
        supertrend = []
        supertrendc = 0

        for i in range(0, len(close_array)):
            if np.isnan(close_array[i]):
                pass
            else:
                highc = high_array[i]
                lowc = low_array[i]
                atrc = atr[i]
                closec = close_array[i]

                if math.isnan(atrc):
                    atrc = 0

                basic_upperband = (highc + lowc) / 2 + atr_multiplier * atrc
                basic_lowerband = (highc + lowc) / 2 - atr_multiplier * atrc

                if basic_upperband < previous_final_upperband or previous_close > previous_final_upperband:
                    final_upperband = basic_upperband
                else:
                    final_upperband = previous_final_upperband

                if basic_lowerband > previous_final_lowerband or previous_close < previous_final_lowerband:
                    final_lowerband = basic_lowerband
                else:
                    final_lowerband = previous_final_lowerband

                if previous_supertrend == previous_final_upperband and closec <= final_upperband:
                    supertrendc = final_upperband
                else:
                    if previous_supertrend == previous_final_upperband and closec >= final_upperband:
                        supertrendc = final_lowerband
                    else:
                        if previous_supertrend == previous_final_lowerband and closec >= final_lowerband:
                            supertrendc = final_lowerband
                        elif previous_supertrend == previous_final_lowerband and closec <= final_lowerband:
                            supertrendc = final_upperband

                supertrend.append(supertrendc)

                previous_close = closec

                previous_final_upperband = final_upperband

                previous_final_lowerband = final_lowerband

                previous_supertrend = supertrendc

        return supertrend

    opn = df["open"]
    high = df["high"]
    low = df["low"]
    clse = df["close"]

    close_array = np.asarray(clse)
    high_array = np.asarray(high)
    low_array = np.asarray(low)
    
    close_array = close_array.astype(float)
    high_array = high_array.astype(float)
    low_array = low_array.astype(float)
    supertrend = generateSupertrend(close_array, high_array, low_array, atr_period=10, atr_multiplier=3)
    # Yüzde döngüsü
    while yuzde <= yuzde_ust:
        stop = 0
        likit = 0
        leverage = 1
        
        # Kaldıraç döngüsü
        while leverage <= leverage_ust:
            bakiye = 100.0
            x = 3
            stop = 0
            likit = 0
            # Supertrend indikatörü ve hacim kullanılarak girilen işlemler ana kısım
            while x < lim:
                depo = 0
                son_kapanis = close_array[x - 2]
                onceki_kapanis = close_array[x - 3]
                son_supertrend_deger = supertrend[x - 2]
                onceki_supertrend_deger = supertrend[x - 3]
                # Renk yeşile dönüyor, Supertrend yükselişe geçti
                if son_kapanis > son_supertrend_deger and onceki_kapanis < onceki_supertrend_deger:
                    islem = islem + 1
                    print("")
                    print("Sinyal Long")
                    print("Bakiye = " + str(bakiye))
                    print("Kaldıraç = " + str(leverage))
                    print("Yüzde = " + str(yuzde))
                    print(datetime.fromtimestamp(int(df['timestamp'][x]) / 1000))
                    print("")
                    giris = float(df["open"][x])
                    y = 0
                    while True:
                        son_kapanis = close_array[x + y - 2]
                        onceki_kapanis = close_array[x + y - 3]
                        son_supertrend_deger = supertrend[x + y - 2]
                        onceki_supertrend_deger = supertrend[x + y - 3]
                        
                        # Likit olma durumu
                        if ((float(df["low"][x + y]) - giris) / giris * 100 <= (-1) * (90 / float(leverage))):
                            print("Likit")
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            bakiye = 0
                            likit = 1
                            basarisiz = basarisiz + 1
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        # Sinyal ile çıkış durumu
                        if son_kapanis < son_supertrend_deger and onceki_kapanis > onceki_supertrend_deger:
                            son = bakiye + bakiye * (float(df["open"][x + y]) - giris) / giris * leverage
                            if son < bakiye:
                                basarisiz = basarisiz + 1
                            else:
                                basarili = basarili + 1
                            bakiye = bakiye + bakiye * (float(df["open"][x + y]) - giris) / giris * leverage
                            print("Sinyal ile kapandı. Bakiye = " + str(bakiye))
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            print("")
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        # Stop olma durumu
                        if ((float(df["high"][x + y]) - giris) / giris * 100 >= yuzde):
                            basarili = basarili + 1
                            bakiye = bakiye + bakiye * yuzde / 100 * leverage
                            stop = 1
                            print("Stop ile kapandı. Bakiye = " + str(bakiye))
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            print("")
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        y = y + 1
                        
                        # Dizi sonunda döngüden çıkılsın
                        if (x + y) == lim:
                            depo = x + y - 2
                            break   

                # Renk kırmızıya dönüyor, Supertrend düşüşe geçti
                elif son_kapanis < son_supertrend_deger and onceki_kapanis > onceki_supertrend_deger:
                    islem = islem + 1
                    print("")
                    print("Sinyal Short")
                    print("Bakiye = "+ str(bakiye))
                    print("Kaldıraç = " + str(leverage))
                    print("Yüzde = " + str(yuzde))
                    print(datetime.fromtimestamp(int(df['timestamp'][x]) / 1000))
                    print("")
                    giris = float(df["open"][x])
                    y = 0
                    while True:
                        son_kapanis = close_array[x + y - 2]
                        onceki_kapanis = close_array[x + y - 3]
                        son_supertrend_deger = supertrend[x + y - 2]
                        onceki_supertrend_deger = supertrend[x + y - 3]
                        
                        # Likit olma durumu
                        if ((float(df["high"][x + y]) - giris) / giris * 100 >= (90 / float(leverage))):
                            print("Likit")
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            bakiye = 0
                            likit = 1
                            basarisiz = basarisiz + 1
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        # Sinyal ile çıkış durumu
                        if son_kapanis > son_supertrend_deger and onceki_kapanis < onceki_supertrend_deger:
                            son = bakiye + bakiye * (float(df["open"][x + y]) - giris) / giris * (-1) * leverage
                            if son < bakiye:
                                basarisiz = basarisiz + 1
                            else:
                                basarili = basarili + 1
                            bakiye = bakiye + bakiye * (float(df["open"][x + y]) - giris) / giris * (-1) * leverage
                            print("Sinyal ile kapandı. Bakiye = " + str(bakiye))
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            print("")
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        # Stop olma durumu
                        if ((float(df["low"][x + y]) - giris) / giris * 100 <= yuzde * (-1)):
                            basarili = basarili + 1
                            bakiye = bakiye + bakiye * yuzde / 100 * leverage
                            stop = 1
                            print("Stop ile kapandı. Bakiye = " + str(bakiye))
                            print(datetime.fromtimestamp(int(df['timestamp'][x + y]) / 1000))
                            print("")
                            if y == 0:
                                x = x + y
                            else:
                                x = x + y - 1
                            break
                        
                        y = y + 1
                        
                        # Dizi sonunda döngüden çıkılsın
                        if (x + y) == lim:
                            depo = x + y - 2
                            break
                
                x = x + 1
                
                # Likit durumu dizi döngüsünden çıkılsın
                if likit == 1:
                    leverage_ust = leverage
                    break
                    
            islemsonu[int(leverage - 1)][a] = bakiye
            basarili_islem[int(leverage - 1)][a] = basarili
            basarisiz_islem[int(leverage - 1)][a] = basarisiz
            
            # Likit olduysa kaldıraç döngüsünden çıkılsın
            if likit == 1:
                leverage_ust = leverage
                while leverage < lev_ust:
                    islemsonu[int(leverage)][a] = 0
                    basarili_islem[int(leverage)][a] = 0
                    basarisiz_islem[int(leverage)][a] = 0
                    leverage = leverage + 1
                break
            basarili = 0
            basarisiz = 0
            leverage = leverage + 1
            
            # Stop çalışmadıysa yüzde döngüsünden çıkılsın
            if stop == 0:
                break
        lev = leverage_ust
            
        # Stop çalışmadıysa yüzde döngüsünden çıkılsın
        if stop == 0:
            yuzde_ust = yuzde
            while leverage_ust < lev_ust:
                b = a
                while b < yuz_ust * 2:
                    islemsonu[int(leverage_ust)][b] = 0
                    basarili_islem[int(leverage_ust)][b] = 0
                    basarisiz_islem[int(leverage_ust)][b] = 0
                    b = b + 1
                leverage_ust = leverage_ust + 1
            break
        yuzde = yuzde + 0.5
        a = a + 1
        leverage_ust = lev - 1
    
    leverage = 0
    while leverage < lev_ust:
        tahmin.append(max(islemsonu[leverage]))
        leverage = leverage + 1
    leverage = 0    
    while leverage < lev_ust:
        k = 1
        while k <= len(islemsonu[leverage]):
            if islemsonu[int(leverage)][int(k - 1)] == max(tahmin):
                return str(leverage + 1), str(k / 2), basarili_islem[leverage][k - 1], basarisiz_islem[leverage][k - 1], str(islemsonu[int(leverage)][int(k - 1)])
            k = k + 1
        leverage = leverage + 1

m1 = deneme("1m", df_1m)
m3 = deneme("3m", df_3m)
m5 = deneme("5m", df_5m)
m15 = deneme("15m", df_15m)
m30 = deneme("30m", df_30m)
h1 = deneme("1h", df_1h)
h2 = deneme("2h", df_2h)
h4 = deneme("4h", df_4h)
d1 = deneme("1d", df_1d)
w1 = deneme("1w", df_1w)

lev_1m = m1[0]
lev_3m = m3[0]
lev_5m = m5[0]
lev_15m = m15[0]
lev_30m = m30[0]
lev_1h = h1[0]
lev_2h = h2[0]
lev_4h = h4[0]
lev_1d = d1[0]
lev_1w = w1[0]

yuz_1m = m1[1]
yuz_3m = m3[1]
yuz_5m = m5[1]
yuz_15m = m15[1]
yuz_30m = m30[1]
yuz_1h = h1[1]
yuz_2h = h2[1]
yuz_4h = h4[1]
yuz_1d = d1[1]
yuz_1w = w1[1]

bli_1m = m1[2]
bli_3m = m3[2]
bli_5m = m5[2]
bli_15m = m15[2]
bli_30m = m30[2]
bli_1h = h1[2]
bli_2h = h2[2]
bli_4h = h4[2]
bli_1d = d1[2]
bli_1w = w1[2]

bsiz_1m = m1[3]
bsiz_3m = m3[3]
bsiz_5m = m5[3]
bsiz_15m = m15[3]
bsiz_30m = m30[3]
bsiz_1h = h1[3]
bsiz_2h = h2[3]
bsiz_4h = h4[3]
bsiz_1d = d1[3]
bsiz_1w = w1[3]

bky_1m = m1[4]
bky_3m = m3[4]
bky_5m = m5[4]
bky_15m = m15[4]
bky_30m = m30[4]
bky_1h = h1[4]
bky_2h = h2[4]
bky_4h = h4[4]
bky_1d = d1[4]
bky_1w = w1[4]

f = open(str(symbolName) + "1.txt", "w")
f.write("1m Kaldıraç = " + str(lev_1m) + " Yüzde = " + str(yuz_1m) + " Başarılı İşlem = " + str(bli_1m) + " Başarısız İşlem = " + str(bsiz_1m) +  " İşlem Sonu Bakiye = " + str(bky_1m) + "\n")
f.write("3m Kaldıraç = " + str(lev_3m) + " Yüzde = " + str(yuz_3m) + " Başarılı İşlem = " + str(bli_3m) + " Başarısız İşlem = " + str(bsiz_3m) +  " İşlem Sonu Bakiye = " + str(bky_3m) + "\n")
f.write("5m Kaldıraç = " + str(lev_5m) + " Yüzde = " + str(yuz_5m) + " Başarılı İşlem = " + str(bli_5m) + " Başarısız İşlem = " + str(bsiz_5m) +  " İşlem Sonu Bakiye = " + str(bky_5m) + "\n")
f.write("15m Kaldıraç = " + str(lev_15m) + " Yüzde = " + str(yuz_15m) + " Başarılı İşlem = " + str(bli_15m) + " Başarısız İşlem = " + str(bsiz_15m) +  " İşlem Sonu Bakiye = " + str(bky_15m) + "\n")
f.write("30m Kaldıraç = " + str(lev_30m) + " Yüzde = " + str(yuz_30m) + " Başarılı İşlem = " + str(bli_30m) + " Başarısız İşlem = " + str(bsiz_30m) +  " İşlem Sonu Bakiye = " + str(bky_30m) + "\n")
f.write("1h Kaldıraç = " + str(lev_1h) + " Yüzde = " + str(yuz_1h) + " Başarılı İşlem = " + str(bli_1h) + " Başarısız İşlem = " + str(bsiz_1h) +  " İşlem Sonu Bakiye = " + str(bky_1h) + "\n")
f.write("2h Kaldıraç = " + str(lev_2h) + " Yüzde = " + str(yuz_2h) + " Başarılı İşlem = " + str(bli_2h) + " Başarısız İşlem = " + str(bsiz_2h) +  " İşlem Sonu Bakiye = " + str(bky_2h) + "\n")
f.write("4h Kaldıraç = " + str(lev_4h) + " Yüzde = " + str(yuz_4h) + " Başarılı İşlem = " + str(bli_4h) + " Başarısız İşlem = " + str(bsiz_4h) +  " İşlem Sonu Bakiye = " + str(bky_4h) + "\n")
f.write("1d Kaldıraç = " + str(lev_1d) + " Yüzde = " + str(yuz_1d) + " Başarılı İşlem = " + str(bli_1d) + " Başarısız İşlem = " + str(bsiz_1d) +  " İşlem Sonu Bakiye = " + str(bky_1d) + "\n")
f.write("1w Kaldıraç = " + str(lev_1w) + " Yüzde = " + str(yuz_1w) + " Başarılı İşlem = " + str(bli_1w) + " Başarısız İşlem = " + str(bsiz_1w) +  " İşlem Sonu Bakiye = " + str(bky_1w) + "\n")
f.close()

print("1m Kaldıraç = " + str(lev_1m) + " Yüzde = " + str(yuz_1m) + " Başarılı İşlem = " + str(bli_1m) + " Başarısız İşlem = " + str(bsiz_1m) +  " İşlem Sonu Bakiye = " + str(bky_1m) + "\n")
print("3m Kaldıraç = " + str(lev_3m) + " Yüzde = " + str(yuz_3m) + " Başarılı İşlem = " + str(bli_3m) + " Başarısız İşlem = " + str(bsiz_3m) +  " İşlem Sonu Bakiye = " + str(bky_3m) + "\n")
print("5m Kaldıraç = " + str(lev_5m) + " Yüzde = " + str(yuz_5m) + " Başarılı İşlem = " + str(bli_5m) + " Başarısız İşlem = " + str(bsiz_5m) +  " İşlem Sonu Bakiye = " + str(bky_5m) + "\n")
print("15m Kaldıraç = " + str(lev_15m) + " Yüzde = " + str(yuz_15m) + " Başarılı İşlem = " + str(bli_15m) + " Başarısız İşlem = " + str(bsiz_15m) +  " İşlem Sonu Bakiye = " + str(bky_15m) + "\n")
print("30m Kaldıraç = " + str(lev_30m) + " Yüzde = " + str(yuz_30m) + " Başarılı İşlem = " + str(bli_30m) + " Başarısız İşlem = " + str(bsiz_30m) +  " İşlem Sonu Bakiye = " + str(bky_30m) + "\n")
print("1h Kaldıraç = " + str(lev_1h) + " Yüzde = " + str(yuz_1h) + " Başarılı İşlem = " + str(bli_1h) + " Başarısız İşlem = " + str(bsiz_1h) +  " İşlem Sonu Bakiye = " + str(bky_1h) + "\n")
print("2h Kaldıraç = " + str(lev_2h) + " Yüzde = " + str(yuz_2h) + " Başarılı İşlem = " + str(bli_2h) + " Başarısız İşlem = " + str(bsiz_2h) +  " İşlem Sonu Bakiye = " + str(bky_2h) + "\n")
print("4h Kaldıraç = " + str(lev_4h) + " Yüzde = " + str(yuz_4h) + " Başarılı İşlem = " + str(bli_4h) + " Başarısız İşlem = " + str(bsiz_4h) +  " İşlem Sonu Bakiye = " + str(bky_4h) + "\n")
print("1d Kaldıraç = " + str(lev_1d) + " Yüzde = " + str(yuz_1d) + " Başarılı İşlem = " + str(bli_1d) + " Başarısız İşlem = " + str(bsiz_1d) +  " İşlem Sonu Bakiye = " + str(bky_1d) + "\n")
print("1w Kaldıraç = " + str(lev_1w) + " Yüzde = " + str(yuz_1w) + " Başarılı İşlem = " + str(bli_1w) + " Başarısız İşlem = " + str(bsiz_1w) +  " İşlem Sonu Bakiye = " + str(bky_1w) + "\n")
print("BTC")