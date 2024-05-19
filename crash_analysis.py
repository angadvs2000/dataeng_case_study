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
        self.columns = self.config['columns']

        # Pre-calculated values that are used multiple times in the below code
        self.car_unit_df = self.unit_df[self.unit_df[self.columns['veh_body_styl']].isin(self.config['car_body_styles'])]
        self.valid_lic_driver_df = self.primary_df[self.primary_df[self.columns['drvr_lic_type']].isin(self.config['drvr_lic']) & 
                                (self.primary_df[self.columns['prsn_type']] == 'DRIVER')][self.config['crash_id_and_unit_nbr']]


    def crashes_with_more_than_2_males_killed(self):
        '''
        Finds the number of crashes (accidents) in which number of males killed are greater than 2

        Returns:
            int: count of crashes
        '''

        crashes_with_male_deaths = self.primary_df[(self.primary_df[self.columns['death_cnt']] == 1) & 
                                (self.primary_df[self.columns['prsn_gndr']] == 
                                 'MALE')][[self.columns['crash_id'],self.columns['death_cnt']]].groupby(self.columns['crash_id']).sum()
        male_fatal_crashes_count = crashes_with_male_deaths[crashes_with_male_deaths[self.columns['death_cnt']] > 2]
        return len(male_fatal_crashes_count)
    

    def two_wheelers_booked_count(self):
        '''
        Finds count of two wheelers booked for crashes

        Returns:
            int: count of distinct two wheelers
        '''

        twowheelers_df = self.unit_df[(self.unit_df[self.columns['veh_body_styl']] == 'MOTORCYCLE') | 
                                    (self.unit_df[self.columns['veh_body_styl']] == 'POLICE MOTORCYCLE')]
        merged_df = pd.merge(twowheelers_df[[self.columns['crash_id'], self.columns['unit_nbr'], self.columns['vin']]], 
                             self.charge_df[self.config['crash_id_and_unit_nbr']], 
                             on=self.config['crash_id_and_unit_nbr'], how='inner')
        return len(set(merged_df[self.columns['vin']]))
    

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
        vehicle_unit_df = self.car_unit_df[[self.columns['crash_id'], self.columns['unit_nbr'], self.columns['veh_make']]]
        filtered_person_df = self.primary_df[(self.primary_df[self.columns['prsn_airbag']].isin(self.config['no_airbag'])) & 
                                             (self.primary_df[self.columns['prsn_type']] == 'DRIVER') & 
                                             (self.primary_df[self.columns['death_cnt']] == 1)][self.config['crash_id_and_unit_nbr']]
        merged_df = pd.merge(vehicle_unit_df, filtered_person_df, on=self.config['crash_id_and_unit_nbr'], how='inner')
        top_veh_makes_in_merged_df = list(merged_df[[self.columns['veh_make']]].groupby(
            self.columns['veh_make']).size().sort_values(ascending=False).reset_index()[self.columns['veh_make']][:5])
        return top_veh_makes_in_merged_df
    
    
    def veh_with_valid_lic_driver_and_hnr(self):
        '''
        Determines number of Vehicles with driver having valid licences involved in hit and run

        Assumption: - For choosing drivers with 'valid licences', the following values from 'DRVR_LIC_TYPE_ID' 
                    in primary_person table were chosen: 'COMMERCIAL DRIVER LIC.', 'DRIVER LICENSE'
        
        Returns:
            int: count of distinct Vehicles
        '''

        hit_and_run_df = self.unit_df[self.unit_df[self.columns['veh_hnr']]=='Y'][[self.columns['crash_id'], 
                                                                                   self.columns['unit_nbr'],self.columns['vin']]]
        merged_df = pd.merge(self.valid_lic_driver_df, hit_and_run_df, on=self.config['crash_id_and_unit_nbr'], how='inner')
        return len(set(merged_df[self.columns['vin']]))
    
    
    def state_with_highest_acccidents_without_females(self):
        '''
        Finds the state with the highest number of accidents in which females are not involved

        Assumption: - For choosing 'states' with higest number of accidents where females are not involved, column 
                    'DRVR_LIC_STATE_ID' from primary_person table is used to get the state name

        Returns:
            str: name of state with most vehicle crashes
        '''

        merge_vin_with_primary = self.primary_df.merge(self.unit_df[[self.columns['crash_id'],
                            self.columns['unit_nbr'], self.columns['vin']]], on=self.config['crash_id_and_unit_nbr'], how='left')
        crashes_with_women = list(set(merge_vin_with_primary[merge_vin_with_primary[self.columns['prsn_gndr']] == 
                                                             'FEMALE'][self.columns['crash_id']]))
        crashes_without_women = merge_vin_with_primary[~merge_vin_with_primary[self.columns['crash_id']].isin(
                                crashes_with_women)][[self.columns['crash_id'], 
                                self.columns['drvr_lic_state']]].drop_duplicates(subset=[self.columns['crash_id']], keep='first')
        state_with_highest_crashes = crashes_without_women[[self.columns['drvr_lic_state']]].groupby(
            self.columns['drvr_lic_state']).size().sort_values(ascending=False).reset_index()[self.columns['drvr_lic_state']][0]
        return state_with_highest_crashes


    def top_3rdto5th_veh_makes_with_largest_total_injuries_incl_death(self):
        '''
        Finds the Top 3rd to 5th VEH_MAKE_IDs that contribute to the largest number of injuries including death
        
        Returns:
            list: list of top 3rd to 5th vehicle makes
        '''

        self.unit_df['total_injuries'] = self.unit_df[self.columns['tot_injry_cnt']] + self.unit_df[self.columns['death_cnt']]
        groupby_vehicle = self.unit_df[[self.columns['veh_make'],'total_injuries']].groupby(
            self.columns['veh_make']).sum().sort_values(by='total_injuries', ascending=False).reset_index()
        top_vehicles = list(groupby_vehicle[self.columns['veh_make']][2:5])
        return top_vehicles
    

    def top_ethnicity_of_each_body_style(self):
        '''
        For all the body styles involved in crashes, this finds the top ethnic user group of each unique body style

        Returns:
            pandas.DataFrame: DataFrame with vehicle body style and the top ethnic group as the columns
        '''
        
        merge_ethnicity = self.unit_df.merge(self.primary_df[[self.columns['crash_id'], self.columns['unit_nbr'], 
                                            self.columns['prsn_ethnicity']]], on=self.config['crash_id_and_unit_nbr'], how='left')
        groupby_bodystyle_ethnicity = merge_ethnicity.groupby([self.columns['veh_body_styl'], 
                                        self.columns['prsn_ethnicity']]).size().reset_index().rename(columns={0:'count'})
        get_maxcount_ethnicity = groupby_bodystyle_ethnicity[groupby_bodystyle_ethnicity.groupby(
            self.columns['veh_body_styl'])['count'].transform('max') == groupby_bodystyle_ethnicity['count']]
        return get_maxcount_ethnicity.reset_index()[[self.columns['veh_body_styl'], 
                                       self.columns['prsn_ethnicity']]].rename(columns={self.columns['prsn_ethnicity']: 'TOP_ETHNICITY'})
    

    def top_5_zipcodes_with_alc_as_contrib_factr(self):
        '''
        Among the crashed cars, this finds the Top 5 Zip Codes with highest number of crashes with alcohols 
        as the contributing factor to a crash (using Driver Zip Code)
        
        Assumption: - For choosing 'crashes with alcohols as the contributing factor', the following values from 
                'CONTRIB_FACTR_P1_ID' in Unit table were chosen: 'HAD BEEN DRINKING','UNDER INFLUENCE - ALCOHOL'
        
        Returns:
            list: top 5 zipcodes
        '''
        
        alcohol_car_crashes = self.car_unit_df[self.car_unit_df[self.columns['contrib_factr_p1']].isin(
            self.config['alcohol_contrib_factr'])][self.config['crash_id_and_unit_nbr']]
        add_zip_data = alcohol_car_crashes.merge(self.primary_df[[self.columns['crash_id'], 
                                                self.columns['unit_nbr'], self.columns['drvr_zip']]], 
                                                on=self.config['crash_id_and_unit_nbr'], how='left')
        groupby_zip = add_zip_data.groupby(self.columns['drvr_zip']).size()
        top_5_zipcodes = list(groupby_zip.sort_values(ascending=False).reset_index()[self.columns['drvr_zip']][:5])
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
        
        filter_data_damage = self.car_unit_df[(self.car_unit_df[self.columns[
                            'veh_dmag_scl_1']].isin(self.config['damage_more_than_four']))|
                             (self.car_unit_df[self.columns['veh_dmag_scl_2']].isin(self.config['damage_more_than_four']))]
        crashes_with_prop_damage = list(set(self.damage_df[self.damage_df[self.columns['damaged_property']].notna()][self.columns['crash_id']]))
        combined_data = filter_data_damage[~filter_data_damage[self.columns['crash_id']].isin(crashes_with_prop_damage)]
        data_with_insurance = combined_data[combined_data[self.columns['fin_resp_type']].isin(self.config['car_insurance'])]
        return len(set(data_with_insurance[self.columns['crash_id']]))
    

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
        
        speeding_charge = self.charge_df[(self.charge_df[self.columns['charge']].notna())&
                                         (self.charge_df[self.columns['charge']].str.contains('SPEED'))][
                                             self.config['crash_id_and_unit_nbr']]
        speeding_on_validlic_driver = self.valid_lic_driver_df.merge(speeding_charge,  
                                                                     on=self.config['crash_id_and_unit_nbr'], how='inner')
        car_speeding_on_validlic_driver = pd.merge(self.car_unit_df, 
                                                speeding_on_validlic_driver[self.config['crash_id_and_unit_nbr']], 
                                                on=self.config['crash_id_and_unit_nbr'], how='inner')
        top_veh_colours = list(self.unit_df[[self.columns['veh_color']]].groupby(
            self.columns['veh_color']).size().sort_values(ascending=False).reset_index()[self.columns['veh_color']][:10])
        states_with_offenses = pd.merge(self.unit_df[[self.columns['crash_id'], self.columns['unit_nbr'], self.columns['veh_lic_state']]], 
                                        self.charge_df[self.config['crash_id_and_unit_nbr']], 
                                        on=self.config['crash_id_and_unit_nbr'], how='inner')
        top_states_with_offenses = list(states_with_offenses.groupby(
            self.columns['veh_lic_state']).size().sort_values(ascending=False).reset_index()[self.columns['veh_lic_state']][:25])
        combined_data = car_speeding_on_validlic_driver[(car_speeding_on_validlic_driver[self.columns['veh_color']].isin(top_veh_colours))&
                                            (car_speeding_on_validlic_driver[self.columns['veh_lic_state']].isin(top_states_with_offenses))]
        top_veh_makes = list(combined_data[[self.columns['veh_make']]].groupby(
            self.columns['veh_make']).size().sort_values(ascending=False).reset_index()[self.columns['veh_make']][:5])
        return top_veh_makes
