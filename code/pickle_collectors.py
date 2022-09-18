import pandas as pd
import pickle
import re

# In case we ever want to update the list of collector surnames to search for
dfs = {
    'russian': pd.read_csv('.txt', dtype='str', error_bad_lines=False, sep='\t', usecols=['recordedBy']),  # e.g. occurrence.txt from https://depo.msu.ru/ipt/archive.do?r=plants
    'tajik': pd.read_csv('.txt', dtype='str', error_bad_lines=False, sep='\t', usecols=['recordedBy'])  # e.g. BRAHMS dataset export from TNAS
}
for country, df in dfs.items():
    colls = df['recordedBy'].unique()
    colls = colls[colls==colls] # remove nans
    flat = []
    for c in colls: flat.extend(c.split(' | '))
    flat = set(flat)
    # proper = [x for x in flat if re.search('^[A-Za-z]+', x) is not None]
    surnames = [re.search('[A-Z][A-Za-z]{3,}', f).group() for f in flat if re.search('[A-Z][A-Za-z]{3,}', f) is not None]

    pickle.dump(surnames, open(f'/srv/code/{country}-collectors.pkl', 'wb'))