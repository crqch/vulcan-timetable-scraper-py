# IMPORTS
import json
import os
import re
import time

from colorama import Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, ' ', raw_html)
    return cleantext


def printState(state, text):
    if state == '+':
        print(f"{Fore.LIGHTGREEN_EX}[+] {text}{Fore.RESET}")
    elif state == '!':
        print(f"{Fore.RED}[!] {text}{Fore.RESET}")
    elif state == '-':
        print(f"{Fore.LIGHTYELLOW_EX}[-] {text}{Fore.RESET}")


class Main:
    def __init__(self):
        printState('+', 'Loading vulcan-timetable-scraper-py by @crqch')
        if not (os.path.isdir('./output')):
            os.mkdir('./output')
            printState('+', 'Creating new directory')
        if os.path.isfile('./output/classes.json') | os.path.isfile('./output/teachers.json') | os.path.isfile(
                './output/rooms.json'):
            printState('-', 'Files already exist, renaming the directory')
            os.rename('./output', './output-{}'.format(str(int(round(time.time() * 1000)))))
            printState('+', 'Creating new directory')
            os.mkdir('./output')
        printState('-', 'Please input the URL of the timetable you want to scrape')
        self.url = input(f"{Fore.YELLOW} > ")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless") # Comment this line if you want to see the browser
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            browser = webdriver.Chrome(options=chrome_options)
            self.browser = browser
            browser.get(f'{self.url}')
            printState('+', 'Browser opened successfully')
            self.scrape(browser)
        except Exception as e:
            printState('!', 'An error occurred while trying to open the browser')
            printState('!', 'Possible solutions:')
            printState('!', '   Check if you have ChromeDriver in the same directory as this script')
            printState('!', '   Check if you have inputted the correct URL')
            printState('!', 'Download ChromeDriver from https://chromedriver.chromium.org/downloads with the same '
                            'version as your browser')
            printState('!', '   \nIf it will still not work, please review the error message below')
            printState('!', f'{e}')
            exit()

    def scrape(self, browser):
        printState('-', 'Checking if the timetable is available')
        try:
            # time.sleep(1)  # Wait for the page to load
            browser.switch_to.frame(browser.find_element_by_xpath('/html/frameset/frame[1]'))
            linksReturned = browser.find_element_by_xpath('/html/body').find_elements_by_tag_name('ul')
            links = {
                "classes": linksReturned[0],
                "teachers": linksReturned[1],
                "rooms": linksReturned[2]
            }
            printState('+', 'Timetable is available')
            printState('-', 'Scraping classes')
            self.classes = {}
            self.teachers = {}
            self.rooms = {}
            self.iterateLinks(0, 'classes')
            self.iterateLinks(1, 'teachers')
            self.iterateLinks(2, 'rooms')
            printState('+', 'Scraping complete')
            printState('-', 'Saving data')
            self.saveFile('classes')
            self.saveFile('teachers')
            self.saveFile('rooms')
            printState('+', 'Data saved successfully')
            printState('-', 'Closing browser')
            browser.close()
            printState('+', 'Browser closed successfully')
            printState('+', 'Successfully completed')
            printState('+', 'Output files are in the output directory')
            printState('+', 'If you liked this script, please consider leaving star rating on GitHub Repository')
            printState('!', 'Exiting')
            exit()

        except Exception as e:
            printState('!', 'The timetable is not available at the URL you have inputted')
            print(e)
            exit()

    def saveFile(self, tableType):
        if os.path.isfile(f'./output/{tableType}.json'):
            file = open(f'./output/{tableType}.json')
            content = json.load(file)
            if tableType == 'classes':
                content.update(self.classes)
            elif tableType == 'teachers':
                content.update(self.teachers)
            elif tableType == 'rooms':
                content.update(self.rooms)
            file.close()
            os.remove(f'./output/{tableType}.json')
            fileWrite = open(f'./output/{tableType}.json', 'w+', encoding="windows-1250")
            json.dump(content, fileWrite, indent=4, ensure_ascii=False)
            fileWrite.close()
        else:
            file = open(f'./output/{tableType}.json', "w+", encoding="windows-1250")
            if tableType == 'classes':
                json.dump(self.classes, file, indent=4, ensure_ascii=False)
            elif tableType == 'teachers':
                json.dump(self.teachers, file, indent=4, ensure_ascii=False)
            elif tableType == 'rooms':
                json.dump(self.rooms, file, indent=4, ensure_ascii=False)
            file.close()

    def iterateLinks(self, num, tableType):
        browser = self.browser
        links = browser.find_element_by_xpath(f'/html/body/ul[{num + 1}]').find_elements_by_tag_name('li')
        iterateNum = 0
        for linkField in links:
            iterateNum += 1
            link = browser.find_element_by_xpath(f'/html/body/ul[{num + 1}]/li[{iterateNum}]').find_element_by_tag_name(
                'a').get_attribute('href')
            linkName = browser.find_element_by_xpath(
                f'/html/body/ul[{num + 1}]/li[{iterateNum}]').find_element_by_tag_name('a').get_attribute("innerHTML")
            printState('-', f'Scraping {linkName}')
            self.saveTimetable(link, linkName, tableType)
            print("\033[A\033[A")
            browser.get(f'{self.url}')
            browser.switch_to.frame(browser.find_element_by_xpath('/html/frameset/frame[1]'))
            printState('+', f'Scraped {linkName}    ')

    def saveTimetable(self, link, linkName, tableType):
        browser = self.browser
        browser.get(link)
        table = browser.find_element_by_xpath('/html/body/div/table/tbody/tr[1]/td/table')
        tableData = []
        for row in table.find_elements_by_tag_name('tr'):
            rowData = []
            if row.find_elements_by_tag_name('td'):
                for cell in row.find_elements_by_tag_name('td'):
                    rowData.append(cleanhtml(cell.get_attribute('innerHTML')))
            else:
                for cell in row.find_elements_by_tag_name('th'):
                    rowData.append(cleanhtml(cell.get_attribute('innerHTML')))
            tableData.append(rowData)
        if tableType == 'classes':
            self.classes[linkName] = tableData
        elif tableType == 'teachers':
            self.teachers[linkName] = tableData
        elif tableType == 'rooms':
            self.rooms[linkName] = tableData


if __name__ == '__main__':
    try:
        Main().__init__()
    except KeyboardInterrupt:
        printState('!', 'Exiting...')
