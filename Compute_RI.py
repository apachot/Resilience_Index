import pandas as pd
import numpy as np
import geopy.distance


def suppliersFromNaF(naf):
	IO_file="./input/IO-matrix.csv"
	IO_table = pd.read_csv(IO_file, sep=";" ,header=None, index_col=None).to_numpy()

	IO_table_naf = [i for i in IO_table if (float(i[0]) == float(naf))]

	IO_table_naf = IO_table_naf[0]
	IO_table_naf_nonzero = [[IO_table[0,i],IO_table_naf[i]] for i in range(0, len(IO_table_naf)) if (float(IO_table_naf[i]) > float(0))]
	IO_table_naf_nonzero = IO_table_naf_nonzero[1:]
	suppliers = IO_table_naf_nonzero
	return suppliers

def scoreLocalSuppliersFromNaf(naf, coord_x, coord_y, threshold=100):
	
	
	#extract GPS coordinates from siret
	coords_naf = (coord_x,coord_y)

	#extract NAF code for suppliers according to IO tables 
	naf_suppliers = suppliersFromNaF(naf)

	score = 0

	for i in range(0, len(naf_suppliers)):
		#extract list of suppliers with each naf code
		officies_file="./input/etablishments-france-department43.csv"
		officies_table = pd.read_csv(officies_file, sep="," ,header=1, index_col=None).to_numpy()
		code_naf_supplier = naf_suppliers[i][0]
		#print(officies_table)
		print("on recherche les établissements de code naf=", code_naf_supplier)
		#code_naf_supplier = 8.11
		officies_table_naf_supplier = [a for a in officies_table if float(str(a[1]).split('.')[0]+'.'+str(a[1]).split('.')[1][0:2]) == float(code_naf_supplier)]
		#print(officies_table_naf_supplier)
		
		supplierFound = 0
		for j in range(0, len(officies_table_naf_supplier)):
			coords_supplier = (str(officies_table_naf_supplier[j][3]).split(",")[0][1:], str(officies_table_naf_supplier[j][3]).split(",")[1][0:-1])
			print("coordonnées = ", coords_supplier)
			distance = geopy.distance.geodesic(coords_naf, coords_supplier).km 

			if (distance <= threshold):
				supplierFound = 1
		
		if (supplierFound == 1):
			score = score + float(naf_suppliers[i][1])
	

	return score * 5

def compute_RI(F_1_4, F_2_2, F_2_4, F_3_1, F_3_3):
	return F_1_4 * (F_2_2 * F_2_4 + 20) * (F_3_1 * F_3_3) + 42 * F_1_4 + 72 * (F_2_2 * F_2_4 + 20) + 40 * (F_3_1 * F_3_3) + 718 

#F^1_4 : Source de secours pour les fournisseurs locaux 
def compute_F_1_4(naf, coord_x, coord_y):
	F_1_4 = scoreLocalSuppliersFromNaf(naf, coord_x, coord_y, 100)
	return F_1_4

#F^2_2 : Agilité
def compute_F_2_2(naf, coord_x, coord_y):
	F_2_2 = 0
	return F_2_2

#F^2_4 : Main-d’œuvre polyvalente dans l’organisation
def compute_F_2_4(naf, coord_x, coord_y):
	F_2_4 = 0
	return F_2_4

#F^3_1 : Flexibilité de la production 
def compute_F_3_1(naf, coord_x, coord_y):
	F_3_1 = 0
	return F_3_1

#F^3_3 : Flexibilité de l’approvisionnement
def compute_F_3_3(naf, coord_x, coord_y):
	F_3_3 = 0
	return F_3_3



def compute_siren_RI(naf, coord_x, coord_y):
	

	#look for naf code
	F_1_4 = compute_F_1_4(naf, coord_x, coord_y)
	F_2_2 = compute_F_2_2(naf, coord_x, coord_y)
	F_2_4 = compute_F_2_4(naf, coord_x, coord_y)
	F_3_1 = compute_F_3_1(naf, coord_x, coord_y)
	F_3_3 = compute_F_3_3(naf, coord_x, coord_y)
	return compute_RI(F_1_4, F_2_2, F_2_4, F_3_1, F_3_3)


#suppliers = suppliersFromNaF(80.30)
#print("suppliers=", suppliers)


#coords_naf = (45.244352,4.271605)
naf = 13.96
coord_x = 45.244352
coord_y = 4.271605

suppliers = suppliersFromNaF(naf)
print("suppliers=", suppliers)



RI = compute_siren_RI(naf, coord_x, coord_y)
print("RI=", RI)