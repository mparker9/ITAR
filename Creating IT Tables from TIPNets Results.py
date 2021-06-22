# Takes in TIPNets results as csv files (see User Guide for details);
# Outputs an excel spreadsheet with IT results grouped by target

from csv import reader
import xlsxwriter

#**********Names and Definitions**********

# Information theory metrics which should be included in the final spreadsheet
# (include all for Circos file generation code input)
IT_metric_lst = ['S', 'R', 'U']

# Define the reservoir names used to generate TIPNets results,
# and the reservoirs and timesteps to be included in the excel doc
# ***CHANGE TO FIT DATA***
allmatlabused_reservoir_lst = ['BON', 'IHR', 'CHJ', 'GCL']
alloutput_reservoir_lst = ['BON', 'IHR', 'CHJ', 'GCL']
target_string = '.Flow_Out [kcfs]'
timestep_lst = ['Daily', 'Monthly', 'Fall', 'Spring', 'Summer', 'Winter', 'Annual']

# Desired spreadsheet name
sprsheet_name = 'IT Tables.xlsx'

# Names of TIPNets csv files containing source pairings and variable names (see User Guide)
pair_file = 'pairvars.csv'
var_file = 'varnames.csv'

# Header of each sheet in the excel doc
header = ['IT Metric', 'Source1', 'Source2', 'Target', 'Value']

# Delete if file names are changed below (see User Guide)
# ***CHANGE TO FIT DATA***
PDO_yes_no = 'noPDO'

num_metrics = len(IT_metric_lst)

#**********Assembling Dictionary of Variable Names and List of Filenames Containing TIPNet Results**********

# Creating a dictionary mapping TIPNet variable numbers to names
# Format: var_dict = {1:BON.Flow_In [kcfs], 2: BON.Flow_Out [kcfs], . . .}
var_dict = {}

with open(var_file) as v_file:
    varnames = reader(v_file)

    for row in varnames:
        for i in range(len(row)):
            var_dict[i+1]= row[i]

# Reading from pairvars and converting numbers to variable names
sourcepair_lst = []
with open(pair_file) as pairs:
    pairs_csv = reader(pairs)

    # Creating a source_pair list

    for row in pairs_csv:
        # Adding the metrics (by plugging their numbers into variable_dict) to the source list
        metric_row = []

        for i in range(2):
            metric_row.append(var_dict[int(row[i])])
        sourcepair_lst.append(metric_row)

# Creating lists of filenames for each IT metric and timestep
allfiles_file_lst = []
Itot_file_lst = []
S_file_lst = []
R_file_lst = []
U_file_lst = []

for timestep in timestep_lst:
    this_timestep_lst = []
    for IT_metric in IT_metric_lst:
        # ***CHANGE TO FIT DATA***
        if not IT_metric == 'U':
            file_str = 'Columbia_' + timestep + '_' + PDO_yes_no + '_no Bogus_' + IT_metric + '_allpairs.csv'
        else:
            file_str = 'Columbia_' + timestep + '_' + PDO_yes_no + '_no Bogus_' + IT_metric + '.csv'

        this_timestep_lst.append(file_str)

        if IT_metric == 'Itot':
            Itot_file_lst.append(file_str)
        elif IT_metric == 'S':
            S_file_lst.append(file_str)
        elif IT_metric == 'R':
            R_file_lst.append(file_str)
        elif IT_metric == 'U':
            U_file_lst.append(file_str)

    allfiles_file_lst.append(this_timestep_lst)


#**********Reading through TIPNets Result Files and Generating a List Containing All Source Pairs and Targets**********

# List format: full_lst = [[[Itot, BON, GCL, BON.Flow_Out[kcfs], 2.793], . . .],
# [IHR target rows], [CHJ target rows], [GCL target rows]]

full_lst = []

for lst in allfiles_file_lst:
    this_lst_timestep = []

    file_num = 0
    for file in lst:
        with open(file) as f:
            this_file = reader(f)

            j = 0
            for row in this_file:

                for i in range(len(row)):
                    this_row = []

                    target_str = var_dict[i + 1]
                    metric_val = float(row[i])

                    this_metric = IT_metric_lst[file_num]

                    if not this_metric == 'U':
                        source1_str = sourcepair_lst[j][0]
                        source2_str = sourcepair_lst[j][1]
                        this_row = [this_metric, source1_str, source2_str, target_str, metric_val]

                    elif this_metric == 'U':
                        source1_str = var_dict[j + 1]
                        source2_str = 'None'
                        this_row = ['U', source1_str, source2_str, target_str, metric_val]

                    # Eliminating source pairs that contributed no information
                    if not metric_val == 0:
                        this_lst_timestep.append(this_row)

                j += 1

        file_num += 1

    full_lst.append(this_lst_timestep)

#**********Creating a List With Only Flow Out Variables as Targets, Grouping by Reservoir, Ordering Sourcepairs from Max to Min**********

updated_full_lst = []
# Grouping by reservoir (each reservoir will have all sourcepairs for each timestep)
for reservoir in alloutput_reservoir_lst:
    this_reservoir_lst = []
    # Looping through each timestep
    for lst in full_lst:
        new_lst_1 = []

        this_target_str = reservoir + target_string

        # Filtering out any sourcepairs which do not have the particular reservoir and variable type as the target
        lst = [row for row in lst if row[3] == this_target_str]

        # Ordering sourcepairs within each timestep from max to min
        lst.sort(key = lambda x: x[4], reverse = True)

        this_reservoir_lst.append(lst)

    updated_full_lst.append(this_reservoir_lst)


#**********Generating Sheet Names (One for each Reservoir and Timestep Combination)**********

sheet_name_lst = []
full_metric_lst = []

for j in range(len(alloutput_reservoir_lst)):
    for i in range(len(timestep_lst)):
        sheet_name = alloutput_reservoir_lst[j] + ' ' + timestep_lst[i]
        sheet_name_lst.append(sheet_name)


workbook = xlsxwriter.Workbook(sprsheet_name)

#**********Adding Text and Background Colors; Writing Rows to the Excel File**********

# Defining colors which can be used in the spreadsheet

blue = workbook.add_format({'bold': False, 'font_color': 'blue'})
green = workbook.add_format({'bold': False, 'font_color': 'green'})
red = workbook.add_format({'bold': False, 'font_color': 'red'})
pink = workbook.add_format({'bold': False, 'font_color': 'pink'})
yellow = workbook.add_format({'bold': False, 'font_color': 'yellow'})
navy = workbook.add_format({'bold': False, 'font_color': 'navy'})
orange = workbook.add_format({'bold': False, 'font_color': 'orange'})
magenta = workbook.add_format({'bold': False, 'font_color': 'magenta'})
cyan = workbook.add_format({'bold': False, 'font_color': 'cyan'})
purple = workbook.add_format({'bold': False, 'font_color': 'purple'})
brown = workbook.add_format({'bold': False, 'font_color': 'brown'})
white = workbook.add_format({'bold': False, 'font_color': 'white'})

# Assigning colors to each IT metric and reservoir

Itot_format = workbook.add_format()
Itot_format.set_color('#F4D03F')

R_format = workbook.add_format()
R_format.set_color('#F39C12')

S_format = workbook.add_format()
S_format.set_color('#CA6F1E')

U_format = workbook.add_format()
U_format.set_color('#A04000')

# ***CHANGE TO FIT DATA***

BON_format = workbook.add_format()
BON_format.set_bg_color('cyan')

IHR_format = workbook.add_format()
IHR_format.set_bg_color('blue')
IHR_format.set_color('white')

# Previous IHR format. Changed so background color matches IHR node color in Circos images
# IHR_format = workbook.add_format()
# IHR_format.set_bg_color('silver')

CHJ_format = workbook.add_format()
CHJ_format.set_bg_color('pink')

GCL_format = workbook.add_format()
GCL_format.set_bg_color('lime')

lst_num = 0
for reserv in updated_full_lst:
    for lst in reserv:
        sheet_name = sheet_name_lst[lst_num]
        sheet = workbook.add_worksheet(sheet_name)

        sheet.write_row(0, 0, header)


        # Assigning color formats to cells based on their content
        # ***CHANGE TO FIT DATA***
        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"BON.Flow_In [kcfs]"',
                                                 'format': BON_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"BON.Flow_Out [kcfs]"',
                                                 'format': BON_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"BON Storage [kaf]"',
                                                 'format': BON_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"IHR.Flow_In [kcfs]"',
                                                 'format': IHR_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"IHR.Flow_Out [kcfs]"',
                                                 'format': IHR_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"IHR Storage [kaf]"',
                                                 'format': IHR_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"CHJ.Flow_In [kcfs]"',
                                                 'format': CHJ_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"CHJ.Flow_Out [kcfs]"',
                                                 'format': CHJ_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"CHJ Storage [kaf]"',
                                                 'format': CHJ_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"GCL.Flow_In [kcfs]"',
                                                 'format': GCL_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"GCL.Flow_Out [kcfs]"',
                                                 'format': GCL_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"GCL Storage [kaf]"',
                                                 'format': GCL_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"Itot"',
                                                 'format': Itot_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"R"',
                                                 'format': R_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"S"',
                                                 'format': S_format})

        sheet.conditional_format('A1:E500', {'type': 'cell',
                                                 'criteria': 'equal to',
                                                 'value': '"U"',
                                                 'format': U_format})


        for row_len in range(len(lst)):
            sheet.write_row(row_len+1, 0, lst[row_len])

        lst_num += 1

workbook.close()