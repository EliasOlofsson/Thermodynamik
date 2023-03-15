import numpy as np
import pyfluids as pf
import matplotlib.pyplot as plt
#from numba import njit
#@njit

### Uppgyggnad och programstruktur
# Programmet består av de simulerade systemen och intervalltester + plottning, svaren finns både i plotten och i print-form
# En del testande har gjorts för att hitta optimala intervall och en kontrollräkning

### Här skapas systemet som ska simulera de givna rankinecykeln 

def System_med_matarvattenförvärmning(Pa):
    
    #Givna värdern
    max_temp = 600
    max_tryck = 15e6
    temp_cond = 30
    # Vi skapar först vår vätska som i detta fall är vatten
    WATER = pf.Fluid(pf.FluidsList.Water)

    #Vi tittar på första punkten samt illustration och TS-diagram
    #Vattnet har här temperaturen av kondensorn med en ångkvalite av 0
    #Vätskan uppdateras med dessa vilkor
    WATER.update(pf.Input.temperature(temp_cond), pf.Input.quality(0))  

    #Hämtar värden från punkt 1 
    h1 = WATER.enthalpy
    s1 = WATER.entropy 

    #Isentrop kompression i pump 1
    s2 = s1 

    #Vätskan uppdateras med med entropi och valt avtappningstryck 
    WATER.update(pf.Input.entropy(s2), pf.Input.pressure(Pa))
    #Hämtar entalpivärde och sparar det
    h2 = WATER.enthalpy 

    #Isobar värmetillförsel från avtappad ånga
    #Uppdatera med värme och tryck
    WATER.update(pf.Input.quality(0), pf.Input.pressure(Pa)) 
    #Spara värden   
    h3 = WATER.enthalpy 
    s3 = WATER.entropy 

    #Isentrop kompression i pump 2
    s4 = s3 

    #Isobar värmetillförsel i ångpannan, trycket blir det samma som maximala trycket
    #Uppdatera med värme och tryck
    WATER.update(pf.Input.pressure(max_tryck), pf.Input.entropy(s4))
    #Spara värde
    h4 = WATER.enthalpy

    #Isobar värmetillförsel i ångpannan, temperatur ökar till max
    #Uppdatera med värme och tryck
    WATER.update(pf.Input.pressure(max_tryck), pf.Input.temperature(max_temp))
    #Spara värden
    h5 = WATER.enthalpy 
    s5 = WATER.entropy 
    
    #Isentrop expansion i turbin
    s6 = s5

    #Punkt 6 har avtappningstrycket från turbinen
    WATER.update(pf.Input.entropy(s6), pf.Input.pressure(Pa))
    #Spara värde
    h6 = WATER.enthalpy

    #Isentrop expansion i turbin
    s7 = s6

    #Isobar värmebortförsel i kondensator
    WATER.update(pf.Input.entropy(s7), pf.Input.temperature(temp_cond)) 
    #Spara värde
    h7 = WATER.enthalpy 

    #andel avtappad ånga formel finns i F7 man behöver endast skriva om den lite
    y = (h3 - h2)/(h6 - h2) 
    
    #Arbete för turbinen formel finns F7
    watt_turb = h5-h6+(1-y)*(h6-h7) 

    #Standard formael för pumpens arbete
    watt_pump1 = h2-h1 
    watt_pump2 = h4-h3 

    #formel för qin finns i F7
    qin = h5-h4

    #Netto arbete för systemet
    watt_net = watt_turb - watt_pump1 - watt_pump2 

    #Systemets verkningsgrad 
    #Formeln finns i rapporten
    n_th = watt_net/qin
    
    #Retunerar verknigsgrad och faktor y, där vi lätt sedan kan inxexa det värdet vi behöver
    return [n_th,y]



#### Här börjar själva uppgift 1 där ett intervall testas för systemet

# Intervall-längd för ökade datapunkter
langd = int(1e3) #snabb
#langd = int(1e4) # något snyggare graf tar ca 30sek
#angd = int(1e5) #mycket långsam, kan köras med Numba @JIT kräver cpp compilator

intervall = np.linspace(1e4, 4e6, langd) #lämpligt intervall för avtappningstryck som ska testas

verk = [System_med_matarvattenförvärmning(i)[0] for i in intervall] # här skapar vi en lista med listbyggaren där systemet testas med olika avtappningstryck, denna lista innehåller verkningsgraderna
y = [System_med_matarvattenförvärmning(i)[1] for i in intervall] # på samma sätt skapar vi en lista som intehåller fraktionen y av avtappad ånga


### Här skapas plottarna för uppgift 1 där all relevant data laddas in
plt.figure(figsize=(16, 12))
plt.subplots_adjust(hspace=0.5, wspace=0.3)
plt.subplot(221)
plt.plot(intervall, verk, ".", color="#2CBDFE", ms=1)
plt.title("Verkningsgrad över med matarvattenförvärmning")
plt.xlabel("Avtappningstryck (Pa)")
plt.ylabel("Verkningsgrad")
plt.subplot(222)
plt.plot(intervall, y, ".", color="#47DBCD", ms=1)
plt.title("Avtappad ångfaktor för matarvattenförvärmning")
plt.xlabel("Avtappningstryck (Pa)")
plt.ylabel("Faktor för avtappad ånga")

### Printar för jämförelse syfte till uppgift 2
print('')
print(f'Maximal verkningsgrad {round(max(verk), 5)} med matarvattenförvärmning')

### Detta är inte strikt rätt då det handlar om olika tryck, eftersom att detta system ej är konstruerat för att ha något avtappningstryck
### Men det är ändå intressant att att se plotten fast själva uppgiften egentligen bara går ut på att jämföra maximala verkningsgraden, villket i detta fall självklart är vid 15MPa
### Så ta denna del med en liten nypa sallt då det endast är i syfte att försöka visualisera på något sätt, själva uppgiftens svar ges i print-satserna

# Skapar systemet utan matarvattenförvärmning för jämförelse

def System_utan_matarvattenförvärmning(Pa): 

    # Vätskan skapas som sist
    WATER = pf.Fluid(pf.FluidsList.Water)
    
    #Initiella villkor antas vara desamma
    max_temp = 600
    temp_cond = 30
   
    # Vi uppdaterar vätskan med på samma sätt
    WATER.update(pf.Input.temperature(temp_cond), pf.Input.quality(0))

    #Hämtar värden från punkt 1 
    h1 = WATER.enthalpy
    s1 = WATER.entropy
    
    #Isentrop kompression i pump 1
    s2=s1
    #Vätskan uppdateras med med entropi och valt tryck, egentilgen ej nödvändigt kan vara statiskt 15MPa
    WATER.update(pf.Input.entropy(s2), pf.Input.pressure(Pa))
     #Hämtar entalpivärde och sparar det
    h2 = WATER.enthalpy
    
    #Isobar värmetillförsel i ångpannan
    #Uppdatera med värme och tryck
    WATER.update(pf.Input.temperature(max_temp), pf.Input.pressure(Pa))
    #Spara värden
    h3 = WATER.enthalpy
    s3 = WATER.entropy
    
    #Isentrop expansion i turbin
    s4=s3
    
    #Isobar värmebortförsel i kondensator
    WATER.update(pf.Input.temperature(temp_cond), pf.Input.entropy(s4))
    #Spara värde  för ekvationer
    h4 = WATER.enthalpy
    
    #Ekvationer från F7
    #watt i turbin = h3-h4
    watt_turbin = h3-h4
    #watt i pump = h2-h1
    watt_pump = h2-h1
    #qin = h3-h2
    qin = h3-h2
    
    #Retunerar verkningsgrad enligt formel
    n_th = (watt_turbin-watt_pump)/qin
    return n_th



intervall_utan = np.linspace(1e4, 15e6, langd) 
verk_utan = [System_utan_matarvattenförvärmning(i) for i in intervall_utan]

# Fyller på plotten med fler plottar
plt.subplot(223)
plt.plot(intervall_utan, verk_utan, ".", color="#9D2EC5", ms=1)
plt.title("Verkningsgrad utan matarvattenförvärmning")
plt.xlabel("Systemtryck (Pa)")
plt.ylabel("Verkningsgrad")
plt.subplot(224)
plt.plot(intervall_utan, verk, ".", color="#2CBDFE", ms=2)
plt.plot(intervall_utan, verk_utan, ".", color="#9D2EC5", ms=2)
plt.title("En typ av jämförelse för några gemensamma tryckvärden")
plt.xlabel('"Systemtryckryck (Pa)" * Läs kommentar i kod')
plt.ylabel("Verkningsgrad")
plt.suptitle("Maximal verkningsgrad 0.48445 med matarvattenförvärmning , Maximal verkningsgrad 0.45023 utan matarvattenförvärmning", fontsize=16)
plt.show()

### Själva uppgift 2 utöver konstruktionen av systemet
print(f'Maximal verkningsgrad {round(max(verk_utan), 5)} utan matarvattenförvärmning')
print('')