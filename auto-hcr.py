import pandas as pd
import os

def main():
    input_file = 'nessus.csv'
    output_file = 'hcr.csv'
    modified_output_file = 'modified_hcr.csv'

    df = pd.read_csv(input_file)

    filtered_df = df[df['Risk'].isin(['PASSED', 'FAILED', 'WARNING'])]

    myIP = sorted(filtered_df['Host'].unique())

    output_df = pd.DataFrame()

    first_ip_filtered_df = filtered_df[filtered_df['Host'] == myIP[0]]
    first_ip_filtered_df = first_ip_filtered_df.sort_values(by='Description')

    myDesc_first = list(first_ip_filtered_df['Description'])
    mySol_first = list(first_ip_filtered_df['Solution'])
    myRisk_first = list(first_ip_filtered_df['Risk'])

    output_df['Control'] = myDesc_first
    output_df['Recommendation'] = mySol_first
    output_df[myIP[0]] = myRisk_first

    for ip in myIP[1:]:
        ip_filtered_df = filtered_df[filtered_df['Host'] == ip]

        ip_filtered_df = ip_filtered_df.sort_values(by='Description')

        myDesc = list(ip_filtered_df['Description'])
        output_df[f'Control_{ip}'] = myDesc

        mySol = list(ip_filtered_df['Solution'])
        output_df[f'Recommendation_{ip}'] = mySol

        myRisk = list(ip_filtered_df['Risk'])
        output_df[ip] = myRisk

    output_df.to_csv(output_file, index=False)
    print(f'Successfully created {output_file}')

    hcr_df = pd.read_csv(output_file)

    columns_to_keep = hcr_df.columns[:2]

    columns_to_remove = [col for col in hcr_df.columns if col.startswith("Control_") or col.startswith("Recommendation_")]

    hcr_df = hcr_df.drop(columns=columns_to_remove, errors='ignore')

    hcr_df.to_csv(modified_output_file, index=False)
    print(f'Successfully created {modified_output_file} with modified columns.')

    myLastCol = len(hcr_df.columns)
    passed_col_values = hcr_df.iloc[:, 2:].eq('PASSED').sum(axis=1)
    failed_warning_col_values = myLastCol - 2 - passed_col_values

    hcr_df.insert(2, "PASSED", passed_col_values)
    hcr_df.insert(3, "FAILED/WARNING", failed_warning_col_values)

    final_output_file = 'final_hcr.csv'
    hcr_df.to_csv(final_output_file, index=False)
    print(f'Successfully created {final_output_file} with additional columns.')

    final_df = pd.read_csv(final_output_file)

    last_row_index = final_df.index[-1]
    final_df.loc[last_row_index + 2, 'Control'] = 'Total Sum'

    final_df.loc[last_row_index + 3, 'Control'] = 'Total Percentage'

    total_sum_c = final_df.iloc[:, 2].sum()
    final_df.loc[last_row_index + 2, 'PASSED'] = total_sum_c

    total_sum_d = final_df.iloc[:, 3].sum()
    final_df.loc[last_row_index + 2, 'FAILED/WARNING'] = total_sum_d

    total_sum_count = total_sum_c + total_sum_d

    percentage_c = (total_sum_c / total_sum_count) * 100
    final_df.loc[last_row_index + 3, 'PASSED'] = f'{percentage_c:.2f}%'

    percentage_d = (total_sum_d / total_sum_count) * 100
    final_df.loc[last_row_index + 3, 'FAILED/WARNING'] = f'{percentage_d:.2f}%'

    for col in final_df.columns:
        if final_df[col].notna().any():  # Check if the column has any non-null values
            final_df[col] = final_df[col].apply(lambda x: f'{x: <18}' if pd.notna(x) else x)

    final_df.to_csv(final_output_file, index=False)
    print(f'Successfully updated {final_output_file} with additional features and set column widths.')


if __name__ == "__main__":
    main()

    try:
        os.remove('hcr.csv')
        print('Successfully removed hcr.csv')
    except FileNotFoundError:
        print('hcr.csv not found, no removal needed')

    try:
        os.remove('modified_hcr.csv')
        print('Successfully removed modified_hcr.csv')
    except FileNotFoundError:
        print('modified_hcr.csv not found, no removal needed')