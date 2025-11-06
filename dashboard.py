import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json

# Настройки цветовой схемы
PRIMARY_COLOR = "#008080"
BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"

# Настройка страницы
st.set_page_config(
    page_title="Медицинская Статистика",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS для настройки цветов
st.markdown(f"""
<style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    .css-1d391kg {{
        background-color: {BACKGROUND_COLOR};
    }}
    .css-1lcbmhc {{
        color: {TEXT_COLOR};
    }}
    .stSidebar {{
        background-color: {BACKGROUND_COLOR};
    }}
    .stMetric {{
        background-color: {PRIMARY_COLOR}10;
        border-radius: 10px;
        padding: 10px;
    }}
    .stMetric .metric-value {{
        color: {PRIMARY_COLOR};
        font-size: 2rem;
        font-weight: bold;
    }}
    .stMetric .metric-label {{
        color: {TEXT_COLOR};
        font-size: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Функции для работы с API
def get_api_data(endpoint, params=None, auth_token=None):
    """Получение данных из API"""
    base_url = st.session_state.get('api_url', 'http://localhost:8000')
    url = f"{base_url}{endpoint}"

    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при получении данных: {e}")
        return None

def login_user(username, password):
    """Аутентификация пользователя"""
    base_url = st.session_state.get('api_url', 'http://localhost:8000')
    url = f"{base_url}/auth/login"

    try:
        response = requests.post(url, json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            st.error("Неверные учетные данные")
            return None
    except Exception as e:
        st.error(f"Ошибка аутентификации: {e}")
        return None

# Инициализация состояния сессии
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'api_url' not in st.session_state:
    st.session_state.api_url = 'http://localhost:8000'

# Боковая панель
with st.sidebar:
    st.title("🏥 Медицинская Статистика")

    # Настройки API
    with st.expander("Настройки API"):
        api_url = st.text_input("URL API", value=st.session_state.api_url)
        if st.button("Сохранить URL"):
            st.session_state.api_url = api_url
            st.success("URL сохранен")

    # Аутентификация
    if st.session_state.auth_token is None:
        st.subheader("Вход в систему")
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")

        if st.button("Войти"):
            if username and password:
                token = login_user(username, password)
                if token:
                    st.session_state.auth_token = token
                    st.success("Успешный вход!")
                    st.rerun()
            else:
                st.error("Введите имя пользователя и пароль")
    else:
        st.success("Вы вошли в систему")
        if st.button("Выйти"):
            st.session_state.auth_token = None
            st.rerun()

# Основной контент
if st.session_state.auth_token is None:
    st.title("Добро пожаловать в дашборд медицинской статистики")
    st.info("Пожалуйста, войдите в систему для просмотра статистики")
else:
    # Заголовок
    st.title("📊 Дашборд Статистики")

    # Получение общей статистики
    general_stats = get_api_data("/stats/general", auth_token=st.session_state.auth_token)

    if general_stats:
        # Метрики
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Всего пациентов", general_stats.get('total_patients', 0))

        with col2:
            st.metric("Всего записей", general_stats.get('total_appointments', 0))

        with col3:
            st.metric("Врачей", general_stats.get('total_doctors', 0))

        with col4:
            st.metric("Процент завершения", f"{general_stats.get('completion_rate', 0)}%")

        # Финансовая статистика
        financial_stats = get_api_data("/stats/financial", auth_token=st.session_state.auth_token)

        if financial_stats:
            st.header("💰 Финансовая статистика")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Общая выручка", f"${financial_stats.get('total_revenue', 0):,.2f}")

            with col2:
                st.metric("Выручка сегодня", f"${financial_stats.get('revenue_today', 0):,.2f}")

            with col3:
                st.metric("Выручка за неделю", f"${financial_stats.get('revenue_this_week', 0):,.2f}")

            with col4:
                st.metric("Средняя стоимость", f"${financial_stats.get('average_appointment_cost', 0):,.2f}")

        # Фильтры по датам
        st.header("📅 Фильтры и настройки")

        col1, col2, col3 = st.columns(3)

        with col1:
            days = st.slider("Количество дней для анализа", min_value=1, max_value=30, value=7)

        with col2:
            start_date = st.date_input("Начальная дата", value=date.today() - timedelta(days=7))

        with col3:
            end_date = st.date_input("Конечная дата", value=date.today())

        # Графики ежедневной статистики
        st.header("📈 Ежедневная статистика")

        # Получение ежедневной статистики
        daily_stats = get_api_data("/stats/daily", params={"days": days}, auth_token=st.session_state.auth_token)

        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            df_daily['date'] = pd.to_datetime(df_daily['date'])

            # График записей
            fig_appointments = px.line(df_daily, x='date', y='appointments_count',
                                     title='Количество записей по дням',
                                     color_discrete_sequence=[PRIMARY_COLOR])
            fig_appointments.update_layout(
                plot_bgcolor=BACKGROUND_COLOR,
                paper_bgcolor=BACKGROUND_COLOR,
                font_color=TEXT_COLOR
            )
            st.plotly_chart(fig_appointments, use_container_width=True)

            # График завершенных записей
            fig_completed = px.line(df_daily, x='date', y='completed_count',
                                  title='Завершенные записи по дням',
                                  color_discrete_sequence=[PRIMARY_COLOR])
            fig_completed.update_layout(
                plot_bgcolor=BACKGROUND_COLOR,
                paper_bgcolor=BACKGROUND_COLOR,
                font_color=TEXT_COLOR
            )
            st.plotly_chart(fig_completed, use_container_width=True)

            # Экспорт данных
            st.subheader("📤 Экспорт данных")
            if st.button("Экспортировать ежедневную статистику в CSV"):
                csv = df_daily.to_csv(index=False)
                st.download_button(
                    label="Скачать CSV",
                    data=csv,
                    file_name="daily_stats.csv",
                    mime="text/csv"
                )

        # Статистика по врачам
        st.header("👨‍⚕️ Статистика по врачам")

        doctors_stats = get_api_data("/stats/doctors", auth_token=st.session_state.auth_token)

        if doctors_stats:
            df_doctors = pd.DataFrame(doctors_stats)

            # Таблица статистики врачей
            st.dataframe(df_doctors[['doctor_name', 'total_appointments', 'completed_appointments', 'completion_rate']])

            # График производительности врачей
            fig_doctors = px.bar(df_doctors, x='doctor_name', y='completion_rate',
                               title='Процент завершения по врачам',
                               color_discrete_sequence=[PRIMARY_COLOR])
            fig_doctors.update_layout(
                plot_bgcolor=BACKGROUND_COLOR,
                paper_bgcolor=BACKGROUND_COLOR,
                font_color=TEXT_COLOR
            )
            st.plotly_chart(fig_doctors, use_container_width=True)

            # Экспорт данных по врачам
            if st.button("Экспортировать статистику врачей в CSV"):
                csv = df_doctors.to_csv(index=False)
                st.download_button(
                    label="Скачать CSV",
                    data=csv,
                    file_name="doctors_stats.csv",
                    mime="text/csv"
                )

        # Финансовая статистика по врачам
        st.header("💰 Финансовая статистика по врачам")

        doctors_financial = get_api_data("/stats/financial/doctors", auth_token=st.session_state.auth_token)

        if doctors_financial:
            df_doctors_fin = pd.DataFrame(doctors_financial)

            # Таблица финансовой статистики
            st.dataframe(df_doctors_fin[['doctor_name', 'total_revenue', 'completed_revenue', 'average_appointment_cost']])

            # График выручки по врачам
            fig_revenue = px.bar(df_doctors_fin, x='doctor_name', y='total_revenue',
                               title='Общая выручка по врачам',
                               color_discrete_sequence=[PRIMARY_COLOR])
            fig_revenue.update_layout(
                plot_bgcolor=BACKGROUND_COLOR,
                paper_bgcolor=BACKGROUND_COLOR,
                font_color=TEXT_COLOR
            )
            st.plotly_chart(fig_revenue, use_container_width=True)

            # Экспорт финансовых данных по врачам
            if st.button("Экспортировать финансовую статистику врачей в CSV"):
                csv = df_doctors_fin.to_csv(index=False)
                st.download_button(
                    label="Скачать CSV",
                    data=csv,
                    file_name="doctors_financial_stats.csv",
                    mime="text/csv"
                )

    else:
        st.error("Не удалось загрузить статистику. Проверьте подключение к API.")