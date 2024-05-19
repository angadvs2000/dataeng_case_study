import pandas as pd
import utils



class CrashAnalytics:
    '''
    Answers all mentioned questions
    '''

    def __init__(self):
        self.data = utils.GetData()
        self.primary_df = self.data.primary()
        self.unit_df = self.data.units()
        self.charge_df = self.data.charges()
        self.damage_df = self.data.damages()
        self.config = self.data.data

        # Pre-calculated values that are used multiple times in the below code
        self.car_unit_df = self.unit_df[self.unit_df['VEH_BODY_STYL_ID'].isin(self.config['car_body_styles'])]
        self.valid_lic_driver_df = self.primary_df[self.primary_df['DRVR_LIC_TYPE_ID'].isin(['COMMERCIAL DRIVER LIC.', 'DRIVER LICENSE']) &
                                              (self.primary_df['PRSN_TYPE_ID'] == 'DRIVER')][['CRASH_ID', 'UNIT_NBR']]


    def crashes_with_more_than_2_males_killed(self):
        '''
        Finds the number of crashes (accidents) in which number of males killed are greater than 2

        Returns:
            int: count of crashes
        '''

        crashes_with_male_deaths = self.primary_df[(self.primary_df['DEATH_CNT'] == 1) & 
                                (self.primary_df['PRSN_GNDR_ID'] == 'MALE')][['CRASH_ID','DEATH_CNT']].groupby('CRASH_ID').sum()
        male_fatal_crashes_count = crashes_with_male_deaths[crashes_with_male_deaths['DEATH_CNT'] > 2]
        return len(male_fatal_crashes_count)
    

    def two_wheelers_booked_count(self):
        '''
        Finds count of two wheelers booked for crashes

        Returns:
            int: count of distinct two wheelers
        '''

        twowheelers_df = self.unit_df[(self.unit_df['VEH_BODY_STYL_ID'] == 'MOTORCYCLE') | 
                                    (self.unit_df['VEH_BODY_STYL_ID'] == 'POLICE MOTORCYCLE')]
        merged_df = pd.merge(twowheelers_df[['CRASH_ID', 'UNIT_NBR', 'VIN']], 
                             self.charge_df[['CRASH_ID', 'UNIT_NBR']], on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        return len(set(merged_df['VIN']))
    

    def top_car_makes_with_fatal_crashes_and_no_airbag(self):
        '''
        Finds the top 5 Vehicle Makes of the cars present in the crashes in which driver died and
        Airbags did not deploy

        Assumptions: - When choosing to do analysis on 'cars', the following values from 'VEH_BODY_STYL_ID' in Unit 
                table were chosen: 'PASSENGER CAR, 2-DOOR','PASSENGER CAR, 4-DOOR', 'POLICE CAR/TRUCK', 'SPORT 
                UTILITY VEHICLE'
                - When choosing data where 'Airbags did not deploy', the following values from 'PRSN_AIRBAG_ID' in 
                primary_person table were chosen: 'NOT DEPLOYED','DEPLOYED, SIDE', 'DEPLOYED, REAR'

        Returns:
            list: top 5 car makes
        '''
        vehicle_unit_df = self.car_unit_df[['CRASH_ID', 'UNIT_NBR', 'VEH_MAKE_ID']]
        filtered_person_df = self.primary_df[(self.primary_df['PRSN_AIRBAG_ID'].isin(self.config['no_airbag'])) & 
                                             (self.primary_df['PRSN_TYPE_ID'] == 'DRIVER') & 
                                             (self.primary_df['DEATH_CNT'] == 1)][['CRASH_ID', 'UNIT_NBR']]
        merged_df = pd.merge(vehicle_unit_df, filtered_person_df, on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        top_veh_makes_in_merged_df = list(merged_df[['VEH_MAKE_ID']].groupby(
            'VEH_MAKE_ID').size().sort_values(ascending=False).reset_index()['VEH_MAKE_ID'][:5])
        return top_veh_makes_in_merged_df
    
    
    def veh_with_valid_lic_driver_and_hnr(self):
        '''
        Determines number of Vehicles with driver having valid licences involved in hit and run

        Assumption: - For choosing drivers with 'valid licences', the following values from 'DRVR_LIC_TYPE_ID' 
                    in primary_person table were chosen: 'COMMERCIAL DRIVER LIC.', 'DRIVER LICENSE'
        
        Returns:
            int: count of distinct Vehicles
        '''

        hit_and_run_df = self.unit_df[self.unit_df['VEH_HNR_FL']=='Y'][['CRASH_ID', 'UNIT_NBR','VIN']]
        merged_df = pd.merge(self.valid_lic_driver_df, hit_and_run_df, on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        return len(set(merged_df['VIN']))
    
    
    def state_with_highest_acccidents_without_females(self):
        '''
        Finds the state with the highest number of accidents in which females are not involved

        Assumption: - For choosing 'states' with higest number of accidents where females are not involved, column 
                    'DRVR_LIC_STATE_ID' from primary_person table is used to get the state name

        Returns:
            str: name of state with most vehicle crashes
        '''

        merge_vin_with_primary = self.primary_df.merge(self.unit_df[['CRASH_ID', 'UNIT_NBR', 'VIN']], 
                                                       on=['CRASH_ID', 'UNIT_NBR'], how='left')
        crashes_with_women = list(set(merge_vin_with_primary[merge_vin_with_primary['PRSN_GNDR_ID'] == 'FEMALE']['CRASH_ID']))
        crashes_without_women = merge_vin_with_primary[~merge_vin_with_primary['CRASH_ID'].isin(crashes_with_women)][['CRASH_ID',
                                                    'DRVR_LIC_STATE_ID']].drop_duplicates(subset=['CRASH_ID'], keep='first')
        state_with_highest_crashes = crashes_without_women[['DRVR_LIC_STATE_ID']].groupby(
            'DRVR_LIC_STATE_ID').size().sort_values(ascending=False).reset_index()['DRVR_LIC_STATE_ID'][0]
        return state_with_highest_crashes


    def top_3rdto5th_veh_makes_with_largest_total_injuries_incl_death(self):
        '''
        Finds the Top 3rd to 5th VEH_MAKE_IDs that contribute to the largest number of injuries including death
        
        Returns:
            list: list of top 3rd to 5th vehicle makes
        '''

        self.unit_df['total_injuries'] = self.unit_df['TOT_INJRY_CNT'] + self.unit_df['DEATH_CNT']
        groupby_vehicle = self.unit_df[['VEH_MAKE_ID','total_injuries']].groupby(
            'VEH_MAKE_ID').sum().sort_values(by='total_injuries', ascending=False).reset_index()
        top_vehicles = list(groupby_vehicle['VEH_MAKE_ID'][2:5])
        return top_vehicles
    

    def top_ethnicity_of_each_body_style(self):
        '''
        For all the body styles involved in crashes, this finds the top ethnic user group of each unique body style

        Returns:
            pandas.DataFrame: DataFrame with vehicle body style and the top ethnic group as the columns
        '''
        
        merge_ethnicity = self.unit_df.merge(self.primary_df[['CRASH_ID', 'UNIT_NBR', 'PRSN_ETHNICITY_ID']], 
                                             on=['CRASH_ID', 'UNIT_NBR'], how='left')
        groupby_bodystyle_ethnicity = merge_ethnicity.groupby(['VEH_BODY_STYL_ID', 
                                                               'PRSN_ETHNICITY_ID']).size().reset_index().rename(columns={0:'count'})
        get_maxcount_ethnicity = groupby_bodystyle_ethnicity[groupby_bodystyle_ethnicity.groupby(
            'VEH_BODY_STYL_ID')['count'].transform('max') == groupby_bodystyle_ethnicity['count']]
        return get_maxcount_ethnicity.reset_index()[['VEH_BODY_STYL_ID', 
                                       'PRSN_ETHNICITY_ID']].rename(columns={'PRSN_ETHNICITY_ID': 'TOP_ETHNICITY'})
    

    def top_5_zipcodes_with_alc_as_contrib_factr(self):
        '''
        Among the crashed cars, this finds the Top 5 Zip Codes with highest number of crashes with alcohols 
        as the contributing factor to a crash (using Driver Zip Code)
        
        Assumption: - For choosing 'crashes with alcohols as the contributing factor', the following values from 
                'CONTRIB_FACTR_P1_ID' in Unit table were chosen: 'HAD BEEN DRINKING','UNDER INFLUENCE - ALCOHOL'
        
        Returns:
            list: top 5 zipcodes
        '''
        
        alcohol_car_crashes = self.car_unit_df[self.car_unit_df['CONTRIB_FACTR_P1_ID'].isin(
            self.config['alcohol_contrib_factr'])][['CRASH_ID', 'UNIT_NBR']]
        add_zip_data = alcohol_car_crashes.merge(self.primary_df[['CRASH_ID', 'UNIT_NBR', 'DRVR_ZIP']], 
                                                 on=['CRASH_ID', 'UNIT_NBR'], how='left')
        groupby_zip = add_zip_data.groupby('DRVR_ZIP').size()
        top_5_zipcodes = list(groupby_zip.sort_values(ascending=False).reset_index()['DRVR_ZIP'][:5])
        return top_5_zipcodes
    
    
    def crashes_with_damaged_prop_and_damage_level_above_4_with_insured_car(self):
        '''
        Finds count of Distinct Crash IDs where No Damaged Property was observed and Damage Level (VEH_DMAG_SCL~) is 
        above 4 and car avails Insurance

        Assumptions: - For choosing data where 'Damage Level (VEH_DMAG_SCL~) is above 4', Unit data is filtered based on if either 
                column 'VEH_DMAG_SCL_1_ID' or column 'VEH_DMAG_SCL_2_ID' contained any of the following values: 'DAMAGED 5',
                'DAMAGED 6','DAMAGED 7 HIGHEST'
                - For choosing data where 'car avails insurance', the following values from 'FIN_RESP_TYPE_ID' were 
                chosen: 'PROOF OF LIABILITY INSURANCE', 'LIABILITY INSURANCE POLICY'

        Returns:
            int: number of distinct vehicles
        '''
        
        filter_data_damage = self.car_unit_df[(self.car_unit_df['VEH_DMAG_SCL_1_ID'].isin(self.config['damage_more_than_four']))|
                             (self.car_unit_df['VEH_DMAG_SCL_2_ID'].isin(self.config['damage_more_than_four']))]
        crashes_with_prop_damage = list(set(self.damage_df[self.damage_df['DAMAGED_PROPERTY'].notna()]['CRASH_ID']))
        combined_data = filter_data_damage[~filter_data_damage['CRASH_ID'].isin(crashes_with_prop_damage)]
        data_with_insurance = combined_data[combined_data['FIN_RESP_TYPE_ID'].isin(self.config['car_insurance'])]
        return len(set(data_with_insurance['CRASH_ID']))
    

    def top_veh_makes_in_speeding_accidents(self):
        '''
        Determines the Top 5 Vehicle Makes where drivers are charged with speeding related offences, has licensed 
        Drivers, used top 10 used vehicle colours and has car licensed with the Top 25 states with highest number 
        of offences

        Assumptions: - When choosing 'cars' that are licenced, the following values from 'VEH_BODY_STYL_ID' were
                chosen: 'PASSENGER CAR, 2-DOOR','PASSENGER CAR, 4-DOOR', 'POLICE CAR/TRUCK', 'SPORT UTILITY VEHICLE'
                - Whn filtering based on 'speeding related offences', those values from Charges data were taken where
                'CHARGE' column contains the string 'SPEED'
                - To deduce the states with highest number of offences, VEH_LIC_STATE_ID column from 
                Unit table is used to determine it

        Returns:
            list: top 5 vehicle makes
        '''
        
        speeding_charge = self.charge_df[(self.charge_df['CHARGE'].notna())&
                                         (self.charge_df['CHARGE'].str.contains('SPEED'))][['CRASH_ID', 'UNIT_NBR']]
        speeding_on_validlic_driver = self.valid_lic_driver_df.merge(speeding_charge,  on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        car_speeding_on_validlic_driver = pd.merge(self.car_unit_df, speeding_on_validlic_driver[['CRASH_ID', 'UNIT_NBR']], 
                                                on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        top_veh_colours = list(self.unit_df[['VEH_COLOR_ID']].groupby(
            'VEH_COLOR_ID').size().sort_values(ascending=False).reset_index()['VEH_COLOR_ID'][:10])
        states_with_offenses = pd.merge(self.unit_df[['CRASH_ID', 'UNIT_NBR', 'VEH_LIC_STATE_ID']], 
                                        self.charge_df[['CRASH_ID', 'UNIT_NBR']], on=['CRASH_ID', 'UNIT_NBR'], how='inner')
        top_states_with_offenses = list(states_with_offenses.groupby(
            'VEH_LIC_STATE_ID').size().sort_values(ascending=False).reset_index()['VEH_LIC_STATE_ID'][:25])
        combined_data = car_speeding_on_validlic_driver[(car_speeding_on_validlic_driver['VEH_COLOR_ID'].isin(top_veh_colours))&
                                                    (car_speeding_on_validlic_driver['VEH_LIC_STATE_ID'].isin(top_states_with_offenses))]
        top_veh_makes = list(combined_data[['VEH_MAKE_ID']].groupby(
            'VEH_MAKE_ID').size().sort_values(ascending=False).reset_index()['VEH_MAKE_ID'][:5])
        return top_veh_makes
