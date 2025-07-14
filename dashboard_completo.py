# resumen_visual_dashboard_final.py

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Cargar datos y limpieza
@st.cache_data
def load_data():
    df = pd.read_csv("diversified_job_postings.csv")
    df['posting_date'] = pd.to_datetime(df['posting_date'], errors='coerce')
    df['application_deadline'] = pd.to_datetime(df['application_deadline'], errors='coerce')
    df['application_duration_days'] = (df['application_deadline'] - df['posting_date']).dt.days
    df['experience_level'] = df['experience_level'].replace({"SE": "Expert", "MI": "Intermediate", "EN": "Junior", "EX": "Director"})
    df['employment_type'] = df['employment_type'].replace({"FT": "Full-time", "PT": "Part-time", "CT": "Contract", "FL": "Freelance"})
    df['company_size'] = df['company_size'].replace({"S": "Small", "M": "Medium", "L": "Large"})
    df['remote_ratio'] = df['remote_ratio'].replace({0: 'No remote', 50: 'Hybrid', 100: 'Fully remote'})
    df['required_skills'] = df['required_skills'].fillna('').apply(lambda x: [s.strip() for s in x.split(',') if s.strip()])
    return df

df = load_data()

# Filtros
st.sidebar.title("Filtros del Dashboard")
selected_year = st.sidebar.selectbox("Año", sorted(df['posting_date'].dt.year.dropna().unique()))
selected_country = st.sidebar.selectbox("País de la empresa", ['Todos'] + sorted(df['company_location'].dropna().unique()))
selected_employment = st.sidebar.selectbox("Tipo de empleo", ['Todos'] + sorted(df['employment_type'].dropna().unique()))
selected_experience = st.sidebar.selectbox("Nivel de experiencia", ['Todos'] + sorted(df['experience_level'].dropna().unique()))
selected_industry = st.sidebar.selectbox("Industria", ['Todos'] + sorted(df['industry'].dropna().unique()))
selected_remote = st.sidebar.selectbox("Modalidad de trabajo", ['Todos'] + sorted(df['remote_ratio'].dropna().unique()))

# Aplicar filtros
df_filtered = df[df['posting_date'].dt.year == selected_year].copy()
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

# Secciones del análisis
def seccion_titulo(nombre):
    st.markdown(f"## {nombre}")

# Pregunta 1: Países con mayores salarios promedio
seccion_titulo("1. Países con mayores salarios promedio")
salary_country = df_filtered.groupby('company_location')['salary_usd'].mean().sort_values(ascending=False).reset_index()
fig1 = px.bar(salary_country.head(10), x='company_location', y='salary_usd', text='salary_usd')
st.plotly_chart(fig1)

# Pregunta 2: Salario promedio por nivel de experiencia
seccion_titulo("2. Salario promedio por nivel de experiencia")
salary_exp = df_filtered.groupby('experience_level')['salary_usd'].mean().reset_index()
fig2 = px.bar(salary_exp, x='experience_level', y='salary_usd', text='salary_usd')
st.plotly_chart(fig2)

# Pregunta 3: Salario vs tamaño de empresa
seccion_titulo("3. Salario promedio por tamaño de empresa")
salary_size = df_filtered.groupby('company_size')['salary_usd'].mean().reset_index()
fig3 = px.bar(salary_size, x='company_size', y='salary_usd', text='salary_usd')
st.plotly_chart(fig3)

# Pregunta 4: Salario por tipo de rol
seccion_titulo("4. Salario por categoría de trabajo")
salary_role = df_filtered.groupby('job_title')['salary_usd'].mean().sort_values(ascending=False).reset_index().head(10)
fig4 = px.bar(salary_role, x='job_title', y='salary_usd', text='salary_usd')
st.plotly_chart(fig4)

# Pregunta 5: Salario por tipo de empleo
seccion_titulo("5. Diferencias salariales por tipo de empleo")
salary_emp = df_filtered.groupby('employment_type')['salary_usd'].mean().reset_index()
fig5 = px.bar(salary_emp, x='employment_type', y='salary_usd', text='salary_usd')
st.plotly_chart(fig5)

# Pregunta 6: Relación entre trabajo remoto y salario
seccion_titulo("6. Relación entre modalidad remota y salario")
salary_remote = df_filtered.groupby('remote_ratio')['salary_usd'].mean().reset_index()
fig6 = px.bar(salary_remote, x='remote_ratio', y='salary_usd', text='salary_usd')
st.plotly_chart(fig6)

# Pregunta 7: Industrias con mejor pago
seccion_titulo("7. Industrias con mejores salarios")
salary_ind = df_filtered.groupby('industry')['salary_usd'].mean().sort_values(ascending=False).reset_index().head(10)
fig7 = px.bar(salary_ind, x='industry', y='salary_usd', text='salary_usd')
st.plotly_chart(fig7)

# Pregunta 8: Países con más ofertas
seccion_titulo("8. Países con mayor número de ofertas")
job_count = df_filtered['company_location'].value_counts().reset_index()
job_count.columns = ['País', 'Ofertas']
fig8 = px.bar(job_count.head(15), x='País', y='Ofertas', text='Ofertas')
st.plotly_chart(fig8)

# Pregunta 13: Evolución de ofertas
seccion_titulo("13. Evolución de publicaciones en IA")
trend = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M')).size().reset_index(name='num_postings')
trend['posting_date'] = trend['posting_date'].dt.to_timestamp()
fig13 = px.line(trend, x='posting_date', y='num_postings', markers=True)
st.plotly_chart(fig13)

# Pregunta 14: Picos por mes en 2024
seccion_titulo("14. Picos de publicación por mes (2024)")
df_2024 = df[df['posting_date'].dt.year == 2024]
df_2024['posting_month'] = df_2024['posting_date'].dt.month_name()
month_counts = df_2024['posting_month'].value_counts().reset_index()
month_counts.columns = ['Mes', 'Publicaciones']
fig14 = px.bar(month_counts.sort_values(by='Publicaciones', ascending=False), x='Mes', y='Publicaciones', text='Publicaciones')
st.plotly_chart(fig14)

# Pregunta 15: Evolución del trabajo remoto
seccion_titulo("15. Evolución del trabajo remoto")
remote_trend = df_filtered.groupby([df_filtered['posting_date'].dt.to_period('M'), 'remote_ratio']).size().reset_index(name='num_offers')
remote_trend['posting_date'] = remote_trend['posting_date'].dt.to_timestamp()
fig15 = px.line(remote_trend, x='posting_date', y='num_offers', color='remote_ratio', markers=True)
st.plotly_chart(fig15)

# Pregunta 16: Duración entre publicación y cierre
seccion_titulo("16. Duración entre publicación y fecha límite")
duration = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M'))['application_duration_days'].mean().reset_index()
duration['posting_date'] = duration['posting_date'].dt.to_timestamp()
fig16 = px.line(duration, x='posting_date', y='application_duration_days')
st.plotly_chart(fig16)

# Pregunta 17: Clustering con KMeans
seccion_titulo("17. Análisis de clúster (KMeans)")
df_cluster = df_filtered.dropna(subset=['salary_usd', 'company_size', 'experience_level', 'remote_ratio']).copy()
df_cluster['company_size_code'] = df_cluster['company_size'].map({"Small": 0, "Medium": 1, "Large": 2})
df_cluster['experience_level_code'] = df_cluster['experience_level'].map({"Junior": 0, "Intermediate": 1, "Expert": 2, "Director": 3})
df_cluster['remote_ratio_code'] = df_cluster['remote_ratio'].map({"No remote": 0, "Hybrid": 1, "Fully remote": 2})

features = ['salary_usd', 'company_size_code', 'experience_level_code', 'remote_ratio_code']
X = df_cluster[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
k = st.slider("Selecciona número de clústeres", 2, 10, 3)
kmeans = KMeans(n_clusters=k, random_state=42)
df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

fig17 = px.scatter(df_cluster, x='salary_usd', y='company_size_code', color='cluster',
                   hover_data=['company_location', 'experience_level'],
                   title="Clustering: Salario vs Tamaño de empresa")
st.plotly_chart(fig17)

centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=features)
centroids['cluster'] = centroids.index
st.dataframe(centroids.round(2))
