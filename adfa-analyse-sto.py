import numpy as np
import python_gsl_fit as gsl_fit
#from matplotlib import pyplot as plt

#Program realizujacy analize ADFA na podstawie pracy 
#wszelkie problemy z operacjami na floatach po tronie numpy traktujemy jako wyjatki !!!!
np.seterr(all='raise')
    
def calculate_adfa2(data, boxes=None, offset=None):
    data_size = len(data) #yutaj chyba trzeba wziasc shape
    #zmienne potrzebne do fitowania gsl
    res_pure = np.zeros(6,dtype=np.double)
    res = np.zeros(6, dtype=np.double)
    
    if boxes is None:
        nmin = 3
        nmax = data_size/4
        boxes = [nmin]
        nact = nmin
        while nact <= nmax:
            nact = nact * 2**(1./8.)
            if int(nact) > boxes[-1]:
                boxes.append(int(nact+0.5))
        #ostatni element moze byc wiekszy ze wzgledu na petle while
        if boxes[-1] > nmax:
            boxes = boxes[:-1]
    #polynomial 1
    boxes1 = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 21, 23, 25,
             27, 30, 33, 35, 39, 42, 46, 50, 54, 59 , 65, 70, 77, 83, 91, 99, 108, 118,
             129,140, 153, 166, 182, 198, 216, 235, 257, 280, 305, 332, 363, 395, 431,
             470, 513, 559, 609, 664, 725, 790, 862, 940, 1025, 1117, 1218, 1328, 1449,
             1580, 1723, 1879, 2049, 2234, 2436, 2656, 2897, 3159, 3445, 3757, 4097, 
             4467, 4871, 5312, 5793, 6317, 6889, 7513, 8193, 8934, 9742, 10624, 11586,
             12634, 13778, 15025, 16385, 17867, 19484, 21248, 23171, 25268]
    #boxes = boxes1
    #boxes = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 21, 23, 25,27]
    FP = np.zeros(len(boxes))
    FM = np.zeros(len(boxes))
    MPT = np.zeros(len(boxes))
    MMT = np.zeros(len(boxes))
    order = 1
    for idx,size in enumerate(boxes):
        #zmienna liczaca ile bylo przedzialow
        MP = 0
        MM = 0
        if offset is None:
            slider = size
        else:
            slider = offset
        #od pierwszego elementu tak dlugo jak sie da przy zadanej dlugosci boxu
        for start_id in xrange(0,data_size - size + 1, slider):
            #dla danego przedzialu zbuduj tablice x-ow (wartosci k)
            x =  np.arange(start_id+1, start_id + size+1, dtype=np.float)
            #zbuduj macierz potrzebna do fitowania
            #A = np.vstack([x, np.ones(size)]).T
            #wyiagnij dane do fitu
            y_pure = data[start_id: start_id+size]
            #fit_pure = np.polyfit(x,y_pure,order) #linalg.lstsq(A,y_pure)
            gsl_fit.python_gsl_fit(x,y_pure,res_pure)
            #zbuduj macierz potrzebna do fitowania
            #A = np.vstack([x, np.ones(size)]).T
            #wyiagnij dane do fitu
            tmp_data  = data[start_id: start_id+size]
            y = (tmp_data - tmp_data.mean()).cumsum()
            #fit = np.polyfit(x,y,order,full=True) #np.linalg.lstsq(A,y)
            gsl_fit.python_gsl_fit(x,y,res)
            #print res_pure[1], " - ", y_pure
 
            if res_pure[1] > 0:
                FP[idx] = FP[idx] + res[5]
                MP = MP + 1

            if res_pure[1] < 0:
                FM[idx] = FM[idx] + res[5]
                MM = MM + 1
 
            #drugi element tablicy to residua = czyli ta suma pod pierwiastkiem
        #teraz trzeba podzielic przez N (ilosc punktow) oraz wziasc pierwiastek
        if MP > 0:
            FP[idx] = np.sqrt( FP[idx]/float(size*MP) )
            
        if MM > 0:
            FM[idx] = np.sqrt( FM[idx]/float(size*MM) )
            
        MPT[idx] = MP
        MMT[idx] = MM
 
    return (FP,FM,boxes, MPT, MMT)
    
def save_adfa_result(filename, result, postfix):
    FP,FM,boxes, MP, MM = result
    output = open("%s.%s" % (filename, postfix) , 'w')
    output.write("#lp box_size F+ F- M+ M-\n")
    for i in xrange(len(boxes)):
        output.write("%s %s %s %s %s %s\n" % (i, boxes[i], FP[i], FM[i], MP[i], MM[i]))
    output.close()
   
    
    
def read_rea_data(filename):
    w = open(filename, 'r')
    data = w.readlines()

    rea_data = []
    for i in data[1:]:
        time, rri, flag =  i.split()
        try:
            tmp = [int(time), float(rri), int(flag)]
            rea_data.append(tmp)
        except ValueError:
            pass
    w.close()
    return np.array(rea_data)
    
def filter_data(raw_data):
    data = []           # tablica z danymi numerycznymi
    flag = False
    entopyBeat = []     # tablica z indeksami gdzie wystapily flag != 0 - indeky wzgledme wywalonego poczatku
    new_idx = 0
    #tworz nowa tablice i apaietaj indeksy wzbudzen entopowych
    for i in raw_data[1:]:
        tmp = i.split()
        if flag == False and float(tmp[2]) != 0:
            continue
        flag = True
        data.append([float(tmp[0]), float(tmp[1]), float(tmp[2])])
        if float(tmp[2]) != 0:
            entopyBeat.append(new_idx)
        new_idx = new_idx + 1

    #print "Tablica wzbudzen ", entopyBeat
    #wywal koncowe wzbudzenia entopowe
    for i in xrange(len(data) -1 , 0, -1):
        if data[i][2] == 0:
            break

    data = data[:i+1]

    #zlicz jak dlugie a przedzialy nastepujacych po sobi wzbudzen entopowych
    k = []
    points = 1
    pr = 0
    if len(entopyBeat) == 0:
        return data

    start = entopyBeat[pr]
    for ne in xrange(1, len(entopyBeat)):
        if entopyBeat[ne] - entopyBeat[pr] != 1:
            k.append( (start, points))
            start = entopyBeat[ne]
            pr = ne
            points = 0
        
        pr = ne
        points = points + 1

    #fituj w przedzialach 
    for idx, points in k:
        x1 = float(data[idx-1][1])
        x2 = float(data[idx + points][1])
        for i in xrange(0,points):
            new_data = data[idx-1][1] + (i + 1.) * ( (x2 - x1) / (points+1.) )
            data[idx + i][1] = new_data

    return data
        
    
if __name__ == "__main__":
    import sys, os
    
    #if len(sys.argv) < 4:
        # "USAGE: python dfa_peng.py filename adfa2 fit|nofit "
        #sys.exit(1)
        
    filename = sys.argv[1]
    
    dirname = filename.split('.')[0] + "_data"
    path = os.path.join('.',dirname)
    
    out_filename = os.path.join(path, filename)
    
    if not os.path.exists(path):
        os.makedirs(dirname)
        
    raw_data = open(sys.argv[1], 'r').readlines()
    #data = read_rea_data(filename)
    data = np.array(filter_data(raw_data))
    
    #bedziemy sie slizgac w okna po size elementow
    tmp = []
    #wielkosc okna
    size = 300
    res = np.zeros(6, dtype=np.float)
    
    i = 0
    #przygotuj plik do danych
    out_slide_data = open(out_filename+".adfa2", 'w')
    out_slide_data.write("#lp box_size F+ F- M+ M-\n")
    
    for start_idx in range(0, len(data) - size+1, 1):
        if i%10000==0:
            print i, "z", len(data) - size
        rri = data[start_idx:start_idx+size,1]
        result = calculate_adfa2(rri)
        
        FP,FM,boxes, MP, MM = result
        postfix = "w_%06d" % i
        #zapisz dane do pliku
        out_slide_data.write("\n# %s\n" % postfix)
        for j in xrange(len(boxes)):
            out_slide_data.write("%s %s %s %s %s %s\n" % (j, boxes[j], FP[j], FM[j], MP[j], MM[j]))

        
        boxes_log = np.log(boxes)
        error_plus = 0
        error_minus = 0
        flag_error_plus  = 0 #czy byly jakies modyfikacje/bled - np. przeliczanie obszarow, albo zerowy blad
        flag_error_minus = 0 #j.w.
       
        if np.all(MP) != 0:
            if not np.all(FP) != 0.:
                #mamu zero bledu w ficie(pewie jeden obszar dodatni z idealnym fitem) - wywalamy to okno
                error_plus = 0
                flag_error_plus = 1
                boxes_log = np.log(boxes)
            else:
                FP_log = np.log(FP)
                error_plus = len(boxes)
            	boxes_log = np.log(boxes)
        else:
            new_FP = []
            new_box = []
            flag_error_plus = 2
            error_plus = 0
            for idx, val in enumerate(MP):
                if val != 0:
                    error_plus = error_plus + 1
                    new_box.append(boxes[idx])
                    #jesli byl fit z zerowym bledem - wywalamy bo log(0) nie moze byc !
                    if FP[idx] == 0:
                        error_plus = 0
                        flag_error_plus = 1
                        break
                    else:
                        new_FP.append(FP[idx])

            if flag_error_plus != 1:
                FP_log = np.log(new_FP)
                boxes_log = np.log(new_box)
        
        if error_plus > 1 and len(MP) > 1:
            gsl_fit.python_gsl_fit(boxes_log,FP_log,res)
            alpha_plus = res[1]
        else:
            alpha_plus = 'nan'

        if np.all(MM)!= 0:
            if not np.all(FM) != 0:
                error_minus = 0
                flag_error_minus = 1
        	boxes_log = np.log(boxes)
            else:
                FM_log = np.log(FM)
                error_minus = len(boxes)
                boxes_log = np.log(boxes)
        else:
            flag_error_minus = 2
            error_minus = 0
            new_FM = []
            new_box = []
            for idx, val in enumerate(MM):
                if val != 0:
                    error_minus = error_minus + 1
                    new_box.append(boxes[idx])
                    if FM[idx] == 0:
                        error_minus = 0
                        flag_error_minus = 1
                        break
                    else:
                        new_FM.append(FM[idx])

            if flag_error_minus != 1:
                FM_log = np.log(new_FM)
                boxes_log = np.log(new_box)

        if error_minus > 1 and len(MM) > 1:
            gsl_fit.python_gsl_fit(boxes_log,FM_log,res)
            alpha_minus = res[1]
        else:
            alpha_minus = "nan"
    
        tmp.append([alpha_plus, alpha_minus, error_plus, error_minus, flag_error_plus, flag_error_minus])
      
        i = i + 1
        
    #zapisz do pliku 
    
    out_name = os.path.join(dirname, 'alpha_%s.dat' % filename)
    out_file = open(out_name, 'w')
    for idx, val in enumerate(tmp):
        out_file.write("%s %s %s %s %s %s %s\n" % (idx, val[0], val[1], val[2], val[3], val[4], val[5]))
    out_file.close()    
    out_slide_data.close()
    
        
    
    #rri = data[:,1]
   
    #if sys.argv[3] == 'nofit':
        #rea_data = read_rea_data(filename)
        #rri = rea_data[:,1]
    #else:
        #raw_data = open(sys.argv[1], 'r').readlines()
        #data = np.array(filter_data(raw_data))
        #rri = data[:,1]
   
    #if sys.argv[2] == 'adfa2':
        #if len(sys.argv) == 5:
            #offset = int(sys.argv[4])
        #else:
            #offset = None
        #result = calculate_adfa2(rri, offset=offset)
        #save_adfa_result(filename, result, sys.argv[2])
    
    

#print "-----"
#Alpha = np.linalg.lstsq(np.vstack([np.log(boxes), np.ones(len(boxes))]).T,np.log(F))[0][0]
#print Alpha    
    
        
        
