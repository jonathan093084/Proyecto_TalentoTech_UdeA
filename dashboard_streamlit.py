import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Agrego Cache para que mantenga los datos en memoria.
# Defino funcion para cargar y limpiar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("diversified_job_postings_version0.csv")
    # Limpieza y transformación
    df = df.drop('job_description_length', axis=1, errors='ignore')
    df['posting_date'] = pd.to_datetime(df['posting_date'], errors='coerce')
    df['application_deadline'] = pd.to_datetime(df['application_deadline'], errors='coerce')
    df['salary_usd'] = pd.to_numeric(df['salary_usd'], errors='coerce')
    df['application_duration_days'] = (df['application_deadline'] - df['posting_date']).dt.days
    df['required_skills'] = df['required_skills'].fillna('').apply(lambda x: [s.strip() for s in x.split(',') if s.strip()])
   
    experience_map = {"SE": "Expert", "MI": "Intermediate", "EN": "Junior", "EX": "Director"}
    df['experience_level'] = df['experience_level'].astype(str).str.strip().replace(experience_map).astype('category')
    
    employment_map = {"PT": "Part-time", "FT": "Full-time", "CT": "Contract", "FL": "Freelance"}
    df['employment_type'] = df['employment_type'].astype(str).str.strip().replace(employment_map).astype('category')
    
    size_map = {"S": "Small", "M": "Medium", "L": "Large"}
    df['company_size'] = df['company_size'].astype(str).str.strip().replace(size_map).astype('category')
    
    remote_map = {0: 'No remote', 50: 'Hybrid', 100: 'Fully remote'}
    df['remote_ratio'] = df['remote_ratio'].replace(remote_map).astype('category')
    
    cat_cols = ['job_title', 'experience_level', 'employment_type', 'company_location', 'company_size', 'employee_residence', 'remote_ratio', 'education_required', 'industry']
    df[cat_cols] = df[cat_cols].astype('category')
    return df

#Cargo el dataframe con los datos
df = load_data()

# Creo las categorias del Sidebar principal de navegación con las opciones definidas que vamos a mostrar
st.sidebar.title("Explorador de Empleos en IA")
seccion = st.sidebar.radio("Selecciona una sección:", (
    "Compensación y Salarios",
    "Educación",
    "Análisis Geográfico",
    "Tendencias del Mercado",
    "Habilidades Demandadas",
    "Duración del Proceso"
))

# Defino los filtros en el Sidebar 
st.sidebar.header("Filtros")
company_size_options = ['Todos'] + list(df["company_size"].unique())
education_required_options = ['Todos'] + list(df["education_required"].unique())
industry_options = ['Todos'] + list(df["industry"].unique())
employment_type_options = ['Todos'] + list(df["employment_type"].unique())
experience_level_options = ['Todos'] + list(df["experience_level"].unique())

#Creo los selectbox para los filtros 
company_size = st.sidebar.selectbox("Tamaño de compañía", options=company_size_options)
education_required = st.sidebar.selectbox("Nivel de educación", options=education_required_options)
industry = st.sidebar.selectbox("Industria", options=industry_options)
employment_type = st.sidebar.selectbox("Tipo de empleo", options=employment_type_options)
experience_level = st.sidebar.selectbox("Nivel de experiencia", options=experience_level_options)

# Aplicar filtros
df_filtered = df.copy()
if company_size != 'Todos':
    df_filtered = df_filtered[df_filtered["company_size"] == company_size]
if education_required != 'Todos':
    df_filtered = df_filtered[df_filtered["education_required"] == education_required]
if industry != 'Todos':
    df_filtered = df_filtered[df_filtered["industry"] == industry]
if employment_type != 'Todos':
    df_filtered = df_filtered[df_filtered["employment_type"] == employment_type]
if experience_level != 'Todos':
    df_filtered = df_filtered[df_filtered["experience_level"] == experience_level]

st.title("Dashboard de Empleos IA")
st.markdown("---")
# KPIs principales
#col1, col2, col3, col4 = st.columns(4)
#salario_promedio = df_filtered['salary_usd'].mean()
#num_ofertas = len(df_filtered)
#top_pais = df_filtered['company_location'].value_counts().idxmax() if not df_filtered.empty else '-'
#num_industrias = df_filtered['industry'].nunique()
#col1.metric("Salario Promedio (USD)", f"{salario_promedio:,.0f}")
#col2.metric("Ofertas Totales", f"{num_ofertas}")
#col3.metric("País con más ofertas", f"{top_pais}")
#col4.metric("Industrias únicas", f"{num_industrias}")
#st.markdown("---")

# Mostrar contenido según la sección seleccionada
if seccion == "Compensación y Salarios":
    
    st.markdown("---")
    # KPIs sección Compensación y Salarios
    col1, col2, col3, col4 = st.columns(4)
    salario_max = df_filtered['salary_usd'].max()
    salario_min = df_filtered['salary_usd'].min()
    salario_mediana = df_filtered['salary_usd'].median()
    salario_std = df_filtered['salary_usd'].std()
    col1.metric("Salario Máximo (USD)", f"{salario_max:,.0f}")
    col2.metric("Salario Mínimo (USD)", f"{salario_min:,.0f}")
    col3.metric("Mediana Salarial (USD)", f"{salario_mediana:,.0f}")
    col4.metric("Desviación estándar", f"{salario_std:,.0f}")
    st.markdown("---")
    st.subheader("Top 10 países con mayores salarios promedio")
    top_salaries_by_country = df_filtered.groupby('company_location')['salary_usd'].mean().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(
        top_salaries_by_country,
        x='company_location',
        y='salary_usd',
        title='Top 10 Ubicación de compañias con salarios promedio más altos de empleos IA',
        labels={'company_location': 'Compañias x País', 'salary_usd': 'Salario Promedio (USD)'},
        text='salary_usd',
        color='company_location',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio por nivel de experiencia")
    salary_by_experience = df_filtered.groupby('experience_level')['salary_usd'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        salary_by_experience,
        x='experience_level',
        y='salary_usd',
        title='Salario promedio según nivel de experiencia',
        labels={'experience_level': 'Nivel de experiencia','salary_usd': 'Salario Promedio (USD)'},
        text='salary_usd',
        color='experience_level',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio por tamaño de empresa")
    salary_by_company_size = df_filtered.groupby('company_size')['salary_usd'].mean().sort_values(ascending=False).reset_index()
    fig_size = px.bar(
        salary_by_company_size,
        x='company_size',
        y='salary_usd',
        title='Salario promedio según tamaño de empresa',
        labels={'company_size': 'Tamaño de la empresa','salary_usd': 'Salario Promedio (USD)'},
        text='salary_usd',
        color='company_size',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_size.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_size.update_layout(xaxis={'categoryorder': 'total descending'},xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig_size, use_container_width=True)

    st.markdown("---")
    st.subheader("Top 15 cargos con mayores salarios")
    top_roles_by_salary = df_filtered.groupby('job_title')['salary_usd'].mean().sort_values(ascending=False).head(15).reset_index()
    fig_roles = px.bar(
        top_roles_by_salary,
        x='salary_usd',
        y='job_title',
        orientation='h',
        title='Top 15 Trabajos con mayores salarios en IA',
        labels={'job_title': 'Categoría de trabajo', 'salary_usd': 'Salario Promedio (USD)'},
        text='salary_usd',
        color='salary_usd',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_roles.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_roles.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True)
    st.plotly_chart(fig_roles, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio por tipo de empleo")
    salary_by_employment = df_filtered.groupby('employment_type')['salary_usd'].mean().sort_values(ascending=False).reset_index()
    fig_employment = px.bar(
        salary_by_employment,
        x='employment_type',
        y='salary_usd',
        title='Salario promedio según tipo de empleo',
        labels={'employment_type': 'Tipo de empleo', 'salary_usd': 'Salario Promedio (USD)'},
        text='salary_usd',
        color='employment_type',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_employment.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_employment.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig_employment, use_container_width=True)

    st.markdown("---")
    st.subheader("Top 15 industrias con mayores salarios")
    salary_by_industry = df_filtered.groupby('industry')['salary_usd'].mean().sort_values(ascending=False).head(15).reset_index()
    fig = px.bar(
        salary_by_industry,
        x='salary_usd',
        y='industry',
        orientation='h',
        color='salary_usd',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Top 15 industrias con mayores salarios',
        labels={'industry': 'Industria', 'salary_usd': 'Salario promedio (USD)'}
    )
    fig.update_traces(texttemplate='%{x:.2f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio por nivel de educación")
    salary_by_education = df_filtered.groupby('education_required')['salary_usd'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        salary_by_education,
        x='education_required',
        y='salary_usd',
        color='education_required',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Salario promedio por nivel de educación',
        labels={'education_required': 'Nivel de Educación', 'salary_usd': 'Salario promedio (USD)'}
    )
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Boxplot: Salario por nivel de experiencia")
    fig = px.box(
        df_filtered,
        x='experience_level',
        y='salary_usd',
        color='experience_level',
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Distribución del salario por nivel de experiencia',
        labels={'experience_level': 'Nivel de experiencia', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
   
    st.markdown("---")  
    st.subheader("Boxplot: Salario por nivel de educación")
    fig = px.box(
        df_filtered,
        x='education_required',
        y='salary_usd',
        color='education_required',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Distribución del salario por nivel de educación',
        labels={'education_required': 'Nivel de educación', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Boxplot: Salario por industria (top 10)")
    top_industries = df_filtered['industry'].value_counts().head(10).index
    df_top_industries = df_filtered[df_filtered['industry'].isin(top_industries)]
    fig = px.box(
        df_top_industries,
        x='industry',
        y='salary_usd',
        color='industry',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Distribución del salario por industria (Top 10)',
        labels={'industry': 'Industria', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
   
    st.markdown("---")
    st.subheader("Boxplot: Salario por tamaño de empresa")
    fig = px.box(
        df_filtered,
        x='company_size',
        y='salary_usd',
        color='company_size',
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Distribución del salario por tamaño de empresa',
        labels={'company_size': 'Tamaño de empresa', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
   
    st.markdown("---")
    st.subheader("Boxplot: Salario por años de experiencia")
    fig = px.box(
        df_filtered,
        x='years_experience',
        y='salary_usd',
        color='years_experience',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Distribución del salario por años de experiencia',
        labels={'years_experience': 'Años de experiencia', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
   
    st.markdown("---")
    st.subheader("Boxplot: Salario por cargo (top 10)")
    top_jobs = df_filtered['job_title'].value_counts().head(10).index
    df_top_jobs = df_filtered[df_filtered['job_title'].isin(top_jobs)]
    fig = px.box(
        df_top_jobs,
        x='job_title',
        y='salary_usd',
        color='job_title',
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Distribución del salario por cargo (Top 10)',
        labels={'job_title': 'Cargo', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Gráfico de burbujas: salario promedio por industria y tamaño de empresa")
    bubble_data = df_filtered.groupby(['industry', 'company_size'])['salary_usd'].mean().reset_index()
    fig = px.scatter(
        bubble_data,
        x='industry',
        y='company_size',
        size='salary_usd',
        color='salary_usd',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Salario promedio por industria y tamaño de empresa',
        labels={'industry': 'Industria', 'company_size': 'Tamaño de empresa', 'salary_usd': 'Salario promedio (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Histograma de salarios")
    fig = px.histogram(
        df_filtered,
        x='salary_usd',
        nbins=30,
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Distribución de salarios',
        labels={'salary_usd': 'Salario (USD)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Matriz de correlación de variables numéricas")
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64'])
    corr_matrix = numeric_cols.corr()
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='Plasma',
        aspect='auto',
        title='Matriz de correlación de variables numéricas',
        labels={col: col for col in corr_matrix.columns}
    )
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Educación":
    st.markdown("---")
    # KPIs sección Educación
    col1, col2, col3, col4 = st.columns(4)
    num_niveles = df_filtered['education_required'].nunique()
    nivel_top = df_filtered['education_required'].value_counts().idxmax() if not df_filtered.empty else '-'
    salario_top_edu = df_filtered.groupby('education_required')['salary_usd'].mean().sort_values(ascending=False).iloc[0] if num_niveles > 0 else 0
    salario_min_edu = df_filtered.groupby('education_required')['salary_usd'].mean().sort_values().iloc[0] if num_niveles > 0 else 0
    col1.metric("Niveles educativos únicos", f"{num_niveles}")
    col2.metric("Nivel más frecuente", f"{nivel_top}")
    col3.metric("Salario promedio más alto", f"{salario_top_edu:,.0f}")
    col4.metric("Salario promedio más bajo", f"{salario_min_edu:,.0f}")
    st.markdown("---")
    st.subheader("Salario promedio por nivel de educación")
    salary_by_education = df_filtered.groupby('education_required')['salary_usd'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        salary_by_education,
        x='education_required',
        y='salary_usd',
        color='education_required',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Salario promedio por nivel de educación',
        labels={'education_required': 'Nivel de Educación', 'salary_usd': 'Salario promedio (USD)'},
        text='salary_usd'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Boxplot: Salario por nivel de educación")
    fig = px.box(
        df_filtered,
        x='education_required',
        y='salary_usd',
        color='education_required',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Distribución del salario por nivel de educación',
        labels={'education_required': 'Nivel de educación', 'salary_usd': 'Salario (USD)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio por nivel de educación y cargo (Top 10 cargos)")
    education_by_job = df_filtered.groupby(['job_title', 'education_required'])['salary_usd'].mean().reset_index(name='avg_salary')
    top_jobs = df_filtered['job_title'].value_counts().head(10).index
    filtered_data = education_by_job[education_by_job['job_title'].isin(top_jobs)]
    custom_colors = [px.colors.sequential.Viridis[6], px.colors.sequential.Viridis[9], px.colors.sequential.Viridis[3], px.colors.sequential.Viridis[7]]
    fig = px.bar(
        filtered_data,
        x='job_title',
        y='avg_salary',
        color='education_required',
        barmode='group',
        color_discrete_sequence=custom_colors,
        text='avg_salary',
        title='Salario promedio por nivel de educación y cargo',
        labels={'job_title': 'Cargo', 'avg_salary': 'Salario promedio (USD)', 'education_required': 'Nivel Educativo'}
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_tickangle=-45, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Salario promedio y mediano por nivel de educación")
    salary_stats = df_filtered.groupby('education_required')['salary_usd'].agg(['mean', 'median', 'count']).reset_index()
    salary_stats = salary_stats.sort_values('mean', ascending=False)
    viridis_colors = px.colors.sequential.Viridis
    color_media = viridis_colors[4]
    color_mediana = viridis_colors[5]
    fig_stats = go.Figure()
    fig_stats.add_trace(go.Bar(
        x=salary_stats['education_required'],
        y=salary_stats['mean'],
        name='Media',
        marker_color=color_media,
        text=[f'{x:.2f}' for x in salary_stats['mean']],
        textposition='outside',
    ))
    fig_stats.add_trace(go.Bar(
        x=salary_stats['education_required'],
        y=salary_stats['median'],
        name='Mediana',
        marker_color=color_mediana,
        text=[f'{x:.2f}' for x in salary_stats['median']],
        textposition='outside',
    ))
    fig_stats.update_layout(
        title='Salario promedio y mediano por nivel de educación',
        xaxis=dict(title='Nivel de Educación', tickangle=-45),
        yaxis=dict(title='Salario (USD)'),
        barmode='group',
        legend_title='Estadística',
        margin=dict(t=50, b=100),
        height=500
    )
    st.plotly_chart(fig_stats, use_container_width=True)

elif seccion == "Análisis Geográfico":
    
    st.markdown("---")
    # KPIs sección Análisis Geográfico
    col1, col2, col3, col4 = st.columns(4)
    num_paises = df_filtered['company_location'].nunique()
    pais_top = df_filtered['company_location'].value_counts().idxmax() if not df_filtered.empty else '-'
    num_empresas = df_filtered['company_location'].count()
    num_residencias = df_filtered['employee_residence'].nunique()
    col1.metric("Países únicos", f"{num_paises}")
    col2.metric("País con más ofertas", f"{pais_top}")
    col3.metric("Total empresas", f"{num_empresas}")
    col4.metric("Residencias únicas", f"{num_residencias}")
    st.markdown("---")
    st.subheader("Cantidad de ofertas por país (top 10)")
    offers_by_country = df_filtered['company_location'].value_counts().head(10).reset_index()
    offers_by_country.columns = ['company_location', 'Cantidad']
    fig = px.bar(
        offers_by_country,
        x='company_location',
        y='Cantidad',
        color='company_location',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Top 10 países con mayor cantidad de ofertas laborales en IA',
        labels={'company_location': 'País', 'Cantidad': 'Cantidad de ofertas'},
        text='Cantidad'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Cantidad de empresas por país")
    company_location_counts = df_filtered['company_location'].value_counts().reset_index()
    company_location_counts.columns = ['company_location', 'num_companies']
    fig = px.bar(
        company_location_counts,
        x='company_location',
        y='num_companies',
        color='company_location',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Ubicación de las compañías con empleos IA',
        labels={'company_location': 'País', 'num_companies': 'Cantidad de empresas'},
        text='num_companies'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Cantidad de empleados por país de residencia")
    residence_counts = df_filtered['employee_residence'].value_counts().reset_index()
    residence_counts.columns = ['employee_residence', 'num_employees']
    fig = px.bar(
        residence_counts,
        x='employee_residence',
        y='num_employees',
        color='employee_residence',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Países donde residen los empleados de IA',
        labels={'employee_residence': 'País de residencia', 'num_employees': 'Cantidad de empleados'},
        text='num_employees'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Relación empresa-residencia (burbujas)")
    location_relation = df_filtered.groupby(['company_location', 'employee_residence']).size().reset_index(name='num_matches')
    fig = px.scatter(
        location_relation,
        x='company_location',
        y='employee_residence',
        size='num_matches',
        color='num_matches',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Relación entre ubicación de la empresa y residencia del empleado',
        labels={'company_location': 'País empresa', 'employee_residence': 'País residencia', 'num_matches': 'Coincidencias'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribución de tipos de contrato por país (top 10)")
    contract_distribution = df_filtered.groupby(['company_location', 'employment_type']).size().reset_index(name='Cantidad')
    top_countries = contract_distribution.groupby('company_location')['Cantidad'].sum().sort_values(ascending=False).head(10).index
    contract_distribution_top10 = contract_distribution[contract_distribution['company_location'].isin(top_countries)]
    custom_colors = [px.colors.sequential.Viridis[6], px.colors.sequential.Viridis[9], px.colors.sequential.Viridis[3], px.colors.sequential.Viridis[7]]
    fig = px.bar(
        contract_distribution_top10,
        x='company_location',
        y='Cantidad',
        color='employment_type',
        color_discrete_sequence=custom_colors,
        title='Distribución de tipos de contrato por país',
        labels={'company_location': 'País', 'Cantidad': 'Cantidad de contratos', 'employment_type': 'Tipo de empleo'},
        text='Cantidad'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Distribución de trabajo remoto/híbrido por país")
    remote_distribution = df_filtered.groupby(['company_location', 'remote_ratio']).size().reset_index(name='Cantidad')
    fig = px.bar(
        remote_distribution,
        x='company_location',
        y='Cantidad',
        color='remote_ratio',
        color_discrete_sequence=custom_colors,
        title='Frecuencia del trabajo remoto o híbrido por país',
        labels={'company_location': 'País', 'Cantidad': 'Cantidad de ofertas', 'remote_ratio': 'Modalidad'},
        text='Cantidad'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Top habilidades más demandadas por país (barras)")
    skills_by_country = df_filtered.explode('required_skills')
    top_skills_global = skills_by_country['required_skills'].value_counts().reset_index()
    top_skills_global.columns = ['required_skills', 'count']
    fig = px.bar(
        top_skills_global,
        x='count',
        y='required_skills',
        orientation='h',
        color='count',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Top habilidades más demandadas en IA (global)',
        labels={'count': 'Cantidad de menciones', 'required_skills': 'Habilidad'},
        text='count'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Top habilidades más demandadas por país (burbujas)")
    skill_demand = skills_by_country.groupby(['company_location', 'required_skills']).size().reset_index(name='count')
    top_skills_by_country = skill_demand.sort_values('count', ascending=False)
    fig = px.scatter(
        top_skills_by_country,
        x='company_location',
        y='required_skills',
        size='count',
        color='count',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Top habilidades más demandadas por país',
        labels={'company_location': 'País', 'required_skills': 'Habilidad', 'count': 'Demanda'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Tendencias del Mercado":
    
    st.markdown("---")
    # KPIs sección Tendencias del Mercado
    col1, col2, col3, col4 = st.columns(4)
    fecha_min = df_filtered['posting_date'].min()
    fecha_max = df_filtered['posting_date'].max()
    total_postings = df_filtered['posting_date'].count()
    promedio_duracion = df_filtered['application_duration_days'].mean()
    col1.metric("Primera publicación", f"{fecha_min.date() if pd.notnull(fecha_min) else '-'}")
    col2.metric("Última publicación", f"{fecha_max.date() if pd.notnull(fecha_max) else '-'}")
    col3.metric("Total publicaciones", f"{total_postings}")
    col4.metric("Duración promedio (días)", f"{promedio_duracion:,.1f}")
    st.markdown("---")
    st.subheader("Evolución de publicaciones en IA")
    job_posting_trend = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M')).size().reset_index(name='num_postings')
    job_posting_trend['posting_date'] = job_posting_trend['posting_date'].dt.to_timestamp()
    fig = px.line(
        job_posting_trend,
        x='posting_date',
        y='num_postings',
        markers=True,
        title='Evolución de la oferta de empleo en IA a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'num_postings': 'Número de publicaciones'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Picos de publicación por mes en 2024")
    df_2024 = df_filtered[df_filtered['posting_date'].dt.year == 2024].copy()
    df_2024['posting_month'] = df_2024['posting_date'].dt.month_name()
    monthly_2024 = df_2024['posting_month'].value_counts().reset_index()
    monthly_2024.columns = ['month', 'num_postings']
    fig = px.bar(
        monthly_2024,
        x='month',
        y='num_postings',
        color='num_postings',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Picos de publicación de vacantes por mes en 2024',
        labels={'month': 'Mes', 'num_postings': 'Número de publicaciones'},
        text='num_postings'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Evolución de ofertas por modalidad remota")
    remote_trend = df_filtered.groupby([df_filtered['posting_date'].dt.to_period('M'), 'remote_ratio']).size().reset_index(name='num_offers')
    remote_trend['posting_date'] = remote_trend['posting_date'].dt.to_timestamp()
    fig = px.line(
        remote_trend,
        x='posting_date',
        y='num_offers',
        color='remote_ratio',
        markers=True,
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Evolución de las ofertas por modalidad de trabajo remoto a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'num_offers': 'Número de ofertas', 'remote_ratio': 'Modalidad'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Evolución de duración entre publicación y fecha límite")
    duration_trend = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M'))['application_duration_days'].mean().reset_index()
    duration_trend['posting_date'] = duration_trend['posting_date'].dt.to_timestamp()
    fig = px.line(
        duration_trend,
        x='posting_date',
        y='application_duration_days',
        markers=True,
        title='Duración promedio entre publicación y fecha límite a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'application_duration_days': 'Duración promedio (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Habilidades Demandadas":
    
    st.markdown("---")
    # KPIs sección Habilidades Demandadas
    col1, col2, col3, col4 = st.columns(4)
    num_habilidades = df_filtered.explode('required_skills')['required_skills'].nunique()
    habilidad_top = df_filtered.explode('required_skills')['required_skills'].value_counts().idxmax() if not df_filtered.empty else '-'
    salario_top_skill = df_filtered.explode('required_skills').groupby('required_skills')['salary_usd'].mean().sort_values(ascending=False).iloc[0] if num_habilidades > 0 else 0
    salario_min_skill = df_filtered.explode('required_skills').groupby('required_skills')['salary_usd'].mean().sort_values().iloc[0] if num_habilidades > 0 else 0
    col1.metric("Habilidades únicas", f"{num_habilidades}")
    col2.metric("Habilidad más frecuente", f"{habilidad_top}")
    col3.metric("Salario promedio más alto", f"{salario_top_skill:,.0f}")
    col4.metric("Salario promedio más bajo", f"{salario_min_skill:,.0f}")
    st.markdown("---")
    st.subheader("Top 20 habilidades con mayor salario promedio")
    skills_salary = df_filtered.explode('required_skills')
    salary_by_skill = skills_salary.groupby('required_skills')['salary_usd'].mean().reset_index()
    top_salary_skills = salary_by_skill.sort_values('salary_usd', ascending=False).head(20)
    fig = px.bar(
        top_salary_skills,
        x='salary_usd',
        y='required_skills',
        orientation='h',
        color='salary_usd',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Top 20 habilidades con mayor salario promedio',
        labels={'salary_usd': 'Salario promedio (USD)', 'required_skills': 'Habilidad'},
        text='salary_usd'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Top habilidades más demandadas (barras)")
    top_skills_global = skills_salary['required_skills'].value_counts().reset_index()
    top_skills_global.columns = ['required_skills', 'count']
    fig = px.bar(
        top_skills_global,
        x='count',
        y='required_skills',
        orientation='h',
        color='count',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Top habilidades más demandadas en IA (global)',
        labels={'count': 'Cantidad de menciones', 'required_skills': 'Habilidad'},
        text='count'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Top habilidades más demandadas (pie)")
    top_skills_pie = skills_salary['required_skills'].value_counts().head(10).reset_index()
    top_skills_pie.columns = ['required_skills', 'count']
    fig = px.pie(
        top_skills_pie,
        names='required_skills',
        values='count',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Top 10 habilidades más demandadas en IA (global)',
        labels={'required_skills': 'Habilidad', 'count': 'Cantidad'}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Mapa de calor de habilidades por industria")
    top_skills = skills_salary['required_skills'].value_counts().head(20).index
    heatmap_data = skills_salary[skills_salary['required_skills'].isin(top_skills)].groupby(['industry', 'required_skills']).size().reset_index(name='count')
    fig = px.density_heatmap(
        heatmap_data,
        x='industry',
        y='required_skills',
        z='count',
        color_continuous_scale=px.colors.sequential.Darkmint,
        title='Mapa de calor: demanda de habilidades por Industria',
        labels={'industry': 'Industria', 'required_skills': 'Habilidad', 'count': 'Demanda'}
    )
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Duración del Proceso":
    st.markdown("---")
    # KPIs sección Duración del Proceso
    col1, col2, col3, col4 = st.columns(4)
    duracion_max = df_filtered['application_duration_days'].max()
    duracion_min = df_filtered['application_duration_days'].min()
    duracion_mediana = df_filtered['application_duration_days'].median()
    duracion_std = df_filtered['application_duration_days'].std()
    col1.metric("Duración máxima (días)", f"{duracion_max:,.0f}")
    col2.metric("Duración mínima (días)", f"{duracion_min:,.0f}")
    col3.metric("Mediana duración (días)", f"{duracion_mediana:,.0f}")
    col4.metric("Desviación estándar", f"{duracion_std:,.0f}")
    st.markdown("---")
    st.subheader("Evolución de duración entre publicación y fecha límite")
    duration_trend = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M'))['application_duration_days'].mean().reset_index()
    duration_trend['posting_date'] = duration_trend['posting_date'].dt.to_timestamp()
    fig = px.line(
        duration_trend,
        x='posting_date',
        y='application_duration_days',
        markers=True,
        title='Duración promedio entre publicación y fecha límite a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'application_duration_days': 'Duración promedio (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribución de la duración del proceso de aplicación")
    fig = px.histogram(
        df_filtered,
        x='application_duration_days',
        nbins=30,
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Duración del proceso de aplicación (días)',
        labels={'application_duration_days': 'Duración (días)'}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Boxplot de duración por industria")
    fig = px.box(
        df_filtered,
        x='industry',
        y='application_duration_days',
        color='industry',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Duración del proceso por industria',
        labels={'industry': 'Industria', 'application_duration_days': 'Duración (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Boxplot de duración por cargo (top 10)")
    top_jobs = df_filtered['job_title'].value_counts().head(10).index
    df_top_jobs = df_filtered[df_filtered['job_title'].isin(top_jobs)]
    fig = px.box(
        df_top_jobs,
        x='job_title',
        y='application_duration_days',
        color='job_title',
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Duración del proceso por cargo (Top 10)',
        labels={'job_title': 'Cargo', 'application_duration_days': 'Duración (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Boxplot de duración por nivel de educación")
    fig = px.box(
        df_filtered,
        x='education_required',
        y='application_duration_days',
        color='education_required',
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Duración del proceso por nivel de educación',
        labels={'education_required': 'Nivel de educación', 'application_duration_days': 'Duración (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Duración promedio por tipo de empleo")
    duration_by_employment = df_filtered.groupby('employment_type')['application_duration_days'].mean().reset_index()
    fig = px.bar(
        duration_by_employment,
        x='employment_type',
        y='application_duration_days',
        color='employment_type',
        color_discrete_sequence=px.colors.sequential.Plasma,
        title='Duración promedio por tipo de empleo',
        labels={'employment_type': 'Tipo de empleo', 'application_duration_days': 'Duración promedio (días)'},
        text='application_duration_days'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

