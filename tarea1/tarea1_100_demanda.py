from pulp import *


def resolver_problema(problema: LpProblem, mensaje: str):
    problema.solve(PULP_CBC_CMD(msg=False))

    print(mensaje)
    print(LpStatus[problema.status])

    for var in problema.variables():
        print(f"{var.name}={var.varValue}")

    print(f"Z = {value(problema.objective)}")


# Problema original
problema = LpProblem("Problema Adicional #1: Incrementar en 100% demanda de Alpha en bodega Este", LpMinimize)

# [Variables Continuas]
## PRODUCTO ALPHA
x_alpha_ne = LpVariable("x_alpha_ne", lowBound=0)  # alpha norte a este
x_alpha_no = LpVariable("x_alpha_no", lowBound=0)  # alpha norte a oeste
x_alpha_nc = LpVariable("x_alpha_nc", lowBound=0)  # alpha norte a centro

x_alpha_se = LpVariable("x_alpha_se", lowBound=0)  # alpha sur a este
x_alpha_so = LpVariable("x_alpha_so", lowBound=0)  # alpha sur a oeste
x_alpha_sc = LpVariable("x_alpha_sc", lowBound=0)  # alpha sur a centro

## PRODUCTO BETA
x_beta_ne = LpVariable("x_beta_ne", lowBound=0)  # beta norte a este
x_beta_no = LpVariable("x_beta_no", lowBound=0)  # beta norte a oeste
x_beta_nc = LpVariable("x_beta_nc", lowBound=0)  #  beta norte a centro

x_beta_se = LpVariable("x_beta_se", lowBound=0)  # beta sur a este
x_beta_so = LpVariable("x_beta_so", lowBound=0)  # beta sur a oeste
x_beta_sc = LpVariable("x_beta_sc", lowBound=0)  # beta sur a centro

# [Variables Binarias]
## PRODUCTOS PRODUCIDOS EN PLANTA NORTE O SUR
y_alpha_n = LpVariable("y_alpha_n", cat=LpBinary)  # alpha se produce en norte
y_alpha_s = LpVariable("y_alpha_s", cat=LpBinary)  # alpha se produce en sur
y_beta_n = LpVariable("y_beta_n", cat=LpBinary)  # beta se produce en norte
y_beta_s = LpVariable("y_beta_s", cat=LpBinary)  # beta se produce en sur

## APERTURA DE BODEGAS
y_e = LpVariable("y_e", cat=LpBinary)  # Se abre bodega del este
y_o = LpVariable("y_o", cat=LpBinary)  # Se abre bodega del oeste
y_c = LpVariable("y_c", cat=LpBinary)  # Se abre bodega del centro

# [Funcion Objetivo]
problema += (
    # Costo de produccion
    5 * (x_alpha_ne + x_alpha_no + x_alpha_nc)
    + 4 * (x_alpha_se + x_alpha_so + x_alpha_sc)
    + 6 * (x_beta_ne + x_beta_no + x_beta_nc)
    + 7 * (x_beta_se + x_beta_so + x_beta_sc)
    # Costos de transporte
    + 2 * x_alpha_ne
    + 3 * x_alpha_no
    + 4 * x_alpha_nc
    + 6 * x_alpha_se
    + 4 * x_alpha_so
    + 3 * x_alpha_sc
    + 3 * x_beta_ne
    + 2 * x_beta_no
    + 5 * x_beta_nc
    + 2 * x_beta_se
    + 3 * x_beta_so
    + 2 * x_beta_sc
    # Costos de preparacion
    + 30 * (y_alpha_n + y_alpha_s)
    + 25 * (y_beta_n + y_beta_s)
    # Costos fijos de bodegas
    + 50 * y_e
    + 40 * y_o
    + 60 * y_c
), "Costo total"


# [Restricciones]
## CAPACIDADES DE PRODUCCION DE PLANTAS (HORAS)
problema += (
    3 * (x_alpha_ne + x_alpha_no + x_alpha_nc) + 2 * (x_beta_ne + x_beta_no + x_beta_nc)
    <= 120,
    "Capacidad en horas de la planta Norte",
)

problema += (
    2 * (x_alpha_se + x_alpha_so + x_alpha_sc) + 4 * (x_beta_se + x_beta_so + x_beta_sc)
    <= 150,
    "Capacidad en horas de la planta Sur",
)

## CAPACIDAD DE BODEGAS
problema += (
    x_alpha_ne + x_alpha_se + x_beta_ne + x_beta_se <= 80,
    "Capacidad bodega este",
)

problema += (
    x_alpha_no + x_alpha_so + x_beta_no + x_beta_so <= 70,
    "Capacidad bodega oeste",
)

problema += (
    x_alpha_nc + x_alpha_sc + x_beta_nc + x_beta_sc <= 100,
    "Capacidad bodega centro",
)

## SATISFACCION DE DEMANDA DE BODEGAS ABIERTAS
problema += x_alpha_ne + x_alpha_se >= 60 * y_e, "Demanda bodega este para alpha" # Originalmente 30

problema += x_alpha_no + x_alpha_so >= 20 * y_o, "Demanda bodega oeste para alpha"

problema += x_alpha_nc + x_alpha_sc >= 25 * y_c, "Demanda bodega centro para alpha"

problema += x_beta_ne + x_beta_se >= 20 * y_e, "Demanda bodega este para beta"

problema += x_beta_no + x_beta_so >= 30 * y_o, "Demanda bodega oeste para beta"

problema += x_beta_nc + x_beta_sc >= 35 * y_c, "Demanda bodega centro para beta"

## RESTRICCIONES DE ACOPLAMIENTO
M = 150

### Plantas preparadas
problema += (
    x_alpha_ne + x_alpha_no + x_alpha_nc <= M * y_alpha_n,
    "Producir alpha en planta norte",
)
problema += (
    x_alpha_se + x_alpha_so + x_alpha_sc <= M * y_alpha_s,
    "Producir alpha en planta sur",
)

problema += (
    x_beta_ne + x_beta_no + x_beta_nc <= M * y_beta_n,
    "Producir beta en planta norte",
)

problema += (
    x_beta_se + x_beta_so + x_beta_sc <= M * y_beta_s,
    "Producir beta en planta sur",
)

### Bodegas abiertas
problema += (
    x_alpha_ne + x_alpha_se + x_beta_ne + x_beta_se <= M * y_e,
    "Abrir bodega este",
)

problema += (
    x_alpha_no + x_alpha_so + x_beta_no + x_beta_so <= M * y_o,
    "Abrir bodega oeste",
)

problema += (
    x_alpha_nc + x_alpha_sc + x_beta_nc + x_beta_sc <= M * y_c,
    "Abrir bodega centro",
)

problema += y_e + y_o + y_c >= 2, "Al menos dos bodegas abiertas"
resolver_problema(problema, "Problema Adicional #1: Incrementar en 100% demanda de Alpha en bodega Este")
