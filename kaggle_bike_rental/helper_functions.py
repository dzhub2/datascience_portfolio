""" A collection of custom functions to help with common tasks found in Machine Learning"""

from sklearn import metrics

def write_params_to_file(save_switch, path, file_name, saved_params, best_score, comment):
    """Saves the parameters of an sklearn GridSearch to file for history keeping. A comment can be
    added to help remember which features or model generated this score.

    Args:
        save_switch (int): == 1 to save the file
        path (str): save path
        file_name (str): file name to be saved
        saved_params (dict): The parameter result of GridSearch.
        best_score (float): The best score result of GridSearch.
        comment (str): An optional comment you want to add to help your memory.
    """
    if save_switch == 1:
        f = open(path+file_name, "a") # never overwrite file
        f.write(str(saved_params)) 
        f.write("\n") 
        f.write("Best score: " + str(best_score.round(4)))
        f.write("\n") 
        f.write(comment)
        f.write("\n") 
        f.write("------------------------------------------------------------") 
        f.close()
    return True

def calculate_adj_r2(y_pred, y_test, X_train):
    """Calculate the adjusted R-squared"""
    r2 = metrics.r2_score(y_test, y_pred)
    n = len(y_test)# nr. of rows in training data
    p = X_train.shape[1]# nr. of indep varaibles
    adj_r2 = 1-(1-r2)*(n-1)/(n-p-1)
    return adj_r2

