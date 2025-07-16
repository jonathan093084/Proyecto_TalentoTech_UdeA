# resumen_visual.py

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

# Cargar datos
df = pd.read_csv("diversified_job_postings_version0.csv")
df['posting_date'] = pd.to_datetime(df['posting_date'], errors='coerce')
df['application_deadline'] = pd.to_datetime(df['application_deadline'], errors='coerce')
df['application_duration_days'] = (df['application_deadline'] - df['posting_date']).dt.days

df['experience_level'] = df['experience_level'].replace({"SE": "Expert", "MI": "Intermediate", "EN": "Junior", "EX": "Director"})
df['employment_type'] = df['employment_type'].replace({"FT": "Full-time", "PT": "Part-time", "CT": "Contract", "FL": "Freelance"})
df['company_size'] = df['company_size'].replace({"S": "Small", "M": "Medium", "L": "Large"})
df['remote_ratio'] = df['remote_ratio'].replace({0: 'No remote', 50: 'Hybrid', 100: 'Fully remote'})
df['required_skills'] = df['required_skills'].fillna('').apply(lambda x: [s.strip() for s in x.split(',') if s.strip()])

# Controles interactivos
st.sidebar.header("Filtros")
selected_year = st.sidebar.selectbox("Año", options=sorted(df['posting_date'].dt.year.dropna().unique()))
selected_country = st.sidebar.selectbox("País de la empresa", options=['Todos'] + sorted(df['company_location'].unique()))
selected_employment = st.sidebar.selectbox("Tipo de empleo", options=['Todos'] + sorted(df['employment_type'].unique()))
selected_experience = st.sidebar.selectbox("Nivel de experiencia", options=['Todos'] + sorted(df['experience_level'].unique()))
selected_industry = st.sidebar.selectbox("Industria", options=['Todos'] + sorted(df['industry'].dropna().unique()))
selected_remote = st.sidebar.selectbox("Modalidad de trabajo", options=['Todos'] + sorted(df['remote_ratio'].dropna().unique()))

# Aplicar filtros
df_filtered = df[df['posting_date'].dt.year == selected_year]
if selected_country != 'Todos':
    df_filtered = df_filtered[df_filtered['company_location'] == selected_country]
if selected_employment != 'Todos':
    df_filtered = df_filtered[df_filtered['employment_type'] == selected_employment]
if selected_experience != 'Todos':
    df_filtered = df_filtered[df_filtered['experience_level'] == selected_experience]
if selected_industry != 'Todos':
    df_filtered = df_filtered[df_filtered['industry'] == selected_industry]
if selected_remote != 'Todos':
    df_filtered = df_filtered[df_filtered['remote_ratio'] == selected_remote]

# ----------- ANALISIS POR CLUSTER (KMEANS) -----------
st.header("Análisis por Clúster (KMeans)")

# Codificar variables categóricas ordinales
size_map = {"Small": 0, "Medium": 1, "Large": 2}
experience_map = {"Junior": 0, "Intermediate": 1, "Expert": 2, "Director": 3}
remote_map = {"No remote": 0, "Hybrid": 1, "Fully remote": 2}

df_cluster = df_filtered.copy()
df_cluster = df_cluster.dropna(subset=['salary_usd', 'years_experience', 'company_size', 'experience_level', 'remote_ratio', 'benefits_score'])
df_cluster['company_size_code'] = df_cluster['company_size'].map(size_map)
df_cluster['experience_level_code'] = df_cluster['experience_level'].map(experience_map)
df_cluster['remote_ratio_code'] = df_cluster['remote_ratio'].map(remote_map)

# Selección de variables para clustering
features = ['salary_usd', 'years_experience', 'company_size_code', 'experience_level_code', 'remote_ratio_code', 'benefits_score']
X = df_cluster[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Selección de número de clusters
k = st.slider("Selecciona el número de clústeres", 2, 10, 3)
kmeans = KMeans(n_clusters=k, random_state=42)
df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

# Gráfico de dispersión 2D
fig_cluster = px.scatter(
    df_cluster,
    x='salary_usd',
    y='years_experience',
    color='cluster',
    title='Clustering de ofertas: Salario vs. Años de experiencia',
    labels={'salary_usd': 'Salario (USD)', 'years_experience': 'Años de experiencia'},
    hover_data=['employment_type', 'company_location']
)
st.plotly_chart(fig_cluster)

# Mostrar tabla de centroides
centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=features)
centroids['cluster'] = centroids.index
st.subheader("Centroides de los clústeres")
st.dataframe(centroids.round(2))

# Análisis textual de los clústeres
st.subheader("Resumen interpretativo de los clústeres")
for _, row in centroids.iterrows():
    cluster_id = int(row['cluster'])
    salario = row['salary_usd']
    experiencia = row['years_experience']
    remote = row['remote_ratio_code']
    resumen = f"\n**Clúster {cluster_id}:** "
    if salario > centroids['salary_usd'].mean():
        resumen += "salarios **altos**, "
    else:
        resumen += "salarios **moderados o bajos**, "
    if experiencia > centroids['years_experience'].mean():
        resumen += "experiencia **alta**, "
    else:
        resumen += "experiencia **baja o media**, "
    if remote == 2:
        resumen += "predomina el trabajo **totalmente remoto**."
    elif remote == 1:
        resumen += "predomina el trabajo **híbrido**."
    else:
        resumen += "predomina el trabajo **presencial**."
    st.markdown(resumen)
