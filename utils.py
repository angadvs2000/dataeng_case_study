import yaml
import pandas as pd
import zipfile

class GetData:
    '''
    Gets and stores all the data from Data.zip and the config file
    '''

    def __init__(self):
        with open('config/config.yaml', 'r') as f:
            data = yaml.safe_load(f)
        
        self.data = data
        self.zf = zipfile.ZipFile('Data.zip')


    def charges(self):
        '''
        Gets Charges csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Charges data
        '''

        charges_df = pd.read_csv(self.zf.open(self.data['paths']['charges']))
        return charges_df
    

    def damages(self):
        '''
        Gets Damages csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Damages data
        '''

        damages_df = pd.read_csv(self.zf.open(self.data['paths']['damages']))
        return damages_df
    

    def endorse(self):
        '''
        Gets Endorsements csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Endorsements data
        '''

        endorse_df = pd.read_csv(self.zf.open(self.data['paths']['endorse']))
        return endorse_df
    

    def primary(self):
        '''
        Gets Primary Person csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Primary Person data
        '''

        primary_df = pd.read_csv(self.zf.open(self.data['paths']['primary_person']))
        return primary_df
    

    def restrict(self):
        '''
        Gets Restrict csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Restrict data
        '''

        restrict_df = pd.read_csv(self.zf.open(self.data['paths']['restrict']))
        return restrict_df
    

    def units(self):
        '''
        Gets Unit csv data from data.zip and converts it to dataframe format

        Returns:
            pandas.DataFrame: DataFrame containg Unit data
        '''

        units_df = pd.read_csv(self.zf.open(self.data['paths']['units']), low_memory=False)
        return units_df
