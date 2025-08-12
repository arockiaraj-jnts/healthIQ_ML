from sqlalchemy import create_engine, MetaData, Table, select
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv('DATABASE_URL')
print("Connecting to database...")
engine = create_engine(db_url)

metadata = MetaData()
metadata.reflect(bind=engine)

users=metadata.tables["users"]
employeeList=metadata.tables["employee_health_profile"]
labReports=metadata.tables["lab_reports"]
vitalResults=metadata.tables["vital_results"]
lipid_profile_results=metadata.tables["lipid_profile_results"]
liver_profile_results=metadata.tables["liver_profile_results"]
glucose_results=metadata.tables["glucose_results"]
thyroid_results=metadata.tables["thyroid_results"]
pulmonary_profile_results=metadata.tables["pulmonary_profile_results"]
ESR_results=metadata.tables["ESR_results"]
audiogram_results=metadata.tables["audiogram_results"]
#pulmonary_profile_results=metadata.tables["pulmonary_profile_results"]