def merge_lists(list_of_lists):
    """
    Merges a list of lists into a single list containing all elements.
    
    Args:
    list_of_lists (list of lists): The input list containing multiple lists to be merged.
    
    Returns:
    list: A single list containing all elements from the input lists.
    """
    merged_list = [item for sublist in list_of_lists for item in sublist]
    return merged_list