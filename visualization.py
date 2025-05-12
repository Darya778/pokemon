import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
import re

df = pd.read_csv("pokemon_data.csv")

def clean_number(value):
    if pd.isna(value):
        return None
    s = str(value)
    s = re.sub(r"[^\d.,]", "", s)
    s = s.replace(",", ".")
    if s.count(".") > 1:
        parts = s.split(".")
        s = parts[0] + "." + "".join(parts[1:])
    try:
        return float(s)
    except ValueError:
        return None

df["Рост"] = df["Рост"].apply(clean_number)
df["Вес"] = df["Вес"].apply(clean_number)

numeric_columns = df.select_dtypes(include='number').columns.tolist()

pokemon_names = df["Имя"].dropna().unique().tolist()
select1 = widgets.Dropdown(options=pokemon_names, description="Персонаж 1:")
select2 = widgets.Dropdown(options=pokemon_names, description="Персонаж 2:")
select3 = widgets.Dropdown(options=pokemon_names, description="Персонаж 3:")
select4 = widgets.Dropdown(options=pokemon_names, description="Персонаж 4:")

param_selector = widgets.SelectMultiple(
    options=numeric_columns,
    value=["Рост", "Вес"],
    description="Параметры:",
    layout=widgets.Layout(width='50%'),
    rows=8
)

colors = ["#FF5733", "#3375FF", "#33FF57", "#FF33A8"]

def compare_pokemons(p1, p2, p3, p4, selected_params):
    clear_output(wait=True)

    if len(selected_params) == 0:
        print("Выберите хотя бы один параметр.")
        return

    if not all([p1, p2, p3, p4]):
        print("Выберите всех четырёх персонажей.")
        return

    try:
        p1_data = df[df["Имя"] == p1][list(selected_params)].iloc[0]
        p2_data = df[df["Имя"] == p2][list(selected_params)].iloc[0]
        p3_data = df[df["Имя"] == p3][list(selected_params)].iloc[0]
        p4_data = df[df["Имя"] == p4][list(selected_params)].iloc[0]
    except IndexError:
        print("Ошибка при получении данных. Убедитесь, что все выбранные персонажи присутствуют в данных.")
        return

    x = range(len(selected_params))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar([i - 1.5 * width for i in x], p1_data, width, label=p1, color=colors[0])
    ax.bar([i - 0.5 * width for i in x], p2_data, width, label=p2, color=colors[1])
    ax.bar([i + 0.5 * width for i in x], p3_data, width, label=p3, color=colors[2])
    ax.bar([i + 1.5 * width for i in x], p4_data, width, label=p4, color=colors[3])

    ax.set_xticks(x)
    ax.set_xticklabels(selected_params, rotation=45)
    ax.set_ylabel("Значение")
    ax.set_title("Сравнение характеристик персонажей")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

ui = widgets.VBox([param_selector, select1, select2, select3, select4])
out = widgets.interactive_output(
    compare_pokemons,
    {
        'p1': select1,
        'p2': select2,
        'p3': select3,
        'p4': select4,
        'selected_params': param_selector
    }
)

display(ui, out)

