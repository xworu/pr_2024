import requests
from bs4 import BeautifulSoup
import time

headers = {
    'Host': 'hh.ru',
    'User-Agent': 'Safari',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}


def get_vacancy_links(query, text, employment, schedule, experience, education_level, salary):
    data = requests.get(
        url=f"https://hh.ru/search/{query}?L_save_area=true&area=113&area=1&items_on_page=100&experience={experience}"
            f"&education={education_level}&employment={employment}&schedule={schedule}&text={text}"
            f"&salary={salary}&only_with_salary=true&page=1",
        headers=headers
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(soup.find_all("span",
                                       attrs={"class": "pager-item-not-in-short-range"})[-1].find("a").find(
            "span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/{query}?L_save_area=true&area=113&area=1&items_on_page=100&experience={experience}"
                    f"&education={education_level}&employment={employment}&schedule={schedule}&text={text}"
                    f"&salary={salary}&only_with_salary=true&page={page}",
                headers=headers
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in (
            soup.find(class_="vacancy-search-item__card serp-item_link vacancy-card-container--OwxCdOj5QlSlCBZvSggS")
                    .find_all("a", attrs={"class": "bloko-link"})):
                href = f"{a.attrs['href'].split('?')[0]}"
                if href.startswith("https://hh.ru/vacancy/"):
                    yield href
        except Exception as e:
            print(f"{e}")
        time.sleep(1)


def get_vacancy(link):
    data = requests.get(
        url=link,
        headers=headers
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find(attrs={"class": "bloko-header-section-1"}).text
    except:
        return
    try:
        salary = (soup.find(attrs={
            "class": "magritte-text___pbpft_3-0-9 magritte-text_style-primary___AQ7MW_3-0-9 magritte-text_typography-label-1-regular___pi3R-_3-0-9"})
                  .text.replace("\u2009", "").replace("\xa0", " "))
    except:
        salary = "Не указано"
    try:
        experience = (soup.find(attrs={"class": "vacancy-description-list-item"})
                      .text.replace("\xa0", " "))
    except:
        experience = "Не указано"
    try:
        company = soup.find(attrs={"class": "vacancy-company-details"}).text.replace("\xa0", " ")
    except:
        company = "Не указано"
    vacancy = {
        "name": name,
        "salary": salary,
        "experience": experience,
        "company": company,
        "link": link
    }
    return vacancy
