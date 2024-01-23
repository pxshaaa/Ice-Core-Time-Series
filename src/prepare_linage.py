# Teddy Tonin


from cmath import nan
import numpy as np

def get_data_ready_for_linage(data_array, abs1, ord1, abs2, ord2):
    '''This function deals with Nan values inside the columns selected for the linage'''

    if abs1 is None or abs2 is  None: 
        return None,None,None, None

    x_ref = data_array[abs1].to_numpy()
    x_dis = data_array[abs2].to_numpy()
    y_ref = data_array[ord1].to_numpy()
    y_dis = data_array[ord2].to_numpy()
    x_ref = x_ref[~np.isnan(x_ref)]
    x_dis = x_dis[~np.isnan(x_dis)]
    y_ref = y_ref[~np.isnan(y_ref)]
    y_dis = y_dis[~np.isnan(y_dis)]
    len_ref = np.min([len(x_ref), len(y_ref)])
    len_dis = np.min([len(x_dis), len(y_dis)])
    x_ref = x_ref[:len_ref]
    y_ref = y_ref[:len_ref]
    x_dis = x_dis[:len_dis]
    y_dis = y_dis[:len_dis]

    return x_ref, y_ref, x_dis, y_dis


def sort_with_indices(arr):
    # Create an array of tuples (element, index)
    indexed_arr = [(element, index) for index, element in enumerate(arr)]
    
    # Sort the array of tuples based on the elements
    sorted_arr = sorted(indexed_arr, key=lambda x: x[0])
    
    # Extract the sorted indices from the sorted tuple array
    sorted_indices = [index for _, index in sorted_arr]
    
    # Extract the sorted elements from the sorted tuple array
    sorted_elements = [element for element, _ in sorted_arr]
    
    return sorted_elements, sorted_indices

