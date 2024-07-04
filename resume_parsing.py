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


def get_resume_links(query, text, employment, schedule, experience, education_level, salary):
    data = requests.get(
        url=f"https://hh.ru/search/{query}?area=113&isDefaultArea=true&employment={employment}"
            f"&schedule={schedule}&ored_clusters=true&order_by=relevance&items_on_page=100"
            f"&search_period=0&education_level={education_level}&logic=normal&pos=full_text"
            f"&exp_period=all_time&experience={experience}&text={text}&salary_from={salary}&page=0",
        headers=headers
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(soup.find("div",
                                   attrs={"class": "pager"}).find_all("span",
                                                                      recursive=False)[-1].find("a").find("span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/{query}?area=113&isDefaultArea=true&employment={employment}"
            f"&schedule={schedule}&ored_clusters=true&order_by=relevance&items_on_page=100"
            f"&search_period=0&education_level={education_level}&logic=normal&pos=full_text"
            f"&exp_period=all_time&experience={experience}&text={text}&salary_from={salary}&page={page}",
                headers=headers
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in soup.find_all("a", attrs={"class": "bloko-link"}):
                href = f"https://hh.ru{a.attrs['href'].split('?')[0]}"
                if href.startswith("https://hh.ru/resume/"):
                    yield href
        except Exception as e:
            print(f"{e}")
        time.sleep(1)


def get_resume(link):
    data = requests.get(
        url=link,
        headers=headers
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find(attrs={"class": "resume-block__title-text"}).text
    except:
        return
    try:
        salary = (soup.find(attrs={"class": "resume-block__salary"})
                  .text.replace("\u2009", "").replace("\xa0", " "))
    except:
        salary = "Не указано"
    try:
        experience = (soup.find(attrs={"class": "resume-block__title-text resume-block__title-text_sub"})
                      .text.replace("\xa0", " ").replace("\xa0", " "))
    except:
        experience = "Не указано"
    try:
        skills = soup.find(attrs={"class": "resume-block", "data-qa": "skills-table"}).find_all("span")
        for i in range(len(skills)):
            skills[i] = skills[i].text
    except:
        skills = "Не указано"
    resume = {
        "name": name,
        "salary": salary,
        "experience": experience,
        "skills": skills,
        "link": link
    }
    return resume
