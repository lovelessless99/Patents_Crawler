import pandas as pd


def extract_id_from_csv(filename):
    df = pd.read_csv(filename, sep=",", engine='python')
    patent_id = df['PublicationNumber'].tolist()
    extract_id_A, extract_id_B, extract_id_S, extract_id_H, extract_id_E = [], [], [], [], []    

    for patent in patent_id:
        pattern = patent[-2:]

        if "A" in pattern:
            index = patent.find("A")
            extract_id_A.append(patent[2:index])
        
        elif "B" in pattern:
            index = patent.find("B")
            extract_id_B.append(patent[2:index])

        elif "H" in pattern:
            index = patent.find("H")
            extract_id_H.append(patent[2:-2])
            
        elif "E" in pattern:
            index = patent.find("E")
            extract_id_E.append(patent[2:-2])
            
        elif "S" in pattern:
            index = patent.find("S")
            extract_id_S.append(patent[2:-2])
            
    output_file("id/id_A"     , extract_id_A)
    output_file("id/id_B"     , extract_id_B)
    output_file("id/id_S"     , extract_id_S)
    output_file("id/id_H"     , extract_id_H)
    output_file("id/id_E"     , extract_id_E)

def output_file(filename, id_list):
    with open(filename, 'w') as f:
        for number in id_list:
            f.write("%s\n" % number) 


if __name__ == "__main__":
    csv_file = "abs_patent.csv"
    extract_id_from_csv(csv_file)


