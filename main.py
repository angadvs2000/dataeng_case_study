import pandas as pd
import numpy as np
import utils

data = utils.get_data()

# Q1
primary_df = data.primary()
primary_df2 = primary_df[(primary_df['DEATH_CNT'] != 0) & (primary_df['PRSN_GNDR_ID'] == 'MALE')][['CRASH_ID','DEATH_CNT']].groupby('CRASH_ID').sum()
primary_df3 = primary_df2[primary_df2['DEATH_CNT'] >= 2]
print(len(primary_df3))



# Q2
unit_df = data.units()
charge_df = data.charges()

'''
two_wheller_crashId = set(unit_df[(unit_df['VEH_BODY_STYL_ID'] == 'MOTORCYCLE') | 
                                  (unit_df['VEH_BODY_STYL_ID'] == 'POLICE MOTORCYCLE')]['CRASH_ID'])
crashes_charged = two_wheller_crashId.intersection(set(charge_df['CRASH_ID']))
print(len(crashes_charged))
'''

merged_df = pd.merge(unit_df[(unit_df['VEH_BODY_STYL_ID'] == 'MOTORCYCLE') | 
                                  (unit_df['VEH_BODY_STYL_ID'] == 'POLICE MOTORCYCLE')][['CRASH_ID', 'UNIT_NBR', 'VIN']], charge_df[['CRASH_ID', 'UNIT_NBR']], on=['CRASH_ID', 'UNIT_NBR'], how='inner')
print(len(set(merged_df['VIN'])))



# Q3
# added suv in car type (unclear about this!), taken liberty and chose the following car types

vehicle_unit_df = unit_df[unit_df['VEH_BODY_STYL_ID'].isin(['PASSENGER CAR, 2-DOOR','PASSENGER CAR, 4-DOOR', 'POLICE CAR/TRUCK', 'SPORT UTILITY VEHICLE'])][['CRASH_ID', 'UNIT_NBR', 'VEH_MAKE_ID']]
filtered_person_df = primary_df[(primary_df['PRSN_AIRBAG_ID'].isin(['NOT DEPLOYED','DEPLOYED, SIDE', 'DEPLOYED, REAR'])) & (primary_df['PRSN_TYPE_ID'] == 'DRIVER') & (primary_df['DEATH_CNT'] != 0)][['CRASH_ID', 'UNIT_NBR']]
merged_df = pd.merge(vehicle_unit_df, filtered_person_df, on=['CRASH_ID', 'UNIT_NBR'], how='inner')
print(list(merged_df[['VEH_MAKE_ID']].groupby('VEH_MAKE_ID').size().sort_values(ascending=False).reset_index()[:5]['VEH_MAKE_ID']))
# below list top 4 more than one, last car type has 1 such crash which is also equal to 7 other types as listed|||| but if include rear ands side airbags then top 5
# print(merged_df[['VEH_MAKE_ID']].groupby('VEH_MAKE_ID').size().sort_values(ascending=False))


# Q4

valid_lic_driverdf = primary_df[primary_df['DRVR_LIC_TYPE_ID'].isin(['COMMERCIAL DRIVER LIC.', 'DRIVER LICENSE'])&(primary_df['PRSN_TYPE_ID'] == 'DRIVER')]
hitandrun_df = unit_df[unit_df['VEH_HNR_FL']=='Y']
merged_df = pd.merge(valid_lic_driverdf, hitandrun_df, on=['CRASH_ID', 'UNIT_NBR'], how='inner')
print(len(set(merged_df['VIN'])))



# Q5

cars_with_women = list(set(primary_df[primary_df['PRSN_GNDR_ID'] == 'FEMALE'][['CRASH_ID', 'UNIT_NBR']]))
cardata_women = pd.merge(unit_df, cars_with_women, on=['CRASH_ID', 'UNIT_NBR'], how='inner')
cars_without_women = unit_df[~unit_df['VIN'].isin(list(set(cardata_women['VIN'])))]['VEH_LIC_STATE_ID']
print(cars_without_women)
