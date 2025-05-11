from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

df = pd.read_csv("pokemons.csv")
data = []


def safe_get_text(element):
    return element.get_text(strip=True) if element else None


def extract_fields(soup):
    fields = {}

    title_section = soup.find("h2", class_="pi-title")
    if title_section:
        japanese_name = title_section.find("i")
        fields["Японское имя"] = safe_get_text(japanese_name)

    card = soup.find("aside", class_="portable-infobox")
    if not card:
        return fields

    for row in card.select(".pi-item.pi-data"):
        label = row.select_one(".pi-data-label")
        value = row.select_one(".pi-data-value")
        if label and value:
            fields[safe_get_text(label)] = safe_get_text(value)

    for group in card.select(".pi-smart-group"):
        group_header = group.select_one(".pi-smart-group-head")
        header_text = safe_get_text(group_header)

        group_body = group.select_one(".pi-smart-group-body")
        if not group_body:
            continue

        labels = group_body.select(".pi-smart-data-value[data-item-name='pi-data-label simple']")
        values = group_body.select(".pi-smart-data-value:not([data-item-name='pi-data-label simple'])")

        if labels and values and len(labels) == len(values):
            for label, value in zip(labels, values):
                fields[safe_get_text(label)] = safe_get_text(value)
        else:
            if header_text:
                fields[header_text] = safe_get_text(group_body)

    type_section = card.find(lambda tag: tag.name == "h3" and "Тип(-ы)" in tag.text)
    if type_section:
        type_value = safe_get_text(type_section.find_next(".pi-smart-group-body"))
        if type_value:
            fields["Тип"] = type_value

    gender_section = card.find(lambda tag: tag.name == "h3" and "Пол" in tag.text)
    if gender_section:
        gender_value = safe_get_text(gender_section.find_next(".pi-smart-group-body"))
        if gender_value:
            fields["Пол"] = gender_value.replace("\n", " ").strip()

    height_section = card.find(lambda tag: tag.name == "h3" and "Рост" in tag.text)
    if height_section:
        height_value = safe_get_text(height_section.find_next(".pi-smart-data-value"))
        if height_value:
            fields["Рост"] = height_value

    weight_section = card.find(lambda tag: tag.name == "h3" and "Вес" in tag.text)
    if weight_section:
        weight_value = safe_get_text(weight_section.find_next(".pi-smart-data-value"))
        if weight_value:
            fields["Вес"] = weight_value

    evolution_sections = card.find_all(lambda tag: tag.name == "div" and "Эволюция" in tag.text)
    for section in evolution_sections:
        text = safe_get_text(section)
        if "Эволюция из" in text:
            fields["Эволюция из"] = text.replace("Эволюция из", "").strip()
        elif "Эволюция в" in text:
            fields["Эволюция в"] = text.replace("Эволюция в", "").strip()

    return fields


for i, row in df.iterrows():
    name = row["name"]
    url = row["link"]

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        fields = extract_fields(soup)
        fields["Имя"] = name
        fields["Ссылка"] = url
        data.append(fields)

        print(f"{i + 1}/{len(df)}: {name} — найдено {len(fields)} характеристик")

    except Exception as e:
        print(f"Ошибка при обработке {name}: {str(e)}")
        continue

    if i % 20 == 0 and i != 0:
        pd.DataFrame(data).to_csv("backup_pokemon_data.csv", index=False)
        print("Резервное сохранение")

driver.quit()

df_out = pd.DataFrame(data)
df_out.to_csv("pokemon_data.csv", index=False)
print("Готово. Данные сохранены в pokemon_data.csv")
