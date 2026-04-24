import streamlit as st
import pandas as pd

# Константи територіальної громади
MFO = "899998"
EDRPOU = "38012494"

st.set_page_config(page_title="Пошук заборгованості", page_icon="🏦")

st.title("🔍 Перевірка боргу зі сплати земельного податкута податку на нерухоме майно")
st.write("Зорянська сільська територіальна громада")

@st.cache_data
def load_data():
    # Завантаження файлу. Використовуємо sep=';' згідно з вашим форматом
    df = pd.read_csv("Борг зі сплати майнових податків Зоря на 01.04.2026.csv", sep=';', skip_blank_lines=True)
    
    # Очищення назв колонок від зайвих пробілів
    df.columns = df.columns.str.strip()
    
    # Видаляємо рядки, де немає ПІБ (наприклад, заголовки)
    df = df.dropna(subset=['ПІБ'])
    
    # Перетворюємо суму боргу в число (прибираємо пробіли та міняємо кому на крапку)
    df['Борг на 01.04.2026'] = df['Борг на 01.04.2026'].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
    df['Борг на 01.04.2026'] = pd.to_numeric(df['Борг на 01.04.2026'], errors='coerce')
    
    return df

try:
    data = load_data()

    # Поле пошуку
    search_input = st.text_input("Введіть ПІБ або РНОКПП (10 цифр):").strip().lower()

    if search_input:
        # Пошук по ПІБ або по РНОКПП (перетворюємо в рядок для порівняння)
        results = data[
            (data['ПІБ'].str.lower().str.contains(search_input, na=False)) |
            (data['РНОКПП'].astype(str).str.contains(search_input, na=False))
        ]

        if not results.empty:
            st.success(f"Знайдено записів: {len(results)}")
            
            for index, row in results.iterrows():
                with st.container():
                    st.markdown(f"### 👤 {row['ПІБ']}")
                    st.markdown(f"**Сума боргу:** `{row['Борг на 01.04.2026']:.2f} грн.`")
                    st.info(f"📍 **Тип податку:** {row['Назва коду класифікації доходів бюджету']}")
                    
                    # Реквізити для оплати
                    with st.expander("💳 Показати реквізити для оплати"):
                        st.code(f"""Отримувач: Зорянська СТГ
Рахунок (IBAN): {row['Бюджетний рахунок']}
МФО: {MFO}
ЄДРПОУ: {EDRPOU}
Призначення: Оплата заборгованості ({row['Назва коду класифікації доходів бюджету']}) для {row['ПІБ']}""", language="text")
                    st.divider()
        else:
            st.warning("Нічого не знайдено. Перевірте правильність введення даних.")

except Exception as e:
    st.error("Помилка завантаження бази даних. Перевірте назву та формат CSV файлу.")
