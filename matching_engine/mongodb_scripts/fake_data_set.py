# -*- coding: utf-8 -*-
"""
Created on Sat May  7 23:06:52 2022

@author: julien.nyambal

# https://towardsdatascience.com/how-i-built-my-own-dating-app-algorithm-2f6def15feb1
"""

import pandas as pd
import random
import faker
from datetime import date

fake = faker.Faker()
num = 1000

class ReechFakeData():
    def __init__(self):
        pass
    
    @staticmethod
    def calculate_age(born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    @staticmethod
    def cols_to_remove(single_profile):
        cols = ["ssn",'blood_group','username','website','job', 'company', 'residence', 'current_location','sex',
        'address', 'mail', 'birthdate']
        for col in cols:
            del single_profile[col]
        return single_profile
        
    def __call__(self):
        raw_data = []
        count=0
        while len(raw_data) < num:
            single_profile = fake.profile()
            age = self.calculate_age(single_profile["birthdate"])
            if (age >= 18 and age <= 50):
                count+=1
                single_profile["jobType"] = fake.job().lower()
                single_profile["empStatus"] = "employed"
                single_profile["surname"] = single_profile["name"].split(' ')[-1]
                single_profile["name"] = single_profile["name"].split(' ')[-2]
                single_profile["location"] =single_profile["residence"] 
                single_profile["email"] =single_profile["mail"] 
                single_profile["userId"] = count 
                single_profile["profileId"]=count
                single_profile = self.cols_to_remove(single_profile)
                raw_data.append(single_profile)
                
        # data = pd.DataFrame(raw_data)
        return raw_data


