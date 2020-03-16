from tqdm import tqdm
import pandas as pd
import requests
import glob
import time
import os

def save_result_page():
    id_list = set([patent_id.strip() for patent_id in open("id/id_A", 'r')])
    
    for id_number in tqdm(id_list):
        if os.path.exists("result_id_A/%s.html" % id_number) == True:
            continue

        result_url = "http://appft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p=1&u=%%2Fnetahtml%%2FPTO" \
                     "%%2Fsearch-bool.html&r=1&f=G&l=50&co1=AND&d=PG01&s1=%s&OS=%s&RS=%s" % (id_number, id_number, id_number)

        while True:
            try:
                result = requests.get(result_url, timeout=10)
                if judge_status(result.status_code, id_number) == True:
                    with open('result_id_A/%s.html' % id_number, 'w') as file:
                        file.write(result.text)
                time.sleep(5)
                break
            except requests.Timeout:
                    print("Timeout! id = %s" % id_number)
                    
            except requests.ConnectionError:
                    print("Connection Error! id = %s" % id_number)

        
def judge_status(status_code, params):
        if 400 <= status_code <= 499:
                print("Error Querying Format or Value: {}".format(params))
                return False
        elif status_code >= 500:
                print("Server error when querying {} ! Maybe exceeding the maximum API request size (1GB).".format(params))
                return False
        else:
                return True

def extract_data_from_page(filename, dataframe):
    # files = "result_id_A/4922925.html"
    pattern1_start = "<BR><CENTER><B>Abstract</B></CENTER>"
    pattern2_start = "<CENTER><B><I>Claims</B></I></CENTER>"
    pattern_end   = "<HR>"

    with open(filename, 'r') as f:
        content = [ line for line in f.readlines()]
        abstract = []
        claim = []

        i = 0 
        total_line = len(content)
        while i < total_line:
            if pattern1_start in content[i]:
                i += 1
                while pattern_end not in content[i]:
                    if "<P>" not in content[i] and "</P>" not in content[i]:
                        abstract.append(content[i])
                    i += 1

            if pattern2_start in content[i]:
                i += 2
                while pattern_end not in content[i]: 
                    claim.append(content[i])
                    i += 1
            i += 1
            
    abstract = ''.join(abstract)
    claim = ''.join(claim).replace("<BR>", "")

    basename = os.path.basename(filename)
    results = {
        "patent_id": str(os.path.splitext(basename)[0]),
        "abstract": abstract,
        "claim"   : claim
    }

    dataframe = dataframe.append(results, ignore_index=True)
    return dataframe

def parse_and_merge_data():
    files = [ i for i in glob.iglob("result_id_A/*.html")]
    data = pd.DataFrame(columns=["patent_id", "abstract", "claim"])
    
    for file in tqdm(files):
        data = extract_data_from_page(file, data)

    data["patent_id"] = data["patent_id"].astype(str)     
    data.to_csv("result/id_A.csv", index=False)


def seperate_abnormal_and_normal():
    data = pd.read_csv("result/id_A.csv", sep=",")
    data["patent_id"] = data["patent_id"].astype(str) 
    no_result = data[data.isnull().any(axis=1)]
    result = data[data.notnull().any(axis=1)]
    abnormal_id = list(no_result.patent_id)

    with open("abnormal_id.txt", 'w') as f:
        for number in abnormal_id:
            f.write("%s\n" % number) 

    result.to_csv("result/normal_id_A.csv", index=False)

if __name__ == "__main__":
    # save_result_page() # fetch all request which contained id
    # parse_and_merge_data() # parse and merge all html files

    seperate_abnormal_and_normal()# split normal and abnormal id
    