import datetime


class Disease:
    def __init__(self, title,cause,symptom,treatment,complication,detail,created_by ,created_date):
        self.__diseaseid = ''
        self.__title = title
        self.__cause = cause
        self.__symptom = symptom
        self.__treatment = treatment
        self.__complication = complication
        self.__detail = detail
        self.__created_by = created_by
        currentdatetime = datetime.datetime.now()
        create_date = str(currentdatetime.day) + "-" + str(currentdatetime.month) + "-" + str(
            currentdatetime.year)  # DD-MM-YYYY format
        self.__created_date = created_date



    def get_diseaseid(self):
        return self.__diseaseid

    def get_title(self):
        return self.__title

    def get_cause(self):
        return self.__cause

    def get_symptom(self):
        return self.__symptom

    def get_treatment(self):
        return self.__treatment

    def get_complication(self):
        return self.__complication

    def get_detail(self):
        return self.__detail

    def get_created_by(self):
        return self.__created_by

    def get_created_date(self):
        return self.__created_date

    def set_title(self, title):
        self.__title = title

    def set_cause(self, cause):
        self.__cause = cause

    def set_symptom(self, symptom):
        self.__symptom = symptom

    def set_treatment(self, treatment):
        self.__treatment = treatment

    def set_complication(self, complication):
        self.__complication = complication

    def set_detail(self, detail):
        self.__detail = detail

    def set_diseaseid(self, diseaseid):
        self.__diseaseid = diseaseid

    def set_created_by(self, created_by):
        self.__createdby = created_by

    def set_created_date(self, created_date):
        self.__created_date = created_date


