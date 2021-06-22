# Taking the output of Creating IT Tables from TIPNets Results.py (one sheet per reservoir and timestep combination)
# Outputting Circos files (karyotype, link) which have one node per reservoir; U, R, and S on the same node

import xlrd
from csv import reader

#**********Names and Definitions**********

# Output File from Creating IT Tables from TIPNets Results.py
# Has to be a file which includes sheets with ALL of the reservoirs
# used to generate the information theory results, with no deleted sheets
input_file = 'IT Tables.xlsx'

# Reservoirs in the IT Table, in the order they appear in the IT Table
# (Copy Paste from Creating IT Tables from TIPNets Results.py)
reservoir_lst = ['BON', 'IHR', 'CHJ', 'GCL']

# Timesteps in IT Table, in the order they appear in IT Table code
timestep_lst = ['Daily', 'Monthly', 'Fall', 'Spring', 'Summer', 'Winter', 'Annual']

# Creating a list of sheetnames in the excel file
# DO NOT DELETE SHEETS WITH NO DATA. This code will print the timesteps without data for each reservoir
sheet_names = []
for res in reservoir_lst:
    for timestep in timestep_lst:
        sheetname = res + ' ' + timestep

        sheet_names.append(sheetname)

# Creating a dictionary that maps each reservoir name to its index in reservoir_lst
# Used to assign each reservoir a chromosome number when creating the link and karyotype files
reservoir_to_index_dict = {}
for ind in range(len(reservoir_lst)):
    reservoir_to_index_dict[reservoir_lst[ind]] = ind

# Creating a list of metric names from varnames
# Creating a dictionary where reservoir_dict[variable] = reservoir_name (Ex. reservoir_dict['BON.Flow_In'] = 'BON')
metric_names = []
reservoir_dict = {}
with open('varnames.csv', 'r') as v_file:
    vars = reader(v_file)

    for row in vars:
        for item in range(len(row)):
            metric_names.append(row[item])
            for h in range(len(reservoir_lst)):
                if reservoir_lst[h] in row[item]:
                    reservoir_dict[row[item]] = reservoir_lst[h]

reservoir_dict['None'] = 'None'

# **********Reading from the output of the It Table code, creating a list of list containing the data for each reservoir,
# and for each timestep within each reservoir**********
wb = xlrd.open_workbook(input_file)

all_data_with_repeats_metric_to_reservoir = []
no_data_metric_to_reservoir = []

for n in range(len(reservoir_lst)):
    all_data_with_repeats_metric_to_reservoir.append([])
    no_data_metric_to_reservoir.append([])

sheet_index = 0
reservoir_index = 0
source_order_flip_dict = {}
for this_res in range(len(sheet_names)):
    ws = wb.sheet_by_index(this_res)

    this_lst_w_data = []
    this_lst_no_data = []
    for this_index in range(1, ws.nrows):

        new_row = []
        new_row_with_data = []

        if not ws.cell_value(this_index, 0) == 'U':
            if not (reservoir_dict[ws.cell_value(this_index, 2)],
                reservoir_dict[ws.cell_value(this_index, 1)]) in source_order_flip_dict.values():

                source_order_flip_dict[
                reservoir_dict[ws.cell_value(this_index, 2)], reservoir_dict[ws.cell_value(this_index, 1)]] = (
                reservoir_dict[ws.cell_value(this_index, 1)], reservoir_dict[ws.cell_value(this_index, 2)])

        source_1 = reservoir_dict[ws.cell_value(this_index, 1)]
        source_2 = reservoir_dict[ws.cell_value(this_index, 2)]

        # Passing source pairs through the dictionary (for R and S values) such that repeat pairs are in the opposite order
        # if they appear in the dictionary keys
        # (Ex. (BON, GCL) and (GCL, BON)) are condensed into one
        if not ws.cell_value(this_index, 0) == 'U':
            if (reservoir_dict[ws.cell_value(this_index, 1)], reservoir_dict[ws.cell_value(this_index, 2)]) in list(
                source_order_flip_dict.keys()):
                source_tuple = source_order_flip_dict[
                reservoir_dict[ws.cell_value(this_index, 1)], reservoir_dict[ws.cell_value(this_index, 2)]]

                source_1 = source_tuple[0]
                source_2 = source_tuple[1]

                new_row = [ws.cell_value(this_index, 0), source_1, source_2, ws.cell_value(this_index, 3), 0]
                new_row_with_data = [ws.cell_value(this_index, 0), source_1, source_2, ws.cell_value(this_index, 3),
                                 ws.cell_value(this_index, 4)]

        else:
            new_row = [ws.cell_value(this_index, 0), source_1, source_2, ws.cell_value(this_index, 3), 0]
            new_row_with_data = [ws.cell_value(this_index, 0), source_1, source_2,
                                 ws.cell_value(this_index, 3), ws.cell_value(this_index, 4)]

        this_lst_w_data.append(new_row_with_data)
        this_lst_no_data.append(new_row)

    # Making sure all timesteps with data are added to the sub-list for each reservoir
    sheet_index += 1

    if sheet_index % len(timestep_lst) != 0:
        all_data_with_repeats_metric_to_reservoir[reservoir_index].append(this_lst_w_data)
        no_data_metric_to_reservoir[reservoir_index].append(this_lst_no_data)
    elif sheet_index % len(timestep_lst) == 0:
        all_data_with_repeats_metric_to_reservoir[reservoir_index].append(this_lst_w_data)
        no_data_metric_to_reservoir[reservoir_index].append(this_lst_no_data)
        if reservoir_index < (len(reservoir_lst) - 1):
            reservoir_index += 1

# **********Adding IT metric information together for all source pairs**********
# Looping through the set of lists for
# Each reservoir
for a in range(len(all_data_with_repeats_metric_to_reservoir)):
    # For each timestep
    for b in range(len(all_data_with_repeats_metric_to_reservoir[a])):
        # For each list within each timestep, looping through all lists with values for each list without
        for c in range(len(no_data_metric_to_reservoir[a][b])):
            for x in range(len(all_data_with_repeats_metric_to_reservoir[a][b])):
                if len(all_data_with_repeats_metric_to_reservoir[a][b][x]) != 0 and len(no_data_metric_to_reservoir[a][b][c]) != 0:
                    if no_data_metric_to_reservoir[a][b][c][0] == all_data_with_repeats_metric_to_reservoir[a][b][x][0] and \
                            no_data_metric_to_reservoir[a][b][c][1] == all_data_with_repeats_metric_to_reservoir[a][b][x][
                            1] and no_data_metric_to_reservoir[a][b][c][2] == all_data_with_repeats_metric_to_reservoir[a][b][x][2]:
                        no_data_metric_to_reservoir[a][b][c][4] += all_data_with_repeats_metric_to_reservoir[a][b][x][4]

# **********Removing repeats from no_data_metric_to_reservoir**********
all_data_no_repeats = []
all_timesteps_with_data = []

for this_reservoir_lst in no_data_metric_to_reservoir:
    all_data_res_lst = []
    all_timestep_res_lst = []
    for timestp in this_reservoir_lst:
        all_data_timestep_lst = []

for w in range(len(no_data_metric_to_reservoir)):
    all_data_res_lst = []
    all_timestep_res_lst = []
    for u in range(len(no_data_metric_to_reservoir[w])):
        all_data_timestep_lst = []
        for v in range(len(no_data_metric_to_reservoir[w][u])):
            # Eliminating empty lists
            if len(no_data_metric_to_reservoir[w][u][v]) != 0:
                # Eliminating repeats
                item = no_data_metric_to_reservoir[w][u][v]
                if item not in all_data_timestep_lst:
                    all_data_timestep_lst.append(item)

        all_data_res_lst.append(all_data_timestep_lst)
        all_timestep_res_lst.append(timestep_lst[u])

    all_data_no_repeats.append(all_data_res_lst)
    all_timesteps_with_data.append(all_timestep_res_lst)

# **********Creating separate lists for R, S, and U information (each will be a separate set of links)**********
R_lst = []
S_lst = []
U_lst = []

for i in range(len(all_data_no_repeats)):
    R_res_lst = []
    S_res_lst = []
    U_res_lst = []
    for s in range(len(all_data_no_repeats[i])):
        R_timestep_lst = []
        S_timestep_lst = []
        U_timestep_lst = []
        for t in range(len(all_data_no_repeats[i][s])):
            if all_data_no_repeats[i][s][t][0] == 'R':
                R_timestep_lst.append(all_data_no_repeats[i][s][t])
            elif all_data_no_repeats[i][s][t][0] == 'S':
                S_timestep_lst.append(all_data_no_repeats[i][s][t])
            elif all_data_no_repeats[i][s][t][0] == 'U':
                U_timestep_lst.append(all_data_no_repeats[i][s][t])

        R_res_lst.append(R_timestep_lst)
        S_res_lst.append(S_timestep_lst)
        U_res_lst.append(U_timestep_lst)

    R_lst.append(R_res_lst)
    S_lst.append(S_res_lst)
    U_lst.append(U_res_lst)

# **********Creating karyotype and link files with each reservoir's flow out as the target, for each timestep**********
separator = '\t'
len_lst = []
timesteps_without_data = []

for r in range(len(reservoir_lst)):
    len_lst.append([])
    timesteps_without_data.append([])

reserv_ind = 0
for reserv in all_timesteps_with_data:
    timestep_ind = 0
    for timestep in reserv:
        # Defining a list which will keep track of the total bit size of each node
        # (ie. the total amount of information in the links of each reservoir)
        this_len_lst = [0]*len(reservoir_lst)

        link_file = reservoir_lst[reserv_ind] + '_' + timestep + '_links_final.txt'
        link = open(link_file, 'w')

        for u_ind in range(len(U_lst[reserv_ind][timestep_ind])):
            # Chromosome number
            chrom = str(reservoir_to_index_dict[(U_lst[reserv_ind][timestep_ind][u_ind][1])] + 1)
            # Defining a row of the link file
            row = ['hs' + chrom, str(0), str(int(round(float(U_lst[reserv_ind][timestep_ind][u_ind][4]) * 10))), 'hs' + chrom,
                       str(int(round(float(U_lst[reserv_ind][timestep_ind][u_ind][4]) * 10 + 1))),
                       str(2 * int(round(float(U_lst[reserv_ind][timestep_ind][u_ind][4]) * 10)) + 1), 'color=u']

            # Getting rid of any links that have 0 U. Doing the same for all R and S links below
            if not row[1] == row[2]:
                link.write(separator.join(row) + '\n')

                # Adding all U bits to the total length (2* (U_val*10) + 1)
                this_len_lst[reservoir_to_index_dict[(U_lst[reserv_ind][timestep_ind][u_ind][1])]] += (2 * int(round(
                        float(U_lst[reserv_ind][timestep_ind][u_ind][4]) * 10))) + 1

        # Adding R links
        for r_ind in range(len(R_lst[reserv_ind][timestep_ind])):
            chrom_1 = str(reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])] + 1)
            chrom_2 = str(reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][2])] + 1)

            if chrom_1 == chrom_2:
                start_len_1 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]])
                end_len_1 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] + int(round(
                                float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10)))
                start_len_2 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] + int(round(
                                float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10) + 1))
                end_len_2 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] + (2 * int(round(
                                float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10))) + 1)
                row = ['hs' + chrom_1, start_len_1, end_len_1, 'hs' + chrom_2, start_len_2, end_len_2,
                                       'color=r']

                if not row[1] == row[2]:
                    link.write(separator.join(row) + '\n')

                    this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] += (2 * int(round(
                                    float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10))) + 1

            elif not chrom_1 == chrom_2:
                start_len_1 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]])
                end_len_1 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] + int(round(
                            float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10)))
                start_len_2 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][2])]])
                end_len_2 = str(this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][2])]] + int(round(
                            float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10)))

                row = ['hs' + chrom_1, start_len_1, end_len_1, 'hs' + chrom_2, start_len_2, end_len_2,
                                       'color=r']

                if not row[1] == row[2]:
                    link.write(separator.join(row) + '\n')

                    this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][1])]] += int(round(
                                float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10))
                    this_len_lst[reservoir_to_index_dict[(R_lst[reserv_ind][timestep_ind][r_ind][2])]] += int(round(
                                float(R_lst[reserv_ind][timestep_ind][r_ind][4]) * 10))

        # Adding S links
        for s_ind in range(len(S_lst[reserv_ind][timestep_ind])):
            chrom_1 = str(reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])] + 1)
            chrom_2 = str(reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][2])] + 1)

            if chrom_1 == chrom_2:
                start_len_1 = str(this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]])
                end_len_1 = str(this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] + int(round(
                            float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10)))
                start_len_2 = str(
                            this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] + int(round(
                                float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10)) + 1)
                end_len_2 = str(this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] + (2 * int(round(
                            float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10))) + 1)
                row = ['hs' + chrom_1, start_len_1, end_len_1, 'hs' + chrom_2, start_len_2, end_len_2,
                                       'color=s']

                if not row[1] == row[2]:
                    link.write(separator.join(row) + '\n')

                    this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] += ((2 * int(round(
                            float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10))) + 1)

            elif not chrom_1 == chrom_2:
                start_len_1 = str(this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]])
                end_len_1 = str(
                            this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] + int(round(
                                float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10)))
                start_len_2 = str(this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][2])]])
                end_len_2 = str(
                            this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][2])]] + int(round(
                                float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10)))

                row = ['hs' + chrom_1, start_len_1, end_len_1, 'hs' + chrom_2, start_len_2, end_len_2,
                                       'color=s']

                if not row[1] == row[2]:
                    link.write(separator.join(row) + '\n')

                    this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][1])]] += int(round(
                                float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10))
                    this_len_lst[reservoir_to_index_dict[(S_lst[reserv_ind][timestep_ind][s_ind][2])]] += int(round(
                                float(S_lst[reserv_ind][timestep_ind][s_ind][4]) * 10))

        # Writing to the karyotype file
        karyotype_file = reservoir_lst[reserv_ind] + '_' + timestep_lst[
                    timestep_ind] + '_karyotype_final.txt'

        karyotype = open(karyotype_file, 'w')

        number_reservoirs_no_data = 0
        for i in range(len(reservoir_lst)):
            end_val = str(this_len_lst[i])

            row = ['chr', '-', 'hs' + str(i + 1), reservoir_lst[i], str(0), end_val, reservoir_lst[i]]

            if not row[4] == row[5]:
                karyotype.write(separator.join(row) + '\n')
            else:
                number_reservoirs_no_data += 1

        karyotype.close()

        len_lst[reserv_ind].append(this_len_lst)

        if number_reservoirs_no_data == 4:
            timesteps_without_data[reserv_ind].append(timestep)

        timestep_ind += 1
    reserv_ind += 1

# Printing the timesteps without data for each reservoir. Don't use these to generate Circos images
for reservoir_ind in range(len(timesteps_without_data)):
    print(reservoir_lst[reservoir_ind], timesteps_without_data[reservoir_ind])