import pandas as pd
import numpy as np
import codecs

RI_file = "./output/computed_RI_for_officies.csv"
Impact_file = "./input/turnover_french_companies_2016_2021.csv"
output_file = "./output/RI_vs_CrisisImpact.csv"
RI_table = pd.read_csv(RI_file, header=1).to_numpy()
Impact_table = pd.read_csv(Impact_file, header=1).to_numpy()
print(RI_table)

#print(Impact_table)

with codecs.open(output_file, "w", "utf8") as o:
	headers = "siren,2016,2017,2018,2019,2020,2021,PRED2020,PRED2021,VARIA2020,VARIA2021,EVO20-21,PRED6_2022,EVOPRED6_2022,siret,naf,ri,F_1_4,F_2_2,F_2_4,F_3_3"
	o.write(f"{headers}\n")

	for i in range(0, len(Impact_table)):
		siren = Impact_table[i][0]
		Impact_data = Impact_table[i]
		idx = -1
		RI_data  = []

		print("siren=", siren)
		for j in range(0, len(RI_table)):
			siren2 = str(RI_table[j][0])[0:9]
			if (int(siren2)==int(siren)):
				print("siren2",siren2)
				RI_data = RI_table[j][0:]
				idx = j
				All_data = np.concatenate((Impact_data, RI_data))
				print("trouvé", All_data)
				o.write(f"{All_data[0]},{All_data[1]},{All_data[2]},{All_data[3]},{All_data[4]},{All_data[5]},{All_data[6]},{All_data[7]},{All_data[8]},{All_data[9]},{All_data[10]},{All_data[11]},{All_data[12]},{All_data[13]},{All_data[14]},{All_data[15]},{All_data[16]},{All_data[17]},{All_data[18]},{All_data[19]},{All_data[20]}\n")
		
		#if(idx>=0):
		#	print("trouvé au moins une fois")
			#o.flush()
		#else:
			#print("non trouvé")
