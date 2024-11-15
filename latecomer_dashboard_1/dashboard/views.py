from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from django.http import HttpResponse
import os
from django.core.files.storage import default_storage

def parse_time(time_str):
    try:
        if pd.isna(time_str) or time_str == '-' or time_str.strip() == '':
            return np.nan
        return pd.to_datetime(time_str, format='%H:%M').time()
    except ValueError:
        return np.nan

def load_data():
    csv_file = os.path.join('dashboard', 'data', 'uploaded_file.csv')
    if not os.path.isfile(csv_file):
        csv_file = os.path.join('dashboard', 'data', 'Test1.csv')

    df = pd.read_csv(csv_file)
    df.rename(columns={
        'Employee Name': 'Employee_Name',
        'Division': 'Division',
        'Date': 'Date',
        'Expected Check-in as per shift': 'Expected_Check_In',
        'Actual Check-in': 'Actual_Check_In',
        'Attendance Status': 'Attendance_Status',
        'Comment': 'Comments',
        'Exceptional Attendance Rule': 'Exceptional_Attendance_Rule',
        'Expected Check-out as per shift': 'Expected_Check_Out',
        'Actual Check-out': 'Actual_Check_Out',
        'In Office Time': 'In_Office_Time',
        'Expected In Office Time': 'Expected_In_Office_Time'
    }, inplace=True)

    df['Expected_Check_In'] = df['Expected_Check_In'].apply(parse_time)
    df['Actual_Check_In'] = df['Actual_Check_In'].apply(parse_time)
    df['Attendance_Status'] = df.apply(
        lambda row: 'Late' if pd.notna(row['Actual_Check_In']) and pd.notna(row['Expected_Check_In']) and row['Actual_Check_In'] > row['Expected_Check_In'] else 'On Time',
        axis=1
    )
    
    # Convert 'Date' column to datetime with the expected format
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['Is_Exceptional'] = df['Exceptional_Attendance_Rule'].apply(lambda x: pd.notna(x))
    return df

def apply_filters(df, request):
    employee_filter = request.GET.get('employee', '')
    division_filter = request.GET.get('division', '')
    date_filter = request.GET.get('date', '')
    exceptional_filter = request.GET.get('exceptional', '')

    if employee_filter:
        df = df[df['Employee_Name'].str.contains(employee_filter, na=False)]
    if division_filter:
        df = df[df['Division'].str.contains(division_filter, na=False)]
    if date_filter:
        try:
            # Convert the date_filter string to a datetime object
            date_filter = pd.to_datetime(date_filter, format='%m/%d/%Y', errors='coerce')
            df = df[df['Date'] == date_filter]
        except ValueError:
            pass  # If date_filter is invalid, do not apply the filter
    if exceptional_filter:
        df = df[df['Exceptional_Attendance_Rule'].str.contains(exceptional_filter, na=False)]
    
    return df

def dashboard(request):
    df = load_data()
    df = apply_filters(df, request)

    # Format the 'Date' column back to 'm/dd/yyyy' for display purposes
    df['Date'] = df['Date'].apply(lambda x: x.strftime('%m/%d/%Y') if pd.notna(x) else 'N/A')

    employee_names = df['Employee_Name'].dropna().unique().tolist()
    divisions = df['Division'].dropna().unique().tolist()
    exceptional = df['Exceptional_Attendance_Rule'].dropna().unique().tolist()

    attendance_summary = df['Attendance_Status'].value_counts().to_dict()
    total_late = attendance_summary.get('Late', 0)
    total_on_time = attendance_summary.get('On Time', 0)
    total_employees = df['Employee_Name'].nunique()
    attendance_rate = round((total_on_time / total_employees) * 100, 2) if total_employees else 0
    total_exceptional = df['Is_Exceptional'].sum()

    chart_data = df['Attendance_Status'].value_counts().to_dict()
    chart_labels = list(chart_data.keys())
    chart_values = list(chart_data.values())

    context = {
        'employee_names': employee_names,
        'divisions': divisions,
        'exceptional': exceptional,
        'total_exceptional': total_exceptional,
        'total_late': total_late,
        'total_on_time': total_on_time,
        'total_employees': total_employees,
        'attendance_rate': attendance_rate,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'table_data': df.to_dict(orient='records'),
        'selected_employee': request.GET.get('employee', ''),
        'selected_division': request.GET.get('division', ''),
        'selected_date': request.GET.get('date', ''),
        'selected_exceptional': request.GET.get('exceptional', ''),
    }

    return render(request, 'dashboard.html', context)

def download_csv(request):
    df = load_data()
    df = apply_filters(df, request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_data.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def download_excel(request):
    df = load_data()
    df = apply_filters(df, request)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="attendance_data.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance Data')
    return response

def upload_file(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        uploaded_file = request.FILES['csv_file']
        file_path = os.path.join('dashboard', 'data', 'uploaded_file.csv')
        
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        return redirect('dashboard')
    return redirect('dashboard')
