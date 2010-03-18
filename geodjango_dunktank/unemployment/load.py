"""
Utilities for loading unemployment data and linking it our maps.
"""


def _get_csv():
    """
    Wrangle the CSV file from our source file.

    I'm starting the name of the function with an underscore, because I don't
    plan on calling it directly. Instead I'm going to use it a couple of 
    times below in other functions.
    
    It's nice to write it up here separately because them I can save myself
    from having to repeat it more than once below.
    """
    import os
    import csv
    # Get the path to our data file
    this_dir = os.path.dirname(__file__)
    data_path = os.path.join(this_dir, 'data/LabForce-CAMSACo.txt')
    # Open up the datafile using Python's CSV module, which will use the
    # headers at the top to key the values in each row as a dictionary.s
    reader = csv.DictReader(open(data_path, 'r'))
    # Pass out the data as a list to whoever calls this function.
    return [i for i in reader]


def specs():
    """
    Print some basic stats about our CSV file, which we can use to write our
    models and think about things a little bit.
    
    Example usage:
    
        >> from unemployment import load; load.specs();
        
    """
    data = _get_csv()
    # I'll proof the results of these against the source CSV file
    # make sure everything in python matches.
    fields = data[0].keys()
    print "%s fields: %s" % (len(fields), fields)
    print "%s total rows" % len(data)
        


def monthlys():
    """
    Load the monthly unemployment totals for each county

    Example usage:
    
        >> from unemployment import load; load.monthly();

    """
    from mapping.counties.models import County
    from unemployment.models import CountyByMonth
    
    # Fetch our data
    data = _get_csv()
    # Filter it down to just the counties (it also has statewide and MSAs)
    data = [i for i in data if i['areatype'] == '04']
    # Filter it down to only the monthly totals (it also has annual totals)
    data = [i for i in data if i['periodtype'] == '03']
    # Run through each remaining row and load it in the database
    for row in data:
        # Pull the fips code out of the data
        county_fips_code = row['area'][3:]
        # Use that fips to pull our County record from the database
        county = County.objects.get(county_fips_code=county_fips_code)
        # Create a new database record in our system
        record, c = CountyByMonth.objects.get_or_create(
            county=county,
            year=row['periodyear'],
            month=row['period'],
            labor_force=row['laborforce'],
            employment=row['emplab'],
            unemployment=row['unemp'],
            unemployment_rate=row['unemprate'],
            is_preliminary=_prep_prelim(row['Preliminary']),
            is_seasonally_adjusted=_prep_adjustment(row['Adjusted']),
            benchmark=row['benchmark'],
        )
        if c:
            print "Added %s" % record


def _prep_prelim(string):
    """
    Clean up the preliminary data field to prep it for the database
    """
    if string == 'Prelim':
        return True
    else:
        return False


def _prep_adjustment(string):
    """
    Clean up the adjustment data to prep it for the database
    """
    if string == 'Adj':
        return True
    else:
        return False








