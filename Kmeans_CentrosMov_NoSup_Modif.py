from PIL import Image
import pathlib
import tkinter
from tkinter import END, TOP, filedialog
import csv
from tkinter import messagebox
import math
import copy
from itertools import combinations
from xlwt import Workbook
import numpy as np
from matplotlib import pyplot as plt

# Definicion de funciones

def fnPlot(centros, dMax, dMin, own, fitness):
    newArray = dict()
    # Recorremos imagenes
    for i in own.keys():
        newArray[i] =  list()
        # Obtenemos valor real de los centros
        centValues = list()
        dif = dMax[i] - dMin[i]
        for c in centros[i]:
            cVal = (c * dif) + dMin[i]
            centValues.append([cVal, 0])
        # Guardamos array
        for row in range(len(own[i])):
            rowArray = list()
            for col in range(len(own[i][row])):
                rowArray.append(centValues[own[i][row][col][0]][0])
                centValues[own[i][row][col][0]][1] = centValues[own[i][row][col][0]][1] + 1
            newArray[i].append(rowArray)
        # Plot image
        plot = plt
        plot.imshow(newArray[i])
        plot.title('C1: ' +  str(centValues[0]) + ', C2: ' + str(centValues[1]))
        plot.show()
        cl = [[centros[i][0], centros[i][0], centros[i][0]], [centros[i][1], centros[i][1], centros[i][1]]]
        plot.bar([1, 2], [centValues[0][1], centValues[1][1]], width=0.8, color=cl, tick_label = [centValues[0][0], centValues[1][0]])
        plot.show()
    return newArray

def logResults(_r, _f, _sd):
    # Comienza a loggear
    wb = Workbook()
    # Muestra los registros
    for i in _r.keys():
        sheet = wb.add_sheet('Matriz de valores ' + str(i))
        sheet.write(0, 0, 'Fitness: ' + str(_f[i]) + ', Distancias a centrs: ' + str(_sd[i]))
        for r in range(len(_r[i])):
            for c in range(len(_r[i][r])):
                sheet.write(r + 2, c, str(_r[i][r][c]))
    wb.save('K_Means_Modif.xls')
    messagebox.showinfo("Archivo Creado", "Se ha creado un archivo con la informacion generada.")

def fnGiftPixels(_own, _i, _pxFit, fcs, fcl, ftObj):
    # Debe regalar pixeles del centro con mas fitnes al de menos
    Nown = copy.deepcopy(_own)
    ftRegalado = 0
    print('Regalando Pixeles')
    while ftRegalado < ftObj:
        minCord = (-1, -1)
        minFit = -1
        # Recorremos todos los pixeles
        for row in range(len(_pxFit[_i])):
            for col in range(len(_pxFit[_i][row])):
                # Si pertenece al centro grande
                if Nown[_i][row][col][0] == fcl:
                    pxft = _pxFit[_i][row][col]
                    if minFit == -1 or minFit > pxft:
                        minFit = pxft
                        minCord = (row, col)
        # Se cambia el ownr del pixel
        Nown[_i][minCord[0]][minCord[1]] = (fcs, Nown[_i][minCord[0]][minCord[1]][1])
        ftRegalado = ftRegalado + minFit
        print('Fitnes objetivo: ' + str(ftObj) + ', Fitness Regalado: ' + str(ftRegalado))
    return Nown

def fnGetfSLCent(_fC):
    fCs = dict()
    fCl = dict()
    for i in _fC.keys():
        fCs[i] = (-1, -1) # (idCentro, fitness)
        fCl[i] = (-1, -1)
        # Por cada centro
        for c in range(len(_fC[i])):
            if fCs[i][0] == -1 or fCs[i][1] > _fC[i][c]:
                fCs[i] = (c, _fC[i][c])
            if fCl[i][0] == -1 or fCl[i][1] < _fC[i][c]:
                fCl[i] = (c, _fC[i][c])
    return fCs, fCl

def fnCalcFitness(_VNorm, _Pnew, _cent, _own):
    fCent = dict()
    pxFit = dict()
    # Se obtienen distancias
    print('Calculando distancia de px a nuevos centros')
    dNorm, sumDist = fnGetDistCenters(_cent, _VNorm)
    print('Calculando distancia de pnew a nuevos centros')
    dPnew, sumDist = fnGetDistCenters(_cent, _Pnew)
    # Por cada imagen
    for i in _cent.keys():
        fCent[i] = list()
        pxFitCent = list()
        # Por cada centro
        for c in range(len(_cent[i])):
            fCent[i].append(0)
        # Por cada pixel
        for row in range(len(_VNorm[i])):
            pxFitCentRow = list()
            for col in range(len(_VNorm[i][row])):
                cOwns = _own[i][row][col][0]
                dobAbsNorm = math.pow(dNorm[i][cOwns][row][col], 2)
                dobAbsPnew = math.pow(dPnew[i][cOwns][row][col], 2)
                pxFitness = math.sqrt(dobAbsNorm + dobAbsPnew)
                fCent[i][cOwns] = fCent[i][cOwns] + pxFitness
                pxFitCentRow.append(pxFitness)
            pxFitCent.append(pxFitCentRow)
        pxFit[i] = pxFitCent
    return fCent, pxFit

def fnCenterCenters(_StrtCent, _owner, _VarNorm):
    newCenters = dict()
    val = dict()
    # Recorrer imagenes
    for i in _StrtCent.keys():
        n = dict()
        newCenters[i] = list()
        # Recorrer pixeles
        for row in range(len(_owner[i])):
            for col in range(len(_owner[i][row])):
                center =_owner[i][row][col][0]
                if center not in val.keys():
                    v = _VarNorm[i][row][col]
                    val[center] = v
                    n[center] = 1
                else:
                    val[center] = val[center] + _VarNorm[i][row][col]
                    n[center] = n[center] + 1
        for c in range(len(_StrtCent[i])):
            nCent = 0
            if c in val.keys():
                cc = val[c]
                nCent = cc / n[c]
                newCenters[i].append(nCent)
            else:
                newCenters[i].append(_StrtCent[i][c])
    return newCenters

def fnGetOwnership(_distCentro):
    ownr = dict()
    # Recorremos cada imagen
    for i in _distCentro.keys():
        ownr[i] = list()
        ic = 0
        # Evaluamos cada Centro
        for c in _distCentro[i]:
            # Recorremos cada pixel
            for row in range(len(c)):
                ownRow = []
                for col in range(len(c[row])):
                    if ic > 0:
                        cent = ownr[i][row][col][0] # Mejor centro
                        mDist = ownr[i][row][col][1] # Menor distancia
                        cDist = c[row][col] # Distancia del p actual al c actual
                        if cent == -1 or mDist > cDist:
                            ownr[i][row][col] = (ic, cDist)
                    else:
                        ownRow.append((ic, c[row][col]))
                if ic == 0:
                    ownr[i].append(ownRow)
            ic = ic + 1
    return ownr

def fnGetDistCenters(_c, dVarN):
    distCentro = dict()
    sumDistCent = dict()
    # Se recorre cada imagen
    for i in _c.keys():
        distCentro[i] = list()
        sumDistCent[i] = list()
        # Se recorre cada centro
        ic = 0
        for c in _c[i]:
            # Se recorre cada instancia
            distCentTot = []
            sumDist = 0
            for row in range(len(dVarN[i])):
                distCentRow = list()
                for col in range(len(dVarN[i][row])):
                    # Se calcula la distancia entre la variable de la instancia y la del centro
                    dist = 0
                    val = dVarN[i][row][col]
                    dist = dist + math.pow((val - c), 2)
                    dcc = math.sqrt(dist)
                    distCentRow.append(dcc)
                    sumDist = sumDist + dcc
                distCentTot.append(distCentRow)
            distCentro[i].append(distCentTot)
            sumDistCent[i].append(sumDist)
            ic = ic + 1
    return distCentro, sumDistCent

def fnKmeansNoSup(_StrtCent, _VarNorm, Pnew, _a0, _aa, _ab, _nc, _wn):
    print('Inicia Kmeans.')
    # Asignamos registros a centros
    print('Obtener distancia a centros.')
    distCentro, sumDist = fnGetDistCenters(_StrtCent, _VarNorm)
    print('Asignamos registros a centros')
    owner = fnGetOwnership(distCentro)
    # Centramos los centros en sus grupos
    print('Recalcular posicion de centros')
    centros = fnCenterCenters(_StrtCent, owner, _VarNorm)
    # Calculamos fitnes de los centros
    fCl = dict()
    fCs = dict()
    for i in _VarNorm.keys():
        fCs[i] = (0, -1)
        fCl[i] = (1, 1)
        # Repetimos hasta que f(Cs) > ab * f(Cl)
        while fCs[i][1] <= _ab * fCl[i][1]:
            # Repetimos hasta que f(Cs) > aa * f(Cl)
            while fCs[i][1] <= _aa * fCl[i][1]:
                # - Paso 5
                print('Calcular Fitness')
                fCentros, pxFit = fnCalcFitness(_VarNorm, Pnew, centros, owner)
                fCs, fCl = fnGetfSLCent(fCentros)
                # - Paso 6
                trshold = _aa * fCl[i][1]
                if fCs[i][1] < trshold:
                    # Regalamos pixeles
                    detail = int((len(owner[i]) * len(owner[i][0])) / 1040)
                    owner = fnGiftPixels(owner, i, pxFit, fCs[i][0], fCl[i][0], (trshold - fCs[i][1]) / detail)
                # - Paso 7
                _aa = _aa - (_aa / _nc)
                print('Recalcular posicion de centros')
                centros = fnCenterCenters(centros, owner, _VarNorm)
            # - Paso 8
            # Asignamos registros a centros
            print('Obtener distancia a centros.')
            distCentro, sumDist = fnGetDistCenters(centros, _VarNorm)
            print('Asignamos registros a centros')
            owner = fnGetOwnership(distCentro)
            # Centramos los centros en sus grupos
            print('Recalcular posicion de centros')
            centros = fnCenterCenters(centros, owner, _VarNorm)
            # - Paso 9
            _aa = _a0
            _ab = _ab  - (_ab / _nc)
    return centros, owner, fCentros, sumDist

def fnStartCentros(nc, dVMax):
    centros = dict()
    for i in dVMax.keys():
        centros[i] = list()
        nextC = 1 / (nc - 1)
        for n in range(nc):
            if n == 0:
                centros[i].append(0)
            elif n == 1:
                centros[i].append(1)
            else:
                centros[i].append((n - 1) * nextC)
    return centros

def fnGetPnew(_dVar, _i, _r, _c, _wn):
    dif = int((_wn - 1) / 2)
    pxn = 0
    n = 0
    for r in range(_r - dif, _r + dif):
        if r >= 0 and r < len(_dVar[_i]):
            for c in range(_c - dif, _c + dif):
                if c >= 0 and c < len(_dVar[_i][0]):
                    val = _dVar[_i][r][c]
                    pxn = pxn + val
                    n = n + 1
    pn = pxn / n
    return pn

def fnGetData(_nc, _wn):
    # Lee los datos de los archivos con formato .jpeg en la direccion ingresada en el campo de texto
    dictVar = dict()
    dictVarMax = dict()
    dictVarMin = dict()
    dictVarNorm = dict()
    Pnew = dict()
    ventana.txtOutput = 0
    # Abrimos el archivo
    print('Leyendo archivos...')
    # Get list of image paths
    paths = list()
    for path in pathlib.Path(ventana.filePath).rglob("*.jpg"):
        paths.append(str(path))
    # Get Variables, normalized, max and min
    i = 0
    if len(paths) == 1:
        for p in paths:
            print("Leyendo imagen " + str(i))
            preImg = Image.open(p).convert('L')
            img = np.array(preImg)
            dictVar[i] = copy.deepcopy(img)
            dictVarMax[i] = -1
            dictVarMin[i] = -1
            dictVarNorm[i] = []
            Pnew[i] = []
            for row in dictVar[i]:
                for px in row:
                        if dictVarMax[i] == -1 or dictVarMax[i] < px:
                            dictVarMax[i] = px
                        if dictVarMin[i] == -1 or dictVarMin[i] > px:
                            dictVarMin[i] = px
            # Obtenemos valores normalizados y Pnew
            print("Obteniendo m y b")
            m = float(1 / (dictVarMax[i] - dictVarMin[i]))
            b = float(-1 * (m * dictVarMin[i]))
            print("Obteniendo valores normalizados")
            for row in range(len(dictVar[i])):
                rowNorm = []
                pnewRow = []
                for col in range(len(dictVar[i][row])):
                    val = dictVar[i][row][col]
                    px = (m * val) + b
                    rowNorm.append(px)
                    pnewRow.append(fnGetPnew(dictVar, i, row, col, _wn))
                dictVarNorm[i].append(rowNorm)
                Pnew[i].append(pnewRow)
            # Inicializamos centros
            centrosIniciales = fnStartCentros(_nc, dictVarMax)
            i = i + 1
    return centrosIniciales, dictVarNorm, dictVarMax, dictVarMin, Pnew

def fnStart():
    #try:
        windowN = 5
        nc = 2
        a0 = (1 / 3) * (1 / nc)
        aa = copy.deepcopy(a0)
        ab = copy.deepcopy(a0)
        dStrtCent, dVarNorm, dMax, dMin, Pnew = fnGetData(nc, windowN)
        # Se ejecuta el kmeans modificado
        centros, own, fitness, sumDist = fnKmeansNoSup(dStrtCent, dVarNorm, Pnew, a0, aa, ab, nc, windowN)
        print('Loggeamos resultados.')
        result = fnPlot(centros, dMax, dMin, own, fitness)
        logResults(result, fitness, sumDist)
    #except:
        #messagebox.showerror("Error al leer el archivo", "Por favor verifique que la ruta y el archivo tengan el formato correcto.\nLa ruta ingresada debe ser una carpeta que contenga solamente 1 imagen en formato *.jpg, de preferencia con dimensiones menores a 500 pixeles.")


def fnExaminar():
    #try:
        # Abre el explorador de archivos de windows e inserta la direccion del archivo seleccionado en el campo de texto
        # PARAMETROS DE -> filedialog.askopenfilename(title= 'titulo de la ventana de explorador de archivos', filetypes= 'los tipos de archivo que se podran seleccionar en la ventana ('descripcion', 'tipo de dato')')
        ventana.filePath = filedialog.askdirectory()
        #PARAMETROS DE -> txtFilePath.delete('coordenada de inicio', 'coordenada de fin')
        txtFilePath.delete(1.0, END)
        txtFilePath.insert(1.0, ventana.filePath)
    #except:
        #messagebox.showerror("Error de buscador de archivos", "Error al intentar acceder al buscador de archivos.")

# Se crea el objeto ventana
ventana = tkinter.Tk()
ventana.title("K-means Clustering no Supervisado")
ventana.geometry("750x150")
ventana.filePath = ""

# Frame de datos
dataFrame = tkinter.Frame(ventana)

# Botones de ejecucion
execFrame = tkinter.Frame(ventana)

btnReadDS = tkinter.Button(execFrame, text="Leer Dataset", command=fnStart)
btnReadDS.grid(row=0, column=0)

# Se crean elementos del buscador de archivos
fileFrame = tkinter.Frame(ventana)

strPedirArchivo = tkinter.Label(fileFrame, text = "Dataset: ")
strPedirArchivo.grid(row=0, column=0)

txtFilePath = tkinter.Text(fileFrame, width=70, height=1)
txtFilePath.grid(row=0, column=1)

btnExaminar = tkinter.Button(fileFrame, text = "Examinar", command = fnExaminar)
btnExaminar.grid(row=0, column=2)

# Se empacan los objetos
fileFrame.pack(side=TOP)
execFrame.pack(side=tkinter.BOTTOM)
dataFrame.pack()


# Se llama la ventana
ventana.mainloop()