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
st.sidebar.title("Secciones del Análisis")
seccion = st.sidebar.radio("Selecciona una sección:", (
    "Inicio",
    "Habilidades Demandadas",
    "Compensación y Salarios",
    "Análisis Geográfico",
    "Ofertas de Empleo"
))

# Defino los filtros en el Sidebar 
st.sidebar.header("Filtros")
company_size_options = ['Todos'] + list(df["company_size"].unique())
education_required_options = ['Todos'] + list(df["education_required"].unique())
industry_options = ['Todos'] + list(df["industry"].unique())
employment_type_options = ['Todos'] + list(df["employment_type"].unique())
experience_level_options = ['Todos'] + list(df["experience_level"].unique())
country_options = ['Todos'] + list(df["company_location"].unique())

#Creo los selectbox para los filtros 
company_size = st.sidebar.selectbox("Tamaño de compañía", options=company_size_options)
education_required = st.sidebar.selectbox("Nivel de educación", options=education_required_options)
industry = st.sidebar.selectbox("Industria", options=industry_options)
employment_type = st.sidebar.selectbox("Tipo de empleo", options=employment_type_options)
experience_level = st.sidebar.selectbox("Nivel de experiencia", options=experience_level_options)
country = st.sidebar.selectbox("País de la empresa", options=country_options)

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
if country != 'Todos':
    df_filtered = df_filtered[df_filtered["company_location"] == country]

st.markdown("""
<h1 style='text-align: center;'>Dashboard - Análisis Global de Salarios para Empleos Relacionados con IA</h1>
""", unsafe_allow_html=True)
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
if seccion == "Inicio":
    st.markdown("---")
    st.markdown("""
    ## Bienvenido al Dashboard de Análisis Global de Salarios para Empleos Relacionados con IA
    Este dashboard interactivo te permite explorar y analizar la oferta laboral en el sector de IA a nivel global. Aquí podrás:
    - Visualizar tendencias salariales y de contratación.
    - Analizar la demanda de habilidades y niveles educativos.
    - Explorar la distribución geográfica de las ofertas.
    - Investigar la duración de los procesos de aplicación y los tipos de empleo.
    
    **¿Cómo usarlo?**
    Utiliza el menú lateral para navegar por las diferentes secciones temáticas. Aplica los filtros para personalizar los resultados según tus intereses (tamaño de empresa, industria, nivel de experiencia, etc.).
    
    **Fuente de datos:**
    El análisis se basa en una base de datos de ofertas laborales diversificadas en IA, con variables como salario, ubicación, habilidades requeridas, tipo de contrato, entre otras.
    
    **Autores**: Soledad Soto Gomez, Fanllany Medina Restrepo, Jonathan Diaz Alvarez, Lucas Perdomo Molano
    """)
    
elif seccion == "Habilidades Demandadas":
    
    st.markdown("---")
    # KPIs sección Habilidades Demandadas
    col1, col2, col3, col4 = st.columns(4)
    num_habilidades = df_filtered.explode('required_skills')['required_skills'].nunique()
    habilidad_top = df_filtered.explode('required_skills')['required_skills'].value_counts().idxmax() if not df_filtered.empty else '-'
    df_explotado = df_filtered.explode('required_skills')
    habilidad_top = df_explotado['required_skills'].value_counts().idxmax()
    salario_promedio_skill = df_explotado[df_explotado['required_skills'] == habilidad_top]['salary_usd'].mean()
    salario_top_skill = df_explotado[df_explotado['required_skills'] == habilidad_top]['salary_usd'].max()

    #salario_top_skill = df_filtered.explode('required_skills').groupby('required_skills')['salary_usd'].mean().sort_values().iloc[0] if num_habilidades > 0 else 0
    #salario_min_skill = df_filtered.explode('required_skills').groupby('required_skills')['salary_usd'].mean().sort_values().iloc[0] if num_habilidades > 0 else 0
    col1.metric("Habilidades Demandadas", f"{num_habilidades}")
    col2.metric("Habilidad más frecuente", f"{habilidad_top}")
    col3.metric(f"Salario mas alto - {habilidad_top}", f"{salario_top_skill:,.0f}")
    col4.metric(f"Salario promedio - {habilidad_top}", f"{salario_promedio_skill:,.0f}")
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
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:

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
            title='Top habilidades más demandadas en IA',
            labels={'count': 'Cantidad de menciones', 'required_skills': 'Habilidad'},
            text='count'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True, title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
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
        fig.update_layout(title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Top habilidades más demandadas por país (burbujas)")
    skills_by_country = df_filtered.explode('required_skills')
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
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Mapa de calor de habilidades mas demandadas por industria")
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
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Compensación y Salarios":
    
    st.markdown("---")
    # KPIs sección Compensación y Salarios
    col1, col2, col3, col4, col5 = st.columns(5)
    salario_max = df_filtered['salary_usd'].max()
    salario_min = df_filtered['salary_usd'].min()
    salario_mediana = df_filtered['salary_usd'].median()
    salario_media = df_filtered['salary_usd'].mean()
    salario_std = df_filtered['salary_usd'].std()
    col1.metric("Salario Máximo (USD)", f"{salario_max:,.0f}")
    col2.metric("Salario Mínimo (USD)", f"{salario_min:,.0f}")
    col3.metric("Mediana Salarial", f"{salario_mediana:,.0f}")
    col4.metric("Desviación estándar", f"{salario_std:,.0f}")
    col5.metric("Salario Promedio", f"{salario_media:,.0f}")
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig_size.update_layout(xaxis={'categoryorder': 'total descending'},xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig_roles.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True, title_x=0.5)
    st.plotly_chart(fig_roles, use_container_width=True)

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
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig.update_layout(xaxis={'categoryorder': 'total ascending'},xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Matriz de correlación de variables numéricas")
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64'])
    corr_matrix = numeric_cols.corr()
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='Viridis',
        aspect='auto',
        title='Matriz de correlación de variables numéricas',
        labels={col: col for col in corr_matrix.columns}
    )
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Análisis Geográfico":
    
    st.markdown("---")
    # KPIs sección Análisis Geográfico
    col1, col2, col3, col4 = st.columns(4)
    num_paises = df_filtered['company_location'].nunique()
    pais_top = df_filtered['company_location'].value_counts().idxmax() if not df_filtered.empty else '-'
    num_empresas = df_filtered['company_location'].count()
    num_industries = df_filtered['industry'].nunique()
    col3.metric("Países con Ofertas", f"{num_paises}")
    col1.metric("País con más ofertas", f"{pais_top}")
    col2.metric("Total Ofertas", f"{num_empresas}")
    col4.metric("Total de Industrias", f"{num_industries}")
    st.markdown("---")
    
    # Mapa dinámico de ofertas por país (OpenStreetMap, sin token)
    st.subheader("Mapa dinámico de ofertas por país")
    # Mapeo de nombres de países para que coincidan con el GeoJSON
    country_name_map = {
        "United States": "United States of America",
        "Russia": "Russian Federation",
        "South Korea": "South Korea",
        "North Korea": "North Korea",
        "Singapore": "Singapore"
    }
    df_filtered['company_location'] = df_filtered['company_location'].replace(country_name_map)
    offers_by_country = df_filtered['company_location'].value_counts().reset_index()
    offers_by_country.columns = ['country', 'offers']
    fig = px.choropleth_mapbox(
        offers_by_country,
        locations="country",
        color="offers",
        geojson="https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
        featureidkey="properties.name",
        color_continuous_scale=px.colors.sequential.Viridis[::-1],
        mapbox_style="open-street-map",
        zoom=1,
        center={"lat": 20, "lon": 0},
        title="Ofertas de empleo en IA por país (mapa interactivo)",
        labels={"offers": "Cantidad de ofertas", "country": "País"}
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Cantidad de ofertas por país (top 10)")
    offers_by_country = df_filtered['company_location'].value_counts().head(20).reset_index()
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=True, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=True, title_x=0.5)
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
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=True, title_x=0.5)
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
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

elif seccion == "Ofertas de Empleo":
    st.markdown("---")
    # KPIs sección Duración del Proceso
    col1, col2, col3, col4 = st.columns(4)
    duracion_max = df_filtered['application_duration_days'].max()
    duracion_min = df_filtered['application_duration_days'].min()
    duracion_mediana = df_filtered['application_duration_days'].median()
    # Calcular promedio de ofertas por mes
    ofertas_por_mes = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M')).size()
    promedio_ofertas_mes = ofertas_por_mes.mean() if not ofertas_por_mes.empty else 0
    col1.metric("Promedio ofertas/mes", f"{promedio_ofertas_mes:,.0f}")
    col2.metric("Duración máxima (días)", f"{duracion_max:,.0f}")
    col3.metric("Duración mínima (días)", f"{duracion_min:,.0f}")
    col4.metric("Promedio de duración (días)", f"{duracion_mediana:,.0f}")
    
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
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5, yaxis=dict(range=[0, 1600]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Evolución de ofertas por modalidad de Trabajo")
    remote_trend = df_filtered.groupby([df_filtered['posting_date'].dt.to_period('M'), 'remote_ratio']).size().reset_index(name='num_offers')
    remote_trend['posting_date'] = remote_trend['posting_date'].dt.to_timestamp()
    custom_colors = [px.colors.sequential.Viridis[6],px.colors.sequential.Viridis[1],px.colors.sequential.Viridis[8]] 

    fig = px.line(
        remote_trend,
        x='posting_date',
        y='num_offers',
        color='remote_ratio',
        markers=True,
        color_discrete_sequence=custom_colors,
        title='Evolución de las ofertas por modalidad de trabajo remoto a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'num_offers': 'Número de ofertas', 'remote_ratio': 'Modalidad'}
    )
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5, )
    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")
    st.subheader("Evolución de duración entre publicación y fecha límite de la oferta")
    duration_trend = df_filtered.groupby(df_filtered['posting_date'].dt.to_period('M'))['application_duration_days'].mean().reset_index()
    duration_trend['posting_date'] = duration_trend['posting_date'].dt.to_timestamp()
    fig = px.line(
        duration_trend,
        x='posting_date',
        y='application_duration_days',
        markers=True,
        title='Duración promedio entre publicación y fecha límite de la oferta a lo largo del tiempo',
        labels={'posting_date': 'Fecha', 'application_duration_days': 'Duración promedio (días)'}
    )
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5 )
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
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

