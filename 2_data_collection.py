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

df = pd.read_csv("pokemons.csv", encoding="utf-8-sig")
data = []

def safe_get_text(element):
    return element.get_text(strip=True) if element else None

def clean_key(key):
    return key.strip().replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')

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
            key = clean_key(safe_get_text(label))
            val = safe_get_text(value)
            fields[key] = val

    for group in card.select(".pi-smart-group"):
        labels = group.select(".pi-smart-data-label")
        values = group.select(".pi-smart-data-value")

        if labels and values and len(labels) == len(values):
            for label, value in zip(labels, values):
                key = clean_key(safe_get_text(label))
                val = safe_get_text(value)
                fields[key] = val
        else:
            group_header = group.select_one(".pi-smart-group-head")
            header_text = safe_get_text(group_header)
            if header_text:
                value_texts = [safe_get_text(val) for val in values if safe_get_text(val)]
                fields[header_text] = " / ".join(value_texts)

    def extract_field_by_header(text, label):
        section = card.find(lambda tag: tag.name == "h3" and text in tag.text)
        if section:
            value = safe_get_text(section.find_next(".pi-smart-group-body") or section.find_next(".pi-smart-data-value"))
            if value:
                fields[label] = value.strip()

    extract_field_by_header("Тип", "Тип")
    extract_field_by_header("Пол", "Пол")
    extract_field_by_header("Рост", "Рост")
    extract_field_by_header("Вес", "Вес")

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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        fields = extract_fields(soup)
        fields["Имя"] = name
        fields["Ссылка"] = url
        data.append(fields)

        print(f"{i + 1}/{len(df)}: {name} — найдено {len(fields)} характеристик")

    except Exception as e:
        print(f"[Ошибка] {name}: {str(e)}")
        continue

    if i % 10 == 0 and i != 0:
        pd.DataFrame(data).to_csv("backup_pokemon_data.csv", index=False, encoding="utf-8-sig")
        print("Резервное сохранение")

driver.quit()

df_out = pd.DataFrame(data)
df_out.to_csv("pokemon_data.csv", index=False, encoding="utf-8-sig")
print("Готово. Данные сохранены в pokemon_data.csv")
