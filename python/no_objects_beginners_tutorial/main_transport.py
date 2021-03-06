#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from lectura_excel_transport import readExcel
import pandas as pd
from random_instances import generate_random_instance
import pulp_transport
import pyomo_transport_functions as pytr
from question_generator import create_xml_elem, save_to_file, prettify
from xml.etree import ElementTree

# Plants, Customers, Capacity, Demand, UnitaryCost = readExcel("..\datos_entrada.xlsx")
Plants, Customers, Capacity, Demand, UnitaryCost = generate_random_instance()

#solve with pyomo funcionts
# model = pytr.create_model(Plants, Customers, Capacity, Demand, UnitaryCost)
# instance = pytr.CreateInstance(model)
# results = pytr.SolveInstance(instance)


# Invoking the solvePulP funcion to use PuLP
minCoste, transport = pulp_transport.solvePuLP(Plants, Customers, Capacity, Demand, UnitaryCost)

print ('Coste mínimo: {}'.format(minCoste))
for (p,c) in [(p, c) for p in Plants for c in Customers if transport[p,c] > 0 ]:
    print("{} trucks from {} to {}".format(transport[p,c], p, c))

no_questions = 50
questions_data = list()

for i in range(1, no_questions+1):
    no_plants = random.choice([2, 3, 4])
    no_customers = random.choice([3, 4, 5])
    Plants, Customers, Capacity, Demand, UnitaryCost = generate_random_instance(no_plants, no_customers)
    minCoste, transport = pulp_transport.solvePuLP(Plants, Customers, Capacity, Demand, UnitaryCost)
    question_name = "Tutorial AIMMS {}".format(i)
    question_text = "<![CDATA["
    question_text += "<p>DATOS DEL PROBLEMA</p>"

    question_text += "<p></p>"
    question_text += "<p><b>Datos de las plantas</b></p>"
    df = pd.DataFrame.from_dict(Capacity, orient='index')
    df.columns = ['Capacidad']
    question_text += df.to_html()

    question_text += "<p></p>"
    question_text += "<p>Datos de las clientes</p>"
    df = pd.DataFrame.from_dict(Demand, orient='index')
    df.columns = ['Demanda']
    question_text += df.to_html()

    question_text += "<p></p>"
    question_text += "<p>Costes de transporte</p>"
    col1 = [i[0] for i in UnitaryCost.keys()]
    col2 = [i[1] for i in UnitaryCost.keys()]
    col3 = [i for i in UnitaryCost.values()]
    zipped = list(zip(col1, col2, col3))
    df = pd.DataFrame(zipped, columns=['Planta', 'Cliente', 'Coste'])
    df_pivot = df.pivot(index='Planta', columns='Cliente', values='Coste')
    question_text += df_pivot.to_html()

    question_text += "<p></p>"
    question_text += "<p><b>Indicar coste del plan de transporte que ofrece el menor coste posible:</b></p>"

    question_text += "]]>"
    answer_text = '{}'.format(minCoste)
    tolerance_text = '{}'.format(0.01*minCoste)

    print(question_text)

    questions_data.append([question_name, question_text, answer_text, tolerance_text])

    # print('Coste mínimo: {}'.format(minCoste))
    # for (p, c) in [(p, c) for p in Plants for c in Customers if transport[p, c] > 0]:
    #     print("{} trucks from {} to {}".format(transport[p, c], p, c))

quiz = create_xml_elem("Tutorial AIMMS", questions_data)

prettify(quiz)

# Prettifying and saving the pretty string to an .xml file
save_to_file(quiz, "tutorial_aimms_b.xml")


#input file
fin = open("tutorial_aimms_b.xml", "rt")
#output file to write the result to
fout = open("tutorial_aimms.xml", "wt")
#for each line in the input file
for line in fin:
	#read replace the string and write to output file
    fout.write(line.replace('&lt;', '<').replace('&gt;', '>'))
#close input and output files
fin.close()
fout.close()