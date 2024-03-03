import os
import google.generativeai as genai
import streamlit as st

from PyPDF2 import PdfReader
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv() ## load all our environment variables

def get_gemini_pro():
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  return genai.GenerativeModel('gemini-pro')

def pdf_to_text(pdf_file):
  reader = PdfReader(pdf_file)
  text = ''
  for page in reader.pages:
    text += str(page.extract_text())
  return text

def construct_skills_prompt(resume, job_description):
  skill_prompt = '''Act as a HR Manager with 20 years of experience.
  Compare the resume provided below with the job description given below.
  Check for key skills in the resume that are related to the job description.
  List the missing key skillset from the resume.
  I just need the extracted missing skillset.
  Here is the Resume text: {resume}
  Here is the Job Description: {job_description}

  I want the response as a list of missing skill word'''.format(resume=resume, job_description=job_description)

  return skill_prompt

def construct_resume_score_prompt(resume, job_description):
  resume_score_prompt = '''Act as a HR Manager with 20 years of experience.
  Compare the resume provided below with the job description given below.
  Check for key skills in the resume that are related to the job description.
  Rate the resume out of 100 based on the matching skill set.
  Assess the score with high accuracy.
  Here is the Resume text: {resume}
  Here is the Job Description: {job_description}

  I want the response as a single string in the following structure score:%'''.format(resume=resume, job_description=job_description)

  return resume_score_prompt

def get_result(input):
  model = get_gemini_pro()
  response = model.generate_content(input)
  return response.text

st.set_page_config(page_title='ATS Scanner', page_icon=':technologist:', layout='wide')

st.title('ATS Tracker Tool')

job_description = ''
with st.container(border=True):
  col1, col2 = st.columns([1,1])
  job_description = col1.text_area('Enter the Job Description')
  uploaded_file = col2.file_uploader('Upload Your Resume', type=['pdf'])

with st.sidebar:
  selected = option_menu(
    menu_title=None,
    options=['🧑‍💻Score Checker', '🕵Skill Checker'],
    icons=['bi-clipboard2-data', 'hash']
  )

if selected == '🧑‍💻Score Checker':
  submit = st.button('Get Score')

  if submit:
    if job_description == '':
      st.error('Enter Job Description')
    elif uploaded_file is None:
      st.error('Upload your Resume')
    else:
      try:
        resume = pdf_to_text(uploaded_file)
        score_prompt = construct_resume_score_prompt(resume, job_description)
        result = get_result(score_prompt)
        final_result = result.split(":")[1]
        print(final_result)
        if '%' not in final_result:
          final_result = final_result + '%'
        result_str = f"""
        <style>
        p.a {{
          font: bold 25px Arial;
        }}
        </style>
        <p class="a">Your Resume matches {final_result} with the Job Description</p>
      """
        st.markdown(result_str, unsafe_allow_html=True)
      except Exception as e:
        print(f'{type(e).__name__}: {e}')

elif selected == '🕵Skill Checker':
    submit = st.button('Get Missing Skills')
    if submit:
      if job_description == '':
        st.error('Enter Job Description')
      elif uploaded_file is None:
        st.error('Upload your Resume')
      else:
        try:
          resume = pdf_to_text(uploaded_file)
          skil_prompt = construct_skills_prompt(resume, job_description)
          result = get_result(skil_prompt)
          st.write('Your Resume misses the following keywords:')
          st.markdown(result, unsafe_allow_html=True)
        except Exception as e:
          print(f'{type(e).__name__}: {e}')
