from pandas.io.json import json_normalize
from configparser import ConfigParser
from tqdm import tqdm
import pandas as pd
import configparser
import requests
import json
import glob
import os

def setting_to_json(configfile):
        setting = ConfigParser()
        setting.read(configfile)
        
        # parse parameters
        output_dir = setting.get("default", "output_directory")
        input_file = setting.get("default", "input_file")
        input_type = setting.get("setting", "input_type")
        endpoint   = setting.get("setting", "endpoint"  )
        field      = setting.get("setting", "fields"    )
        field      = json.loads(field)       
        date_range, sort = parse_optional(setting)

        id_list = set([patent_id.strip() for patent_id in open(input_file, 'r')])       
        result_list = []

        for i in tqdm(id_list):
                params = {
                        "q": {"_and": [{input_type: i}, date_range] },
                        "f": field,
                        "o": {"per_page": 100 },
                }
                if sort is not None:
                        params['s'] = sort

                url = "https://www.patentsview.org/api/%s/query?" % endpoint
                # result = requests.post(url, json.dumps(params), timeout=10) # single quote to double quote
                # if judge_status(result.status_code, params) == True:
                #         if json.loads(result.text)["count"] > 0:
                #                 result_list.append(json.loads(result.text))

                while True:
                        url = "https://www.patentsview.org/api/%s/query?" % endpoint
                        try:
                                result = requests.post(url, data=json.dumps(params), timeout=5)
                                if judge_status(result.status_code, params) == True:
                                        if json.loads(result.text)["count"] > 0:
                                                result_list.append(json.loads(result.text))
                                break
                        except requests.Timeout:
                                print("Timeout! id = %s" % i)
                                
                        except requests.ConnectionError:
                                print("Connection Error! id = %s" % i)
                


        output_params = {
                "output_directory": output_dir,
                "endpoint"  : endpoint,
                "sort"      : sort
        }
        convert_results_to_csv(result_list, **output_params)


def parse_optional(configparser):
        date_range, sort = None, None
        if "filter" in configparser:
                options = configparser["filter"].keys()

                if "date_range" in options:
                        date = configparser.get("filter", "date_range")
                        date = json.loads(date) # string to list
                        date_range = {
                               "_and": [ {"_gte":{"patent_date": date[0]}}, {"_lte":{"patent_date": date[1]}} ]
                        }

                if "sort" in options:
                        sort = configparser.get("filter", "sort")
                        sort = json.loads(sort)

        return date_range, sort

def judge_status(status_code, params):
        if 400 <= status_code <= 499:
                print("Error Querying Format or Value: {}".format(params))
                return False
        elif status_code >= 500:
                print("Server error when querying {} ! Maybe exceeding the maximum API request size (1GB).".format(params))
                return False
        else:
                return True

def init_directory(directory):
        if directory != "." and not os.path.exists(directory):
                os.makedirs(directory)

def convert_results_to_csv(results_list, endpoint="patents", output_directory=".", sort=None):
        all_json = []
        for result in results_list:
                for i in result["patents"]:
                     all_json.append(i)
  
        data = json_normalize(all_json)
        
        if sort is not None:
                sort_column = [ key for item in sort for key in item.keys() ]
                sort_order  = [ True if value == "asc" else False for item in sort for value in item.values() ]
                data = data.sort_values(sort_column, ascending = sort_order)
        
        init_directory(output_directory)
        data.to_csv("%s/%s.csv" % (output_directory, endpoint))



if __name__ == "__main__":
        configfile = "configure/patent.cfg"
        setting_to_json(configfile)
        



