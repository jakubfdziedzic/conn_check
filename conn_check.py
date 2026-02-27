# how to use (all parameters are mandatory- must be given in CMD command line)  
# conn_check.py [debug] [Time] [Timeout]
# [debug]   = sys.argv[1] debug or nodebug 
# [Time]    = sys.argv[2] time in sec (integer value) 
# [Timeout] = sys.argv[3] max time of waiting for answer from remote server 
# example: python3 conn_check.py nodebug 5 5

import socket
import time
import sys
import os
import requests
import socket
import re
import subprocess
import tempfile
import shutil

from sh import uptime, df
import runpy

from datetime import datetime

#import httplib  # python < 3.0
import http.client 

    ###################################################################
    #############  funkcja zapisu do loga błędów skryptu ##############
    ###################################################################
    
def error_log(error_massage):                                                   #definicja funkcji
    try:                                                                        #rozpoczęcie bloku bezpiecznego. Jeśli gdzieś niżej wystąpi błąd to python przeskoczy do bloku except
        print (error_massage)
        MainLogFile=open("/var/www/html/Scripts/Main_Script_Log.log",mode='a')  #otwarcie pliku. tryb a oznacza że nowe dane trafią na koniec pliku a stare nie zostaną skasowane, 'r' to read, 'w' to write
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")                          #formatowanie daty (funkcja strftime zwraca string) Usunąłem przypisanie daty do zmiennej Main_date_time żeby była ona aktualna w momencie zapisu do loga a nie w momencie odczytu pliku conn.log           
        MainLogFile.writelines(date_time+" "+error_massage)                     #zapis do bufora. Przygotowuje linię tekstu składającą się z daty i treści błędu do zapisania w pliku
        MainLogFile.write("\n")                                                 #wstawianie znaku nowej linii
          
        MainLogFile.close()                                                     #zamknięcie pliku
    except:                                                                     #obsługa wyjątku. Jeśli coś się nie uda w bloku try to blok except zostanie wykonany
        print("Error 00 when writing Main_Error_Log.log")
    
    ###################################################################
    ########## funkcja sprawdzania połączenia z internetem ############
    ###################################################################
    
def internet() -> bool:                                                         #fragment -> bool powoduje że funkcja zwraca wartość true albo false
    try:
        conn = http.client.HTTPSConnection("8.8.8.8", timeout=int(sys.argv[3])) #tworzy obiekt połączenia szyfrowanego, 8.8.8.8 to dns google czyli stabilny punkt odniesienia, ustawia maksymalny czas oczekiwania na połączenie (sys.argv[3] oznacza że skrypt pobiera wartość z 3 argumentu podanego przy uruchamiuaniu)
        conn.request("HEAD", "/")                                               #wysyła zapytanie typu head do głównej ścieżki. Czyli pobiera nagłówki bez treści żeby było szybciej
        return True                                                             
    except Exception:                                                           #przechwycenie każdego możliwego błędu
        return False
    finally:                                                                    #ten blok się wykonuje zawsze niezależnie od od tego czy był błąd czy nie
        conn.close()                                                            #zamknięcie połączenia

def internet1() -> bool:
    try:
        conn = http.client.HTTPSConnection("1.1.1.1", timeout=int(sys.argv[3])) #robi to samo co ta wyżej tylko łączy się z cloudfare a nie z google
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()
        
    ###################################################################    
    ######### Wyświetla interwał sprawdzania połaczenia  ##############
    ###################################################################
    
print ("Checking interval [sec]: " + sys.argv[2])
    ###################################################################    
    ############ Wyświetla ostatni restet histconn.log   ##############
    ########## wartoć odczytywana jest z pliku hitconn.log  ###########
    ###################################################################
    
HistLogFile=open("/var/www/html/Scripts/histconn.log",mode='r')                 #otwarcie pliku pod ścieżką w trybie do odczytu
print (HistLogFile.readline())                                                  #odczyt tylko pierwszej linii z pliku
HistLogFile.close()                                                             #zamyka plik

    ###################################################################    
    ################## pętla główna programu ##########################
    ###################################################################
    
while True:
    
    ###################################################################
    ###### Odczyt poprzedniego stanu połączenia z pliku conn.log ######
    ################### do zmiennej CurrentStatus  ####################
    ###################################################################
    
    try:
        LogFile = open("/var/www/html/Scripts/conn.log",mode='r')
        CurrentStatus=LogFile.read()                                            #tutaj czytany jest cały plik
        LogFile.close()
        
    except: 
        error_log("conn_check.py: Error 0A when reading conn.log file")
        
    ###################################################################
    ######### Sprawdzanie obecnej daty i czasu + formatowanie #########
    ###################################################################
    try:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    except:
        error_log("conn_check.py: Error 0A1 when time/date reading/formating")
    ###################################################################
    ####### Sprawdzanie połączenia z internetem i przypisanie #########
    ######## odpowiedniej watości do zmiennej Internet_Status #########
    ###################################################################
    
    if internet() or internet1():
        Internet_Status = 'detected'
        ThinyControlStatusInternet = " "
        try:
            # Sprawdzenie połączenia z Thiny Control
            socket.create_connection(('192.168.30.106',80), timeout=1)  
            response = requests.get('http://192.168.30.106/outs.cgi?out0=0')
            ThinyControlStatusInternet_Temp = re.search(r'<out>(.*?)</out>', response.text)

            if ThinyControlStatusInternet_Temp:
                ThinyControlStatusInternet = str(ThinyControlStatusInternet_Temp.group(1))[0:1]

                if ThinyControlStatusInternet == "0":
                    ThinyControlStatusInternet = "- Relay0 (Red LED ligt)   is OFF"

                print(ThinyControlStatusInternet)

        except socket.error:
            # Jeśli połączenie jest nieaktywne, wyświetlenie komunikatu o błędzie
            ThinyControlStatusInternet="No conncetion to LAN cont."
            print(ThinyControlStatusInternet)
            error_log("conn_check.py: Error 0AA when reading ix.xml file from LAN controller (parameter <out></out>")    
    else: 
        Internet_Status = 'NOT detected'
        ThinyControlStatusInternet = " "
        try:
            # Sprawdzenie połączenia z Thiny Control
            socket.create_connection(('192.168.30.106',80), timeout=1)                              #80 to jest port http (standard przemysłowy)
            response = requests.get('http://192.168.30.106/outs.cgi?out0=1')
            ThinyControlStatusInternet_Temp = re.search(r'<out>(.*?)</out>', response.text)

            if ThinyControlStatusInternet_Temp:
                ThinyControlStatusInternet = str(ThinyControlStatusInternet_Temp.group(1))[0:1]

                if ThinyControlStatusInternet == "1":
                   ThinyControlStatusInternet = "- Relay0 (Red LED light)   is ON"

                print(ThinyControlStatusInternet)  

        except socket.error:
            # Jeśli połączenie jest nieaktywne, wyświetlenie komunikatu o błędzie
            ThinyControlStatusInternet = "Relay0 (Red LED) is ??? (LAN cont. is not responding)"
            print(ThinyControlStatusInternet)    
            error_log("conn_check.py: Error 0AB when reading ix.xml file from LAN controller (parameter <out></out>")    
  
        ############################################################### 
        ### Sprawdzenie temparatury procesora LAN Controlera  ##########
        ###############################################################       
    try:
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        ThinyControlCPUTemp_Temp=re.search(r'<tem>(.*?)</tem>', response.text).group(1)
        if ThinyControlCPUTemp_Temp.isdigit():
            ThinyControlCPUTemp_Temp = str(int(ThinyControlCPUTemp_Temp) / 100) 
        else:
            ThinyControlCPUTemp_Temp = "????"
        ThinyControlCPUTemp=str(ThinyControlCPUTemp_Temp+"°C")
    except socket.error:
        # Jeśli połączenie jest nieaktywne, wyświetlenie komunikatu o błędzie
        ThinyControlCPUTemp="????"
        print(ThinyControlCPUTemp) 
        error_log("conn_check.py: Error 0AC when reading ix.xml file from LAN controller (parameter <tem></tem>")    
        ############################################################### 
        ##### Sprawdzenie napięcia zasilania LAN Controlera  ##########
        ###############################################################        
        
    try:
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        ThinyControlVCC_Temp=re.search(r'<vin>(.*?)</vin>', response.text).group(1)
        if ThinyControlVCC_Temp.isdigit():
            ThinyControlVCC_Temp = str(int(ThinyControlVCC_Temp) / 100) 
        else:
            ThinyControlVCC_Temp = "????"
        ThinyControlVCC=str(ThinyControlVCC_Temp+"V")
    except socket.error:
        ThinyControlVCC="????"
        error_log("conn_check.py: Error 0AD when reading ix.xml file from LAN controller (parameter <vin></vin>")    
        
        ############################################################### 
        ##### Sprawdzenie temperatury w rodzielnicy (DS8)    ##########
        ############################################################### 
          
    try:
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        InCabintetTemp1_Temp=re.search(r'<ds8>(.*?)</ds8>', response.text).group(1)
        if InCabintetTemp1_Temp.isdigit():
            InCabintetTemp1_Temp = str(int(InCabintetTemp1_Temp) / 10) 
        else:
            InCabintetTemp1_Temp = "????"
        InCabintetTemp1=str(InCabintetTemp1_Temp+"°C")
    except socket.error:
        InCabintetTemp1="????"
        error_log("conn_check.py: Error 0AE when reading ix.xml file from LAN controller (parameter <ds8></ds8>")    
        
        ############################################################### 
        ##### Sprawdzenie temperatury i wilgotności w pokoju ##########
        ############################################################### 
        
    try:
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        RoomTemp1_Temp=re.search(r'<dth0>(.*?)</dth0>', response.text).group(1)
        RoomHumid_Temp=re.search(r'<dth1>(.*?)</dth1>', response.text).group(1)
        if RoomTemp1_Temp.isdigit():
            RoomTemp1_Temp = str(int(RoomTemp1_Temp) / 10) 
        else:
            RoomTemp1_Temp = "????"
        RoomTemp1=str(RoomTemp1_Temp+"°C")
        
        if RoomHumid_Temp.isdigit():
            RoomHumid_Temp = str(int(RoomHumid_Temp) / 10) 
        else:
            RoomHumid_Temp = "????"
        RoomHumid=str(RoomHumid_Temp+"%")
    except socket.error:
        RoomTemp1="????"
        RoomHumid="????"
        error_log("conn_check.py: Error 0AF when reading ix.xml file from LAN controller (parameter <dth0></dth0> i <dth1></dth1>")    
    
        ############################################################### 
        ##### zappis temperatury i wilgotności w pokoju do plików #####
        ############################################################### 
            
    try:
            with tempfile.NamedTemporaryFile(prefix="Hum_",mode="w", delete=False) as temp_file:
                temp_file_path = temp_file.name
                HumFile = temp_file 
                HumFile.writelines("Room humid.="+ RoomHumid)
                HumFile.close()
                os.rename(temp_file_path, "/var/www/html/Scripts/RoomHumid.data")
                os.chmod("/var/www/html/Scripts/RoomHumid.data", 0o644)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
    except:
        error_log("conn_check.py: Error 0AG when writing to RoomHumid.data file")
            
    try:
            with tempfile.NamedTemporaryFile(prefix="Temp_",mode="w", delete=False) as temp_file:
                temp_file_path = temp_file.name
                TemFile = temp_file 
                TemFile.writelines("Room temp.="+ RoomTemp1)
                TemFile.close()
                os.rename(temp_file_path, "/var/www/html/Scripts/RoomTemp.data")
                os.chmod("/var/www/html/Scripts/RoomTemp.data", 0o644)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
    except:
        error_log("conn_check.py: Error 0AHG when writing to RoomTemp.data file")
            
            
        ############################################################### 
        ### Formowanie pełnego komunikatu do zapisu w pliku conn.log ##
        ######### data, czas Connection to internet: STATUS  ##########
        ###############################################################
        
    Total_Status = date_time + " Internet: " + Internet_Status

        ############################################################### 
        ############ Odzczyt czasu działania LAN controllera ##########
        ###############################################################
    try: 
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        ThinyControlRunningTime_Day_Temp=re.search(r'<sec3>(.*?)</sec3>', response.text)
        ThinyControlRunningTime_Day=str(ThinyControlRunningTime_Day_Temp.group(1))
        ThinyControlRunningTime_Hour_Temp=re.search(r'<sec2>(.*?)</sec2>', response.text)
        ThinyControlRunningTime_Hour=str(ThinyControlRunningTime_Hour_Temp.group(1))
        ThinyControlRunningTime_Minute_Temp=re.search(r'<sec1>(.*?)</sec1>', response.text)
        ThinyControlRunningTime_Minute=str(ThinyControlRunningTime_Minute_Temp.group(1))
        ThinyControlRunningTime="LAN cont. running time: "+ThinyControlRunningTime_Day+" days, "+ThinyControlRunningTime_Hour+" hours, "+ThinyControlRunningTime_Minute+ " minutes"
    except socket.error:
        error_log("conn_check.py: Error 0B when reading ix.xml file from LAN controller (parameter <secN></secN> N=1..3")
        
        ############################################################### 
        ## Sprawdzanie statusu przekazników ThinyControl od 1 do 4  ###
        ###############################################################            
    try: 
        socket.create_connection(('192.168.30.106',80), timeout=1) 
        response = requests.get('http://192.168.30.106/xml/ix.xml')
        ThinyControlStatusRealy_Temp=re.search(r'<out1>(.*?)</out1>', response.text)
        ThinyControlStatusRelay_1=str(ThinyControlStatusRealy_Temp.group(1))
        if ThinyControlStatusRelay_1=="1":
            ThinyControlStatusRelay_1="- Relay1 (GL.iNet router) is ON"
        else:
            ThinyControlStatusRelay_1="- Relay1 (GL.iNet router) is OFF"
   
        ThinyControlStatusRealy_Temp=re.search(r'<out2>(.*?)</out2>', response.text)
        ThinyControlStatusRelay_2=str(ThinyControlStatusRealy_Temp.group(1))
        if ThinyControlStatusRelay_2=="1":
            ThinyControlStatusRelay_2="- Relay2 (Spare relay)    is ON"
        else:
            ThinyControlStatusRelay_2="- Relay2 (Spare relay)    is OFF"

        ThinyControlStatusRealy_Temp=re.search(r'<out3>(.*?)</out3>', response.text)
        ThinyControlStatusRelay_3=str(ThinyControlStatusRealy_Temp.group(1))        
        if ThinyControlStatusRelay_3=="1":
            ThinyControlStatusRelay_3="- Relay3 (Room lamp)      is ON"
        else:
            ThinyControlStatusRelay_3="- Relay3 (Room Lamp)      is OFF"
        ThinyControlStatusRealy_Temp=re.search(r'<out4>(.*?)</out4>', response.text)
        ThinyControlStatusRelay_4=str(ThinyControlStatusRealy_Temp.group(1))        
    
        if ThinyControlStatusRelay_4=="1":
            ThinyControlStatusRelay_4="- Relay4 (Spare relay)    is ON"
        else:
            ThinyControlStatusRelay_4="- Relay4 (Spare relay)    is OFF"
    except socket.error:    
        ThinyControlStatusRelay_1="- Relay1 (GL.iNet router) is ??? (LAN cont. is not responding)"
        ThinyControlStatusRelay_2="- Relay2 (Spare rellay)   is ??? (LAN cont. is not responding)"
        ThinyControlStatusRelay_3="- Relay3 (Room lamp)      is ??? (LAN cont. is not responding)"
        ThinyControlStatusRelay_4="- Relay4 (Spare relay)    is ??? (LAN cont. is not responding)"
        
        ############################################################### 
        ######  Sprawdzanie czy poprzedni status jest  ################
        ######           różny od obecnego             ################
        ####### jeżeli tak to modyfikuje plik          ################
        ###############################################################
                    
    if CurrentStatus[31:]!= Internet_Status: 
        print ("Internet connection status changed from: "+ CurrentStatus[31:]+" to: "+ Internet_Status)
        
        ###############################################################
        ############## aktualizacja statusu połączenia ################
        ###############################################################
        
        try:
            with tempfile.NamedTemporaryFile(prefix="Connlog_",mode="w", delete=False) as temp_file:
                temp_file_path = temp_file.name
                LogFile = temp_file
                LogFile.writelines(Total_Status)
                LogFile.close()
                os.rename(temp_file_path, "/var/www/html/Scripts/conn.log")
                os.chmod("/var/www/html/Scripts/conn.log", 0o644)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        except:
            error_log("conn_check.py: Error 01 when writing conn.log file")
            
        ###############################################################
        ############## dodanie wpisu do historii połączeń #############
        ###############################################################
        
        try:
            HistLogFile=open("/var/www/html/Scripts/histconn.log",mode='a')
            HistLogFile.writelines(Total_Status)
            HistLogFile.write("\n")
            HistLogFile.close()
        except:
            error_log("conn_check.py: Error 02 when writing histconn.log file (simlified log)")
    else:
        print ("Internet connection status NOT changed. Current status: "+ CurrentStatus[31:])
        
        ###############################################################
        ############# dodawanie do loga połaczeń z internetem  ########
        ################ czasu weryfikacji połączenia    ##############
        ##############  gdy wybrany jest parametr "debug" #############
        ###############################################################
        
    if sys.argv[1]=="debug":
        print("Debug function: Active (more detailed log)")
       # Tworzenie tymczasowego pliku
        try: 
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file_path = temp_file.name
                # Tworzenie zmiennej HistLogFile
                HistLogFile = temp_file
                # Konwersja danych do stringów
                date_time = str(date_time)
                # Zapis danych do pliku
                HistLogFile.write(("verification on: " + date_time).encode())
                HistLogFile.write("\n".encode())
                HistLogFile.flush()
                # Przenoszenie tymczasowego pliku do oryginalnego pliku
                with open('/var/www/html/Scripts/histconn.log', 'ab') as original_file:
                    temp_file.seek(0)
                    shutil.copyfileobj(temp_file, original_file)
                temp_file.close()
        except:
            error_log("conn_check.py: Error 03 when writing histconn.log file (more detaialed log)")
    else:
        print("Debug function: Not active (simplified log)")
    
        ###############################################################
        ################  Odczyt pliku conn.log  ######################
        ###############################################################
        
    try:
        LogFile = open("/var/www/html/Scripts/conn.log",mode='r')
        CurrentStatus=LogFile.read()
        LogFile.close()
    except:
        error_log("conn_check.py: Error 04 when reading conn.log file")
        
        ############################################################### 
        ################  uaktualnienie pliku sys.log  ################
        ############################################################### 
    CPURPIVolt = os.popen("sudo vcgencmd measure_volts").read() 
    CPURPIVolt=CPURPIVolt.strip()
    print (CPURPIVolt) 
    try:
        with tempfile.NamedTemporaryFile(prefix="syslog_", delete=False) as temp_file:
            temp_file_path = temp_file.name
            SysLogFile = temp_file
            uptime_work = str(uptime('-p'))
            SysStatus = "Server running time: "+ uptime_work[3:]
            SysLogFile.write(SysStatus.encode())
            SysVer1 = os.popen("/usr/bin/uname -srm")
            SysV1 = SysVer1.read()[:-1]
            SysLogFile.write(("System ver: "+SysV1).encode())
            SysLogFile.write(b"\n")
            Gate2 = os.popen("sudo route -n | grep 'UG'")
            GateV2 = Gate2.read()[16:32] 
            SysLogFile.write(("Gateway: "+GateV2).encode())
            SysLogFile.write(b"\n")
            SysLogFile.write(CurrentStatus.encode())
            SysLogFile.write(b"\n") 
            Temp=os.popen("/usr/bin/vcgencmd measure_temp")
            Proc_Temp=Temp.read()[:-1]
            SysLogFile.write(("Current RPI CPU "+Proc_Temp).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(("Current PRI CPU "+CPURPIVolt.strip()).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write((ThinyControlRunningTime).encode())
            SysLogFile.write(b"\n")
            SysLogFile.write(("LAN cont. temp="+ThinyControlCPUTemp).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(("LAN cont. input voltage="+ThinyControlVCC).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(b"\n") 
            SysLogFile.write(("LAN controler relays status:").encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(ThinyControlStatusInternet.encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(ThinyControlStatusRelay_1.encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(ThinyControlStatusRelay_2.encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(ThinyControlStatusRelay_3.encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(ThinyControlStatusRelay_4.encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(b"\n") 
            SysLogFile.write(("LAN controler env. sensors:").encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(("- In-cabinet temp (DS18B20)="+InCabintetTemp1).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(("- Room humidity (AM2320)="+RoomHumid).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.write(("- Room temp (AM2320)="+RoomTemp1).encode())
            SysLogFile.write(b"\n") 
            SysLogFile.close()
            os.chmod(temp_file_path,0o777)
            os.rename(temp_file_path, "/var/www/html/Scripts/sys.log")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    except:
        error_log("conn_check.py: Error 05 when writing sys.log file")
        
        ############################################################### 
        ###########  wyświetlanie danych na ekranie ###################
        ############################################################### 
        
    print ("sys.log temp file path"+ temp_file_path)
    print (SysStatus)
    print ("Curent RPI CPU "+Proc_Temp)
    print ("Current PRI CPU "+CPURPIVolt)
    print ("Lan controller Temp="+ThinyControlCPUTemp) 
    print ("Lan Controller input Voltage="+ThinyControlVCC)
    print ("In-cabinet temp="+InCabintetTemp1)
    print (ThinyControlRunningTime)
    print ("Gateway: "+GateV2) 
    print ("System ver: "+SysV1)
    print ("Relays (1-4):")
    print (ThinyControlStatusRelay_1[0:60])
    print (ThinyControlStatusRelay_2[0:60])
    print (ThinyControlStatusRelay_3[0:60])
    print (ThinyControlStatusRelay_4[0:60])
    
        ############################################################### 
        ##############  uaktualnienie pliku space.log  ################
        ############################################################### 
        # Tworzenie tymczasowego pliku
    try:
        with tempfile.NamedTemporaryFile(prefix="spacelog_",delete=False) as temp_file:
            temp_file_path = temp_file.name
            # Tworzenie zmiennej SpaceLogFile
            SpaceLogFile = temp_file
            # Konwersja danych do stringów
            Disc_space = str(df( "-h","/", "/public","/hdd","/ramdisk"))
            SpaceLogFile.write(Disc_space.encode())
            SpaceLogFile.close()
            # Przenoszenie tymczasowego pliku do oryginalnego pliku
            os.rename(temp_file_path, "/var/www/html/Scripts/space.log")
            os.chmod("/var/www/html/Scripts/space.log", 0o644)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    except:
        error_log("conn_check.py: Error 06 when writing space.log file")
        
 
    print ("\n")
    print ("*** End of information ***")
    print ("\n")
            
        # Interwał X sekund pomiedzy sprawdzeniami podany 
        # jako parametr sys.argv[2])  
    time.sleep(int(sys.argv[2]))
    

