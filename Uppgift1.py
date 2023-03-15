import numpy as np
import math as m
import datetime
import matplotlib.pyplot as plt

data = np.loadtxt("Uppsala_temperaturer_2008_2017.txt", skiprows=1) #importera textfil
dates = [datetime.datetime(int(y), int(m), int(d)) for y, m, d in data[:, :3]]
temp_corrected = data[:, 4]
Tin = 21
Tout = temp_corrected
VLh = 2e6
Tl = 10 + 273.15 #kelvin

#definiera alla konstanter
#här stoppar jag in beräkningarna högst upp för att det ska se snyggt ut, inte ett måste
def calculate_vld():
    dT = Tin - Tout # skillnad mellan inomhus- och utomhustemperatur
    return VLh * 1e-3 * dT * 24 / 3600 # räknar ut värmeläckage i kWh/dag
#är glad att jag hittade np.where då det gjorde saker enklare då den filtrerar värden i en array

def calculate_cop():
    Th = np.where(Tout < 0, Tin * (1 + 0.043 * Tin - 0.035 * Tout), np.where((Tout >= 0) & (Tout < Tin), Tin * (1 + 0.043 * (Tin - Tout)), 0)) + 273.15 # räknar ut temperaturen vid förångaren i Kelvin med hjälp av en konditionsats
    COP = 1 / (1 - Tl / Th) # räknar ut COP med hjälp av temperaturen vid förångaren
    COP[Tin <= Tout] = 0 # om inomhustemperaturen är mindre än eller lika med utomhustemperaturen sätts värdet till 0
    return COP

def calculate_watt(cop, vld):
    with np.errstate(divide='ignore', invalid='ignore'):
        watt = np.where(cop == 0, 0, vld / cop)
    return watt


def calculate_vinst(cop, vld): 
    with np.errstate(divide='ignore', invalid='ignore'): # med with blocket ignoreras division med 0
        vinst = np.where(cop == 0, 0, vld / cop / 10) # räknar ut värmepumpens elförbrukning i kWh/dag
    return vinst
 
#använder funktionerna för att skapa viktiga variabler
VLd = calculate_vld()
COP = calculate_cop()
watt = calculate_watt(COP, VLd)
# Beräkna önskad inomhustemperatur Tin2
# Om temperaturen utanför är mindre än 0 grader, sätt Tin2 till 19 grader, annars 21 grader
Tin2 = np.where(Tout < 0, 19, 21)
# Beräkna värmeläckaget från huset
VLd2 = calculate_vld()
# Beräkna temperaturen vid förångaren (Th2) för varje tidpunkt under perioden
# Om temperaturen utanför är mindre än 0 grader, använd första formeln
# Annars, använd andra formeln
# Notera att temperaturen vid tidigare ekvation ges i Kelvin
Th2 = np.where(Tout < 0, Tin2 * (1 + 0.043 * Tin2 - 0.035 * Tout), np.where((Tout >= 0) & (Tout < Tin2), Tin2 * (1 + 0.043 * (Tin2 - Tout)), 0)) + 273.15
# Beräkna COP (Coefficient of Performance) för värmepumpen för varje tidpunkt underperioden
# Notera att denna formel är ekvivalent med den som användes i uppgift 3, eftersom Tl är samma för båda uppgifterna
COP2 = 1 / (1 - Tl / Th2)
# Om Tin2 är mindre än eller lika med Tout, sätt COP2 till 0
COP2[Tin2 <= Tout] = 0
# Beräkna värmepumpens elförbrukning för varje tidpunkt under perioden
vinst2 = calculate_vinst(COP2, VLd2) ##felet jag gjorde var att ta differansen, sparade summan är redan beräknad i watt
#Wsparad = sum(vinst - vinst2) detta är fel tänkte att differansen behövde räknas, men jag redan gör det i min funktion
vinst_ar = sum(vinst2)/10 #total vinst per år 
vinst_tot = sum(vinst2)/1000 #total vinst omvandlat till MWh


#samlar alla print statements här istället
print(f"Värmepumpens årliga energiförbrukning: {round(sum(watt)/10000, 2)} MWh/år.")
print(f"Värmepumpens tottala energiförbrukning: {round(sum(watt)/1000, 2)} MWh.")
print(' ')
print(f'Energi sparad per år med innertemp 19: {vinst_ar} kWh/år.')
print(f'Total energi sparad: {vinst_tot} MWh.')



#flyttade plottar längst ner då det är standard och la till variabler i printsen istället för text
#dags att plotta, la lite extra tid för att få det snyggt, mest för att jag hade gammal kod som liknade
plt.figure(figsize=(16, 12))
plt.subplots_adjust(hspace=0.5, wspace=0.3)
plt.subplot(221)
plt.plot(dates, VLd, ".", color="#2CBDFE", ms=1)
plt.title("Husets värmeläckage")
plt.xlabel("Datum")
plt.ylabel("kWh/dag")
plt.subplot(222)
plt.plot(dates, COP, ".", color="#47DBCD", ms=1)
plt.title("Värmepumpens dagliga COP under tidsperioden")
plt.xlabel("Datum")
plt.ylabel("Värmefaktor COP")
plt.subplot(223)
plt.plot(dates, watt, ".", color="#9D2EC5", ms=1)
plt.title("Värmepumpens elförbrukning")
plt.xlabel("Datum")
plt.ylabel("kWh/dag")
plt.subplot(224)
plt.text(0.5, 0.9, f"Värmepumpens årliga energiförbrukning: {round(sum(watt)/10000, 2)} MWh/år.", ha="center")
plt.text(0.5, 0.7, f"Värmepumpens tottala energiförbrukning: {round(sum(watt)/1000, 2)} MWh.", ha="center")
plt.text(0.5, 0.5, f"Energi sparad per år med innertemp 19: {round(vinst_ar, 2)} kWh/år.", ha="center")
plt.text(0.5, 0.3, f"Total energi sparad: {round(vinst_tot, 2)} MWh.", ha="center")
plt.axis('off')
plt.show()