import streamlit as st
import pandas as pd

# Streamlit app title
st.title("Data Validation-01")

# File uploader for target and reference Excel files
target_file = st.file_uploader("Upload Recon Data Excel File", type=['xlsx'])
reference_file = st.file_uploader("Upload Bank Statement Excel File", type=['xlsx'])

if target_file and reference_file:
    # Load the target sheet into a DataFrame
    df1 = pd.read_excel(target_file)

    # Clean column names
    df1.columns = df1.columns.str.strip()

    # Rename columns for consistency
    df1.rename(columns={
        'UTR_Details': 'UTR',
        'Date_Details': 'Date',
        'collection_amount': 'Amount',
        'Bank _Name_Details': 'Bank Name',
    }, inplace=True)

    # Ensure 'Date' and 'UTR' columns are properly formatted
    df1['Date'] = pd.to_datetime(df1['Date'], errors='coerce').dt.strftime('%d-%m-%Y')
    df1['UTR'] = df1['UTR'].astype(str)

    # Remove duplicates by UTR and aggregate relevant columns
    df1_grouped = df1.groupby('UTR', as_index=False).agg({
    'Amount': 'sum',
    'Date': 'first',
    'Bank Name': 'first',
    'partner_name': 'first',
    'region': 'first',
    'hub_code': 'first',
    'hub_name': 'first',
    'spoke_code': 'first',
    'spoke_name': 'first',
    'MCC Centre Id': 'first',
    'MCC Centre Name': 'first',
    'RM/SO Id': 'first',
    'RM/SO Name': 'first',
    'State': 'first',
    'deposited_bank_account': 'first',
    'deposited_bank_branch': 'first',
    'bank_deposit_reference': 'first',  
    'collected_by': 'first',
    'deposited_by': 'first',
    'account_number': 'first',
    'ClientID': 'first',
    'product_name': 'first',
    'product_code': 'first',
    'customer_name': 'first',
    'applicant_name': 'first',
    'customer id': 'first',
    'Applicant URN': 'first',
    'demand_date': 'first',
    'loan_amount': 'first',
    'schedule_demand_amount': 'first',
    'installment_number': 'first',
    'EMI Amount': 'first',
    'tenure': 'first',
    'instrument_type': 'first',
    'repayment_posted_date': 'first',
    'deposited_on_date': 'first',
    'principal_magnitude': 'first',
    'normal_interest_magnitude': 'first',
    'adjusted_security_emi': 'first',
    'fee_amount': 'first',
    'Penal_due': 'first',
    'Bounce_charges': 'first',
    'fee_waiver_amount': 'first',
    'Transaction Name': 'first',
    'status': 'first',
    'additional_interest_waiver_amount': 'first',
    'approved_by': 'first',
    'Approved Date and time': 'first',
    'stage': 'first',
    'Reject Reason': 'first',
    'Reject Remarks': 'first',
    'Rejected stage': 'first',
    'Rejected by': 'first',
}, errors='ignore')

    # Load all sheets from the reference file
    sheets = pd.read_excel(reference_file, sheet_name=None)

    # Define mappings for bank names and sheet structures
    bank_to_sheet_mapping = {
        'AirtelPayment': 'Airtel Payments Bank',
        'FinoBank': 'FinoBank',
        'SpiceMoney': 'Spice Money',
        'FingpayAccount': 'FingpayAccount',
        'SBIPowerJyothi': 'SBI PJ -7190',
        'Axis Bank': 'Axis Bank -4542',
    }

    sheet_column_mapping = {
    'Airtel Payments Bank': {'Transaction Id': 'UTR', 'Date and Time': 'Date', 'Original Input Amt': 'Amount', 'Bank Name': 'Bank Name'},
    'FinoBank': {'TRANSACTION ID': 'UTR', 'LOCAL DATE': 'Date', 'AMOUNT': 'Amount', 'Bank Name': 'Bank Name'},
    'Spice Money': {'Spice Txn ID': 'UTR', 'Date': 'Date', 'Amount': 'Amount', 'Bank Name': 'Bank Name'},
    'FingpayAccount': {'Fingpay Transaction Id': 'UTR', 'Corporate': 'Date', 'Drop Amount': 'Amount', 'Bank': 'Bank Name'},
    'SBI PJ -7190': {'Narration': 'UTR', 'Txn Date': 'Date', 'Credit': 'Amount', 'Bank Name': 'Bank Name'},
    'Axis Bank -4542': {'Transaction Particulars': 'UTR', 'Tran Date': 'Date', 'Amount(INR)': 'Amount', 'Bank Name': 'Bank Name'},
    }

    # Process each bank
    merged_results = []
    for bank_name, sheet_name in bank_to_sheet_mapping.items():
        if sheet_name in sheets and sheet_name in sheet_column_mapping:
            df1_filtered = df1_grouped[df1_grouped['Bank Name'] == bank_name]
            if df1_filtered.empty:
                continue

            df2 = sheets[sheet_name]
            df2.rename(columns=sheet_column_mapping[sheet_name], inplace=True)
            df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.strftime('%d-%m-%Y')
            df2['UTR'] = df2['UTR'].astype(str)

            df2_filtered = df2[df2['UTR'].isin(df1_filtered['UTR'])]
            merged_df = df1_filtered.merge(df2_filtered, on='UTR', how='left', suffixes=('', '_df2'))

            merged_df['date_status'] = merged_df.apply(
            lambda row: 'matched' if row['Date'] == row['Date_df2'] else 'mismatched', axis=1
        )
        merged_df['amount_status'] = merged_df.apply(
            lambda row: 'matched' if row['Amount'] == row['Amount_df2'] else 'mismatched', axis=1
        )
        merged_df['bank_name_status'] = merged_df.apply(
            lambda row: 'matched' if row['Bank Name'] == row['Bank Name_df2'] else 'mismatched', axis=1
        )
        merged_df['utr_status'] = merged_df.apply(
            lambda row: 'matched' if pd.notna(row['Date_df2']) else 'mismatched', axis=1
        )

        # Add final status
        merged_df['final_status'] = merged_df.apply(
            lambda row: 'Ok' if (
                row['date_status'] == 'matched' and
                row['amount_status'] == 'matched' and
                row['utr_status'] == 'matched' and
                row['bank_name_status'] == 'matched'
            ) else 'Not Ok',
            axis=1
        )

        final_columns = [ 'UTR', 'Amount', 'Date', 'Bank Name', 'account_number','partner_name', 'region', 'hub_code',
            'hub_name', 'spoke_code', 'spoke_name', 'MCC Centre Id', 'MCC Centre Name',
            'RM/SO Id', 'RM/SO Name', 'State', 'date_status', 'amount_status', 
            'bank_name_status', 'utr_status', 'final_status']
        merged_df = merged_df[final_columns]
        merged_results.append(merged_df)

    if merged_results:
        final_df = pd.concat(merged_results, ignore_index=True)
        st.success("Data processed successfully!")

        # Display the DataFrame
        st.dataframe(final_df)

        # Option to download the result as an Excel file
        output_file = "final_reconciliation.xlsx"
        final_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as file:
            st.download_button(
                label="Download Reconciled Data",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No matching data found.")
