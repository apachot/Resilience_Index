import pandas as pd
import numpy as np
import geopy.distance
import codecs

def suppliersFromNaF(naf):
	IO_file="./input/IO-matrix.csv"
	IO_table = pd.read_csv(IO_file, sep=";" ,header=None, index_col=None).to_numpy()

	IO_table_naf = [i for i in IO_table if (float(i[0]) == float(naf))]

	IO_table_naf = IO_table_naf[0]
	IO_table_naf_nonzero = [[IO_table[0,i],IO_table_naf[i]] for i in range(0, len(IO_table_naf)) if (float(IO_table_naf[i]) > float(0))]
	IO_table_naf_nonzero = IO_table_naf_nonzero[1:]
	suppliers = IO_table_naf_nonzero
	return suppliers

def scoreLocalSuppliersFromNaf(naf, coord_x, coord_y, threshold):
	
	coords_naf = (coord_x,coord_y)

	#extract NAF code for suppliers according to IO tables 
	naf_suppliers = suppliersFromNaF(naf)

	score = 0

	for i in range(0, len(naf_suppliers)):
		#extract list of suppliers with each naf code
		officies_file="./input/offices-france.csv"
		officies_table = pd.read_csv(officies_file, sep="," ,header=1, index_col=None).to_numpy()
		code_naf_supplier = naf_suppliers[i][0]
		#print(officies_table)
		#print("on recherche les établissements de code naf=", code_naf_supplier)
		#code_naf_supplier = 8.11
		officies_table_naf_supplier = [a for a in officies_table if float(str(a[1]).split('.')[0]+'.'+str(a[1]).split('.')[1][0:2]) == float(code_naf_supplier)]
		#print(officies_table_naf_supplier)
		
		supplierFound = 0
		for j in range(0, len(officies_table_naf_supplier)):
			coords_supplier = (str(officies_table_naf_supplier[j][3]).split(",")[0][1:], str(officies_table_naf_supplier[j][3]).split(",")[1][0:-1])
			#print("coordonnées = ", coords_supplier)
			distance = geopy.distance.geodesic(coords_naf, coords_supplier).km 

			if (distance <= threshold):
				supplierFound = 1
		
		if (supplierFound == 1):
			score = score + float(naf_suppliers[i][1])
	

	return min(score,1)

def scoreProductsFromLocalSuppliersFromNaf(naf):
	
	
	#extract NAF code for suppliers according to IO tables 
	naf_suppliers = suppliersFromNaF(naf)

	score = 0

	for i in range(0, len(naf_suppliers)):
		#extract list of products for each naf code
		code_naf_supplier = naf_suppliers[i][0]
		weight_naf_supplier = naf_suppliers[i][1]
		
		NAF_HS4_file = "./input/NAF_HS4.csv"
		products_table = pd.read_csv(NAF_HS4_file, sep="," ,header=1, index_col=None).to_numpy()
		#print("naf recherché=", code_naf_supplier, "poids", weight_naf_supplier)
		
		products_table_naf_supplier = [[a[1],a[2]] for a in products_table if int(a[0][0:4]) == int(str(code_naf_supplier).split('.')[0]+str(code_naf_supplier).split('.')[1])]
		
		total_score_supplier = 0

		for j in range(0, len(products_table_naf_supplier)):
			# looking for resilience values for each product
			prod = products_table_naf_supplier[j][0]
			prod_weight = products_table_naf_supplier[j][1]
			#print("produit recherché=", prod, "weight=", prod_weight)

			
			resilience_file = "./input/ranking_productive_resilience.csv"
			resilience_table = pd.read_csv(resilience_file, sep="," ,header=1, index_col=None).to_numpy()

			resilience_table_product = [a[5] for a in resilience_table if a[0] == prod]
			if len(resilience_table_product) > 0:
				#print("resilience_table_product=",resilience_table_product[0])
				total_score_supplier = total_score_supplier + prod_weight * resilience_table_product[0]

		#print ("score resilience cumulé pour ce NAF=", total_score_supplier)
		score = score + weight_naf_supplier * total_score_supplier

	#print("total_ score pour cet établissement =", score)
	return min(score,1)

def scoreDiversificationFromNaf(naf, threshold):

	
	#first we look for products associated with this naf code
	NAF_HS4_file = "./input/NAF_HS4.csv"
	products_table = pd.read_csv(NAF_HS4_file, sep="," ,header=1, index_col=None).to_numpy()
		
	products_table_naf = [[a[1],a[2]] for a in products_table if int(a[0][0:4]) == int(str(naf).split('.')[0]+str(naf).split('.')[1])]
		
	#print("products_table_naf", products_table_naf)
	score = 0

	for j in range(0, len(products_table_naf)):
		prod = products_table_naf[j][0]
		prod_weight = products_table_naf[j][1]
		#print("produit recherché=", prod, "weight=", prod_weight)

		file_proximities = "./input/HS_similarity_usingCF.csv"
		tab_proximities = pd.read_csv(file_proximities, sep="," ,header=0, index_col=None).to_numpy()
		tab_proximities_prod = [[a[1],a[2]] for a in tab_proximities if (int(a[0]) == int(prod) and float(a[2]) <= threshold and float(a[2]) > 0)]
		#print("tab_proximities_prod", tab_proximities_prod)
		if (len(tab_proximities_prod) > 0):
			score = score + prod_weight
		#print(score)

	#print("score diversification=", score)

	return min(score,1)

def scoreDiversificationHRFromNaf(naf, threshold):
	score = 0

	max_jumps = 47

	#looking for NAF-ROME weighted correspondance
	NAF_ROME_file = "./input/APE_ROME.csv"
	NAF_ROME_tab = pd.read_csv(NAF_ROME_file, sep=";" ,header=1, index_col=None).to_numpy()

	NAF_ROME_tab_naf = [[a[1],a[2]] for a in NAF_ROME_tab if float(str(a[0][0:5])) == naf]
	#print(NAF_ROME_tab_naf)

	for i in range(0, len(NAF_ROME_tab_naf)):
		code_rome = NAF_ROME_tab_naf[i][0]
		code_rome_weight = NAF_ROME_tab_naf[i][1]
		#print("code_rome_weight", code_rome_weight)

		#print("métier trouvé=", code_rome, "weight=", code_rome_weight)

		#looking for job jumps
		ROME_proximities_file = "./input/ROME_proximities.csv"
		ROME_proximities_tab = pd.read_csv(ROME_proximities_file, sep=";" ,header=1, index_col=None).to_numpy()

		ROME_proximities_tab_rome = [a for a in ROME_proximities_tab if (a[0] == code_rome and a[2] <= threshold  and a[2] > 0)]

		if (len(ROME_proximities_tab_rome)):
			score = score + code_rome_weight * (len(ROME_proximities_tab_rome) / max_jumps)

			#print("score=",score, "code_rome_weight", code_rome_weight, "len(ROME_proximities_tab_rome)", len(ROME_proximities_tab_rome))

		

	#print("score diversification rh=", score)
	return min(score,1)

def compute_RI(F_1_4, F_2_2, F_2_4, F_3_3):
	return F_1_4 * (F_2_2 * F_2_4 + 20) * F_3_3 + 42 * F_1_4 + 72 * (F_2_2 * F_2_4 + 20) + 40 * F_3_3 + 718 

#F^1_4 : Source de secours pour les fournisseurs locaux 
def compute_F_1_4(naf, coord_x, coord_y, threshold):
	F_1_4 = 10 * scoreLocalSuppliersFromNaf(naf, coord_x, coord_y, threshold)
	return F_1_4

#F^2_2 : Agilité
def compute_F_2_2(naf, threshold):
	F_2_2 = 10 * scoreDiversificationFromNaf(naf, threshold)
	return F_2_2

#F^2_4 : Main-d’œuvre polyvalente dans l’organisation
def compute_F_2_4(naf, threshold):
	F_2_4 = 10 * scoreDiversificationHRFromNaf(naf, threshold)
	return F_2_4

#F^3_1 : Flexibilité de la production 
#def compute_F_3_1(naf, threshold):
#	F_3_1 =  0
#	return F_3_1

#F^3_3 : Flexibilité de l’approvisionnement
def compute_F_3_3(naf):
	F_3_3 = 10 * scoreProductsFromLocalSuppliersFromNaf(naf)
	return F_3_3


def compute_naf_RI(naf, coord_x, coord_y):
	

	#look for naf code
	F_1_4 = compute_F_1_4(naf, coord_x, coord_y, 200)
	F_2_2 = compute_F_2_2(naf, 0.8)
	F_2_4 = compute_F_2_4(naf, 0.9)
	#F_3_1 = compute_F_3_1(naf, )
	F_3_3 = compute_F_3_3(naf)
	return compute_RI(F_1_4, F_2_2, F_2_4, F_3_3), F_1_4, F_2_2, F_2_4, F_3_3




#coords_naf = (45.244352,4.271605)
naf = 13.96
coord_x = 45.244352
coord_y = 4.271605

all_officies_file="./input/offices-france.csv"
all_officies_table = pd.read_csv(all_officies_file, sep="," ,header=1, index_col=None).to_numpy()

NAF_HS4_file = "./input/NAF_HS4.csv"
products_table = pd.read_csv(NAF_HS4_file, sep="," ,header=1, index_col=None).to_numpy()

output_filename = "./output/computed_RI_for_officies.csv"
with codecs.open(output_filename, "w", "utf8") as o:
	o.write(f"siret,naf,ri,F_1_4,F_2_2,F_2_4,F_3_3\n")
	for i in range(0, len(all_officies_table)):
		siret = all_officies_table[i][0]
		naf = float(all_officies_table[i][1][0:5])
		coord_x = float(str(all_officies_table[i][3].split(',')[0][1:]))
		coord_y = float(str(all_officies_table[i][3].split(',')[1][0:-1]))
		
		#we verify that thos etabilishment is industrial
		products_table_naf = [[a[1],a[2]] for a in products_table if int(a[0][0:4]) == int(str(naf).split('.')[0]+str(naf).split('.')[1])]
	
		if(len(products_table_naf)):
			#print("(", i ,"/", len(all_officies_table),": Etablissement", all_officies_table[i][4], " (", naf, ")")
			#print("coord_x=", coord_x, "coord_y=", coord_y, "origin=", all_officies_table[i][3])
			RI, F_1_4, F_2_2, F_2_4, F_3_3 = compute_naf_RI(naf, coord_x, coord_y)
			print("[" , i , "/" , len(all_officies_table) , "]" , round(RI,2),round(F_1_4,2),round(F_2_2,2),round(F_2_4,2),round(F_3_3,2),"(siret=",siret,")")
			o.write(f"{siret},{all_officies_table[i][1]},{round(RI,2)},{round(F_1_4,2)},{round(F_2_2,2)},{round(F_2_4,2)},{round(F_3_3,2)}\n")
			o.flush()


