#
# WalletKit Rest Client
#


import traceback
import urllib2
import httplib
import urllib
import simplejson
import requests

url = 'https://api.walletkit.com/v1/passes'

"""WalletKit REST client

Author: Walletkit <support@walletkit.com>
Version: 1.0

"""
class Walletkit:
    def __init__(self,apikey,brandid):
        """
        Initialize REST client with provided credentials

        apikey: The API key
        brandid: The Brand Id
        
        """
        self.apikey = apikey
        self.brandid = brandid
        self.h = {"Brand-Id": self.brandid,"API-Key": self.apikey,"Content-Type":"application/json"}

    def create_pass_template(self,template_data):
        """Return json response containing id of template created

        Create a new pass template

        template_data: The template json data as a dictionary

        """
        try:

            data = simplejson.dumps(template_data)
            response = requests.post(url,data,headers=self.h,verify = False)
            response_json= response.json()
            template_id = response_json['id']
            return template_id
        except Exception:
            return response.json()

    def show_pass_template_list(self):
        """Return json response containing list of pass templates created

        Display all pass templates created

        """
        try:
            response = requests.get(url,headers=self.h,verify=False)
            return response.json()
        except Exception:
            return response.json()
        
        
    def show_pass_template_info(self,template_id):
        """Return json response containing all information about the pass template

        Display all information about an existing pass template

        """
        try:
            response = requests.get(url+'/'+str(template_id),headers=self.h,verify =False)
            return response.json()
        except Exception:
            return response.json()

    def create_pass(self,pass_data,template_id):
        """Return json response containing details of pass created

        Create a new pass

        pass_data: The pass json data as a dictionary

        """
        try:
            data = simplejson.dumps(pass_data)
            response = requests.post(url+'/'+str(template_id),data,headers=self.h,verify = False)
            return response.json()
        except Exception:
            return response.json()
        
    def update_pass(self,update_data,template_id):
        """Return json response containing details of pass updated

        Update an existing pass

        update_data: The pass data to be updated, as a dictionary

        """
        try:
            data = simplejson.dumps(update_data)
            response = requests.put(url+'/'+str(template_id),headers=self.h,verify =False)
            return response.json()
        except Exception:
            return response.json()
        

    def delete_pass_template(self,template_id):
        """Delete an existing pass template"""
        try:
            response = requests.delete(url+'/'+str(template_id),headers=self.h,verify =False)
            return response.json()
        except Exception:
            return response.json()
       
