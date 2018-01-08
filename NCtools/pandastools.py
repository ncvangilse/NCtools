# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 10:42:00 2016

@author: fbx182
"""
import pandas as pd
import numpy as np

def resample(df, sr=0.1524, fill=None):
    """
    Resamples an input DataFrame to a specified sample rate
    Empty cells can be filled with the fill argument
    """
    #Calculate the index numbers (integers) where the current data relies
    s = (df.index // sr).astype(int)
    #and use that as a basis for how many samples should be output:
    new_index = np.arange(s.min(), s.max() + 1)
    #Save the original column order
    cols_org = df.columns.values
    #Aggregate numeric columns by taking the mean
    df_num = df.select_dtypes(include=[np.number]).groupby(s).mean()
    #Aggregate non-numeric columns by selecting the most popular one within each index
    df_non_num = df.select_dtypes(exclude=[np.number]).groupby(s).agg(lambda x: x.value_counts().index[0])
    #Recombine the numeric and non-numeric columns and reorder columns to original order
    grp = pd.concat([df_num, df_non_num], axis=1)[cols_org]
    #Save the NaN mask in the end of the dataframe to restore it after interpolation/fill
    grp_mask = grp.fillna(method='backfill').isnull()
    #Run different fill algorithms based on the 'fill' argument
    switcher = {
        'interpolate': grp.reindex(new_index).interpolate(),
        'ffill': grp.reindex(new_index).ffill(),
        'pad': grp.reindex(new_index).ffill()
    }
    grp = switcher.get(fill, grp.reindex(new_index))
    #Apply the NaN mask
    grp[grp_mask] = np.nan
    # Rename the index integers to actual floats
    grp.index = grp.index * sr
    return grp
    
def resample_like(df, otherindex, fill=None):
    """
    Resamples an input DataFrame to a specified sample rate
    Empty cells can be filled with the fill argument
    """
    #Calculate the index numbers (integers) where the current data relies
#    s = (df.index // sr).astype(int)
    s = np.digitize(df.index, otherindex)
        
    if len(set(s)) < len(s)/2:
        df = resample(df, sr=0.1, fill='interpolate')
        s = np.digitize(df.index, otherindex)
    #and use that as a basis for how many samples should be output:
#    new_index = np.arange(s.min(), s.max())
    new_index=np.arange(0, len(otherindex))
    #Save the original column order
    cols_org = df.columns.values
    #Aggregate numeric columns by taking the mean
    df_num = df.select_dtypes(include=[np.number]).groupby(s).mean()
    #Aggregate non-numeric columns by selecting the most popular one within each index
    df_non_num = df.select_dtypes(exclude=[np.number]).groupby(s).agg(lambda x: x.value_counts().index[0])
    #Recombine the numeric and non-numeric columns and reorder columns to original order
    grp = pd.concat([df_num, df_non_num], axis=1)[cols_org]
    #Save the NaN mask in the end of the dataframe to restore it after interpolation/fill
    grp_mask = grp.fillna(method='backfill').isnull()
    #Run different fill algorithms based on the 'fill' argument
    switcher = {
        'interpolate': grp.reindex(new_index).interpolate(),
        'ffill': grp.reindex(new_index).ffill(),
        'pad': grp.reindex(new_index).ffill()
    }
    grp = switcher.get(fill, grp.reindex(new_index))
    #Apply the NaN mask
    grp[grp_mask] = np.nan
    # Rename the index integers to actual floats
#    grp.index = grp.index * sr
    grp.set_index(otherindex[new_index], inplace=True)
    return grp.iloc[1:,:]

    
def drop_duplicate_columns(df, keep='last'):
    tmp = []
    drop = []
    if keep=='last':
        for i, col in reversed(list(enumerate(df.columns))):
#            print(col)
            if col in tmp:
                drop += [i]
            else:
                tmp += [col]
    else:
        for i, col in enumerate(df.columns):
            if col in tmp:
                drop += [i]
            else:
                tmp += [col]
#    print(drop)
#    print(cols)
#    print(df.columns)
    return df.iloc[:, [j for j, c in enumerate(df.columns) if j not in drop]]
    
if __name__ == '__main__':
    #TEST THE resample_like()
#    df_long = pd.DataFrame(np.array([np.arange(0,5,0.1),np.arange(0, 50, 1)]).T).set_index(0)
#    df_short = pd.DataFrame(np.array([np.arange(0,5,1.0),np.arange(0, 500, 100)]).T).set_index(0)
#    df = pd.DataFrame(np.array([np.arange(1,3,0.2),np.arange(1000, 3000, 200)]).T).set_index(0)
#    rs = resample_like(df, df_short, fill='interpolate')
##    rs= resample(df, sr=2)

    #TEST drop_duplicate_columns():
    df1 = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
    df2 = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('CDEF'))
    df3 = drop_duplicate_columns(pd.concat([df1, df2], axis=1), keep='first')

    