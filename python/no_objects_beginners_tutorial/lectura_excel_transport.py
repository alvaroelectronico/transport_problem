import xlrd
import pandas as pd
from requests.utils import dict_from_cookiejar


def leerExcel (ruta):
    wb = xlrd.open_workbook(ruta)

    sheet = wb.sheet_by_name("oferta")
    Oferta = {sheet.cell_value(r,0): sheet.cell_value(r,1)
                for r in range(0, sheet.nrows)}
    Plantas = list(Oferta.keys())

    sheet = wb.sheet_by_name("demanda")
    Demanda = {sheet.cell_value(r,0): sheet.cell_value(r,1)
                for r in range(0, sheet.nrows)}
    Clientes = list(Demanda.keys())

    sheet = wb.sheet_by_name("coste_transporte")
    CosteUnitario = {(sheet.cell_value(r,0), sheet.cell_value(r,1)): sheet.cell_value(r,2)
                for r in range(0, sheet.nrows)}

    return Plantas, Clientes, Oferta, Demanda, CosteUnitario

    print (Plantas)
    print (Oferta)
    print (Clientes)
    print (Demanda)
    print (CosteUnitario)

def readExcel(path):
    df_capacity = pd.read_excel(path, sheet_name="oferta", header=None)
    df_capacity.set_index(0, inplace=True)
    Capacity = df_capacity.to_dict()[1]
    Plants = list(Capacity.keys())

    df_demand = pd.read_excel(path, sheet_name="demanda", header=None)
    df_demand.set_index(0, inplace=True)
    Demand = df_demand.to_dict()[1]
    Customers = list(Demand.keys())

    df_unitary_cost = pd.read_excel(path, sheet_name="coste_transporte", header=None)
    df_unitary_cost.set_index([0, 1], inplace=True)
    UnitaryCost = df_unitary_cost.to_dict()[2]

    return Plants, Customers, Capacity, Demand, UnitaryCost
