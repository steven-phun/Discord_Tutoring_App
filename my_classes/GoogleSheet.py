import os
import gspread
import openpyxl
from datetime import date
from calendar import day_name


class GoogleSheet:
    def __init__(self):
        self.excel_workbook = openpyxl.load_workbook('student_sign_in_sheet/excel_template.xlsx')

    def get_sign_in_sheet(self, tutor, day):
        """transfer the information from the google sign-in sheet to school's sign-in sheet format.

        a template of the school's excel sheet is stored in a local .xlsx file.

        Parameters
        ----------
        :param 'Tutor' tutor: the tutor object that the sign-in sheet is generated for.
        :param 'datetime' day: the datetime object that represents the sign-in sheet will be generated at.
        """
        # get the google sign-in sheet.
        sheet = get_google_sheet()
        # generate an excel sheet from template.
        excel = self.excel_workbook.active

        # edit template with tutor's information.
        excel_date_format = date.strftime(day, '%m/%d/%Y')
        excel['D10'].value = tutor.name  # tutor's name
        excel['D4'].value = tutor.course.code  # course code
        excel['B6'].value = day_name[day.weekday()]  # day of the week
        excel['G6'].value = excel_date_format

        # transfer student information.
        cell_num = 13  # the starting cell for student's info in excel.
        for content in sheet:
            if content['Timestamp'].split(' ')[0] == excel_date_format and content['Tutor'] == tutor.name:
                excel[f'A{cell_num}'].value = content['Student ID']
                excel[f'D{cell_num}'].value = content['Student Name']
                excel[f'H{cell_num}'].value = content['Degree']

                cell_num += 1

        self.excel_workbook.save(f'student_sign_in_sheet/{tutor.name} {date.strftime(day, "%Y-%m-%d")}.xlsx'.replace(' ', '_'))


def get_google_sheet():
    """        BOT AUTHENTICATION AND AUTHORIZATION NEEDED:
            for gspread api: https://gspread.readthedocs.io/en/latest/
        API DOCUMENTATIONS AND RESTRICTIONS LIMITS:
            restrictions:
                Sheets API v4 introduced Usage Limits as of this writing:
                    500 requests per 100 seconds per project,
                    100 requests per 100 seconds per user.
                API will display an APIError 429 RESOURCE_EXHAUSTED:
        ACTION NEEDED:
            google form appends new data to the end of the sheet rather than inserting it at the top of the sheet.
                to reduce the time complexity, new data should be searched first.
            add a new sheet and insert the formula in the A1 cell.
                =SORT('Form responses 1'!A1:R,1,false)
                'Form responses 1' is the sheet's name that contains the sign-in information.
        WARNING: google sheet api takes 3-5 seconds to open.
            to improve user's experience place this function where the user would feel the least amount of delay.
            it is NOT recommend to look up and modify the sheet directly because the delay will be noticeable.
                instead store the sheet's content in a data structure
                    then perform the look ups and modification on the data structure.
    """
    # get authentication and authorization from google sheet student_sign_in_sheet file.
    credentials = gspread.service_account(filename='student_sign_in_sheet/google_cred.json')

    # get sign-in sheet.
    sheet = credentials.open_by_key(os.getenv("GOOGLE_SHEET_KEY")).get_worksheet(1)

    # store content in dictionary.
    return sheet.get_all_records()
