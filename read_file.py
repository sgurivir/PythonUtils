import re

summary = None
with open("/tmp/summary.txt", "r") as f:
    summary = f.readlines()
    f.close()

def first_line_with_string(substring):
    """Returns first line with substring match """
    for line in summary:
        if substring in line:
            return line.strip("\n")
    
    return None
    
"""
class Example:
    @staticmethod
    def get_all():
        [cov_x, cov_y, cov_z, cov_h] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Match covariance:"))
        print cov_x
        print cov_y
        print cov_z
        print cov_h

        # Ex: Average height error: 0.000 and std dev: 0.000 and height covariance: 1.588
        [avg_h_error, avg_h_stdev, avg_h_cov] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Average height error:"))

        # Ex: Average heading error: 0.578 and std dev: 9.971 and heading covariance: 0.126
        [avg_heading_error, avg_heading_stdev, avg_heading_cov] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Average heading error:"))

        # Ex: Horizontal distance: mean=0.369011; median=0.803968; max=1.95206
        [hdist_mean, hdist_median, hdist_max] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Horizontal distance:"))

        # Ex: Percentage match: 5.537
        [percentage_match] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Percentage match:"))

        # Ex: First match: 25277 last match: 34460
        [first_match, last_match] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("First match:"))

"""    
#print match_obj
#Example.get_all()

# Ex: Total: 165858 success: 9184 failure: 156674
        
        
        #[total, success, failure] = re.findall(r"\d+",
        #                                       first_line_with_string("Total:"))
        #print total

    
def get_all():
    # Ex: Total: 165858 success: 9184 failure: 156674
    [total, success, failure] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Total:"))
    print total, success, failure
    
    # Ex: Average match error: (0.026, 0.000, 0.049) (0.578)
    [avg_match_error_x, avg_match_error_y, avg_match_error_z, avg_match_error_h] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Average match error:"))
    print avg_match_error_x, avg_match_error_y, avg_match_error_z, avg_match_error_h
                     
    [cov_x, cov_y, cov_z, cov_h] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Match covariance:"))
    print cov_x, cov_y, cov_z, cov_h

    # Ex: Average height error: 0.000 and std dev: 0.000 and height covariance: 1.588
    [avg_h_error, avg_h_stdev, avg_h_cov] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Average height error:"))
    print avg_h_error, avg_h_stdev, avg_h_cov

    # Ex: Average heading error: 0.578 and std dev: 9.971 and heading covariance: 0.126
    [avg_heading_error, avg_heading_stdev, avg_heading_cov] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Average heading error:"))
    print avg_heading_error, avg_heading_stdev, avg_heading_cov

    # Ex: Horizontal distance: mean=0.369011; median=0.803968; max=1.95206
    [hdist_mean, hdist_median, hdist_max] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Horizontal distance:"))
    print hdist_mean, hdist_median, hdist_max

    # Ex: Percentage match: 5.537
    [percentage_match] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("Percentage match:"))
    print percentage_match

    # Ex: First match: 25277 last match: 34460
    [first_match, last_match] = re.findall(r"[-+]?\d*\.*\d+", first_line_with_string("First match:"))
    print first_match, last_match

get_all()



