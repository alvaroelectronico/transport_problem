from pulp import*


def solvePuLP (Plantas, Clientes, Oferta, Demanda, CosteUnitario):
    modelMinCoste = LpProblem("MinCoste", LpMinimize)
    Transporte=LpVariable.dicts('Transporte', [(p,c) for p in Plantas for c in Clientes], lowBound = 0)

    for p in Plantas:
        modelMinCoste+=LpConstraint(sum(Transporte[p,c] for c in Clientes), sense=LpConstraintGE, rhs= Oferta[p], name='Oferta'+str(p))

    for c in Clientes:
        modelMinCoste += LpConstraint(sum(Transporte[p, c] for p in Plantas), sense=LpConstraintGE, rhs=Demanda[c],
                                      name='Demanda' + str(c))

    modelMinCoste+=sum(Transporte[p,c]*CosteUnitario[p,c] for p in Plantas for c in Clientes)

    modelMinCoste.solve()

    # print ('Coste mínimo: ' + str(value(modelMinCoste.objective)))
    # for p in Plantas:
    #     for c in Clientes:
    #         if Transporte[p,c].varValue>0:
    #              print (str(Transporte[p,c].varValue) + ' camiones de ' + str(p) + ' a ' +str(c))

    TransporteSalida = {(p,c): Transporte[p, c].varValue for p in Plantas for c in Clientes}

    return value(modelMinCoste.objective), TransporteSalida
