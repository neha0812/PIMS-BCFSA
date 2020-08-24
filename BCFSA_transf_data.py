


import pandas as pd
import numpy as np
import io
import json
import requests



def transformed_data():


	url = 'https://raw.githubusercontent.com/shughestr/PIMS_2020_Real_Estate_data/master/sample_clean.csv'
	df = pd.read_csv(url, error_bad_lines=False)




### Normalise absolute value of crime variables and income recipients by the respective population 

	for col in ['saf1','saf2','saf3','saf4','saf5','saf6','saf7','saf8','inc2']:
	    df[col] = 100 * df[col] / df['pop1'] 




### Adding vacancy rate column from other census dataset

	data2 = requests.get('https://data.calgary.ca/resource/set9-futw.json')
	df2 = pd.DataFrame(json.loads(data2.text))

	df2 = df2.loc[df2['dwelling_type_code'].isin([str(x) for x in range(1,11)])]

	df2 = df2.drop(labels = ['census_year', 'community','ward','dwelling_type','dwelling_type_code','dwelling_type_description'],axis=1)

	df2[['dwelling_cnt', 'resident_cnt', 'ocpd_dwelling_cnt',
       'vacant_dwelling_cnt', 'ocpd_ownership_cnt', 'renovation_dwelling_cnt',
       'under_const_dwelling_cnt', 'inactive_cnt', 'other_purpose_cnt']] = df2[['dwelling_cnt', 'resident_cnt', 'ocpd_dwelling_cnt',
       'vacant_dwelling_cnt', 'ocpd_ownership_cnt', 'renovation_dwelling_cnt',
       'under_const_dwelling_cnt', 'inactive_cnt', 'other_purpose_cnt']].astype(int)

	df2=df2.groupby(['code']).sum()

	df2['vacancy_rate'] = df2['vacant_dwelling_cnt']/(df2['vacant_dwelling_cnt']+df2['ocpd_dwelling_cnt']) * 100

	df2vac = df2['vacancy_rate']

	vacdict = df2vac.to_dict()

	df['vacancy_rate'] = 0

	for x in vacdict:
		df['vacancy_rate'] = np.where(df['COMM_CODE']==x, vacdict[x],df['vacancy_rate'])
		## I have added the code for addding the walk,transit, bike score and community population
        url = 'https://raw.githubusercontent.com/neha0812/BCFFSA-project/master/walk_score.csv'
        df3 = pd.read_csv(url, error_bad_lines=False)
# making the entries of both the csv files in lowercase for mapping purpose.
        df = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)  
        df3 = df3.apply(lambda x: x.str.lower() if x.dtype == "object" else x)  
        df3 = df3.set_index('Name')
#Adding walk score, bike score, transit score and population for different community in calgary
        df['walk_score_comm'] = df['COMM_NAME'].map(df3['Walk Score'])
        df['transit_score_comm'] = df['COMM_NAME'].map(df3['Transit Score'])
        df['bike_score_comm'] = df['COMM_NAME'].map(df3['Bike Score'])
        df['comm_polulation'] = df['COMM_NAME'].map(df3['Population'])    
	return df



