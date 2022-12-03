import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from extract_skills import skill_extractor, extract_words
from selenium.webdriver.chrome.options import Options
import re


def remove_char(text):
    return re.sub('[^A-Za-z0-9\s£]+', '', text)


def get_url_indeed(title, location):

    job_title = title
    location = location
    jobs_url = {"Indeed": "https://uk.indeed.com/"}
    driver = webdriver.Chrome(options= chrome_options)
    driver.get(jobs_url["Indeed"])

    driver.find_element(by=By.XPATH, value='//*[@id="text-input-what"]').send_keys(job_title)
    time.sleep(1)
    if location != "":
        driver.find_element(by=By.XPATH, value='//*[@id="text-input-where"]').send_keys(location)
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='/html/body/div').click()
    time.sleep(1)
    try:
        driver.find_element(by=By.XPATH, value='//*[@id="jobsearch"]/button').click()
    except NoSuchElementException:
        driver.find_element(by=By.XPATH, value='//*[@id="whatWhereFormId"]/div[3]/button').click()
    time.sleep(1)
    contents = []
    num_of_pages = 1
    content = BeautifulSoup(driver.page_source, "lxml")
    contents.append(content)
    for i in range(0,num_of_pages-1):
        next_page_xpath = '/html/body/main/div/div[1]/div/div/div[5]/div[1]/nav/div[{}]/a'
        x = 2
        if i < 1:
            x = 4
        elif i > 1:
            x = 5
        next_page_xpath = next_page_xpath.format(x)
        element = driver.find_element(by=By.XPATH, value=next_page_xpath)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        content = BeautifulSoup(driver.page_source, "lxml")
        contents.append(content)
    return contents


def scrape_job_details_indeed(contents):
    jobs_list = []
    for content in contents:

        for post in content.select('.job_seen_beacon'):
            try:
                data = {
                    "job_title": post.select('.jobTitle')[0].get_text().strip(),
                    "location": post.select('.companyLocation')[0].get_text().strip(),
                    "company": post.select('.companyName')[0].get_text().strip(),
                    "date": post.select('.date')[0].get_text().strip(),
                    "job_desc": remove_char(post.select('.job-snippet')[0].get_text().strip())
                }
            except IndexError:
                continue
            jobs_list.append(data)

    dataframe = pd.DataFrame(jobs_list)
    dataframe.to_csv("indeed.csv")


def scrape_job_details_reed(title, location):
    url = "https://www.reed.co.uk/jobs/{}-jobs-in-{}?pageno={}"
    all_data = []
    title = title
    title = title.replace(" ", "-")
    location = location
    if location is None or location == "":
        url = "https://www.reed.co.uk/jobs/{}-jobs{}?pageno={}"
    for page in range(1, 3):
        print("Getting page {}".format(page))
        soup = BeautifulSoup(requests.get(url.format(title,location,page)).content, "html.parser")

        for job in soup.select("#server-results article"):

            if job is not None and job.h3 is not None:
                print(job)
                title = job.h3.get_text(strip=True)
                posted_by = job.select_one(".job-result-heading__posted-by").get_text().strip()
                salary = job.find('li', attrs={'class': 'job-metadata__item job-metadata__item--salary'}).text
                salary = salary.strip() if salary else ""
                description = job.select_one(".job-result-description").p.get_text().strip()
                location = job.select_one(".job-metadata__item--location").get_text().strip()
                all_data.append((title, posted_by, salary, description, location))
            else:
                continue
    df = pd.DataFrame(all_data, columns=["Title", "Location", "Company", "Salary", "Summary" ])
    df.to_csv("reed.csv", index=False)


def scrape_jobs_details_totaljobs(title, location):
    url = "https://www.totaljobs.com/jobs/{}/in-{}"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    title = title
    title = title.replace(" ", "-")
    driver = webdriver.Chrome(options= chrome_options)
    print(location)
    if location is None or location == "":
        url = "https://www.totaljobs.com/jobs/{}{}"
        location = ""
    driver.get(url.format(title, location))

    time.sleep(6)
    content = BeautifulSoup(driver.page_source, "lxml")
    #print(content)
    #print(content.find_all("div", {"class": "Wrapper-sc-11673k2-0 eHVkAX"}))
    jobs_list = []
    for info in content.find_all("div", {"class": "Wrapper-sc-11673k2-0 eHVkAX"}):
        try:
            data = {
                "job_title": info.find("h2", {"class": "sc-fzqMAW krdChg"}).get_text().strip(),
                "location": info.find("li", {"class": "sc-fznXWL jExrPv"}).get_text().strip(),
                "company": info.find("div", {"class": "sc-fzoiQi kuzZTz"}).get_text().strip(),
                "Salary": remove_char(info.find("dl", {"class": "sc-fzoJMP jpodhy"}).get_text().strip()),
                "date": info.find("li", {"class": "sc-fznXWL jwFffy"}).get_text().strip(),
                "job_desc": info.find("a", {"class": "sc-fznWOq sc-fzolEj kZvhzt"}).get_text().strip(),
                "skills": extract_words(skills_extractor, info.find("a", {"class": "sc-fznWOq sc-fzolEj kZvhzt"}).get_text().strip())
            }
            print(data)
        except IndexError:
            continue
        jobs_list.append(data)
    dataframe = pd.DataFrame(jobs_list)
    dataframe.to_csv("totaljobs.csv")


if __name__ == '__main__':
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    skills_extractor = skill_extractor()
    title = "Software developer"
    location = ""
    chrome_options = Options()

    chrome_options.headless = True
    chrome_options.add_argument("--user-agent=Mozilla...")
    chrome_options.add_argument('--disable-gpu')
    #indeed_url = get_url_indeed(title, location)
    #scrape_job_details_indeed(indeed_url)
    #scrape_job_details_reed(title, location)
    scrape_jobs_details_totaljobs(title, location)

