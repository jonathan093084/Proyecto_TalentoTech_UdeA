# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv("diversified_job_postings.csv")
df['posting_date'] = pd.to_datetime(df['posting_date'], errors='coerce')
df['application_deadline'] = pd.to_datetime(df['application_deadline'], errors='coerce')
df['application_duration_days'] = (df['application_deadline'] - df['posting_date']).dt.days

df['experience_level'] = df['experience_level'].replace({"SE": "Expert", "MI": "Intermediate", "EN": "Junior", "EX": "Director"})
df['employment_type'] = df['employment_type'].replace({"FT": "Full-time", "PT": "Part-time", "CT": "Contract", "FL": "Freelance"})
df['company_size'] = df['company_size'].replace({"S": "Small", "M": "Medium", "L": "Large"})
df['remote_ratio'] = df['remote_ratio'].replace({0: 'No remote', 50: 'Hybrid', 100: 'Fully remote'})
df['required_skills'] = df['required_skills'].fillna('').apply(lambda x: [s.strip() for s in x.split(',') if s.strip()])

# Sidebar de navegación
st.sidebar.title("Explorador de Empleos en IA")
seccion = st.sidebar.radio("Selecciona una secci\u00f3n:", (
    "Compensaci\u00f3n y Salarios",
    "An\u00e1lisis Geogr\u00e1fico",
    "Tendencias del Mercado",
    "Habilidades Demandadas",
    "Duraci\u00f3n del Proceso"
))

# COMPENSACION
if seccion == "Compensaci\u00f3n y Salarios":
    st.header("Salario promedio por nivel de experiencia")
    salary_exp = df.groupby('experience_level')['salary_usd'].mean().reset_index()
    fig = px.bar(salary_exp, x='experience_level', y='salary_usd', text='salary_usd')
    st.plotly_chart(fig)

    st.header("Salario promedio por tama\u00f1o de empresa")
    salary_size = df.groupby('company_size')['salary_usd'].mean().reset_index()
    fig2 = px.bar(salary_size, x='company_size', y='salary_usd', text='salary_usd')
    st.plotly_chart(fig2)

# GEOGRAFIA
elif seccion == "An\u00e1lisis Geogr\u00e1fico":
    st.header("Empresas contratantes por pa\u00eds")
    top_companies = df['company_location'].value_counts().head(15).reset_index()
    top_companies.columns = ['Pa\u00eds', 'Empresas']
    fig = px.bar(top_companies, x='Pa\u00eds', y='Empresas', text='Empresas')
    st.plotly_chart(fig)

    st.header("Residencia de los empleados")
    top_residence = df['employee_residence'].value_counts().head(15).reset_index()
    top_residence.columns = ['Pa\u00eds', 'Empleados']
    fig2 = px.bar(top_residence, x='Pa\u00eds', y='Empleados', text='Empleados')
    st.plotly_chart(fig2)

# TENDENCIAS
elif seccion == "Tendencias del Mercado":
    st.header("Evoluci\u00f3n mensual de publicaciones")
    trend = df.groupby(df['posting_date'].dt.to_period('M')).size().reset_index(name='num_postings')
    trend['posting_date'] = trend['posting_date'].dt.to_timestamp()
    fig = px.line(trend, x='posting_date', y='num_postings', markers=True)
    st.plotly_chart(fig)

    st.header("Modalidad remota a lo largo del tiempo")
    remote_trend = df.groupby([df['posting_date'].dt.to_period('M'), 'remote_ratio']).size().reset_index(name='num_offers')
    remote_trend['posting_date'] = remote_trend['posting_date'].dt.to_timestamp()
    fig2 = px.line(remote_trend, x='posting_date', y='num_offers', color='remote_ratio', markers=True)
    st.plotly_chart(fig2)

# HABILIDADES
elif seccion == "Habilidades Demandadas":
    st.header("Top 10 habilidades m\u00e1s demandadas")
    skills = df.explode('required_skills')
    top_skills = skills['required_skills'].value_counts().head(10).reset_index()
    top_skills.columns = ['Habilidad', 'Frecuencia']
    fig = px.pie(top_skills, names='Habilidad', values='Frecuencia')
    st.plotly_chart(fig)

# DURACION DEL PROCESO
elif seccion == "Duraci\u00f3n del Proceso":
    st.header("Duraci\u00f3n promedio entre publicaci\u00f3n y fecha l\u00edmite")
    duracion = df.groupby(df['posting_date'].dt.to_period('M'))['application_duration_days'].mean().reset_index()
    duracion['posting_date'] = duracion['posting_date'].dt.to_timestamp()
    fig = px.line(duracion, x='posting_date', y='application_duration_days', markers=True)
    st.plotly_chart(fig)
