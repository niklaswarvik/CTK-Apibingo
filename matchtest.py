from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_best_match(article_dict, key):
    best_keys = []
    for k in article_dict.keys():
        m_r = fuzz.ratio(k,key)
        if m_r > 70:
            best_keys += [k]
    return best_keys
                    
            
def main():
    key = "Pripps Blå"
    dict_test = {"Pripps Blå": [1,2,3,4], "Prip Blå": [1,2,3,4], "Heja": [12,3]}
    print(get_best_match(dict_test,key))

main()
    
