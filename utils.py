import yaml
import pandas as pd
import zipfile

class get_data:
    '''get and store all the data from Data.zip'''

    def __init__(self):
        with open('config/config.yaml', 'r') as f:
            data = yaml.safe_load(f)
        
        self.data = data
        self.zf = zipfile.ZipFile('Data.zip')

    def charges(self):
        charges_df = pd.read_csv(self.zf.open(self.data['paths']['charges']))
        return charges_df

    def damages(self):
        damages_df = pd.read_csv(self.zf.open(self.data['paths']['damages']))
        return damages_df
    
    def endorse(self):
        endorse_df = pd.read_csv(self.zf.open(self.data['paths']['endorse']))
        return endorse_df
    
    def primary(self):
        primary_df = pd.read_csv(self.zf.open(self.data['paths']['primary_person']))
        return primary_df
    
    def restrict(self):
        restrict_df = pd.read_csv(self.zf.open(self.data['paths']['restrict']))
        return restrict_df
    
    def units(self):
        units_df = pd.read_csv(self.zf.open(self.data['paths']['units']), low_memory=False)
        return units_df