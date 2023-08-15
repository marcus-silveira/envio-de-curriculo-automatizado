from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep


class FindJobs:
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("--incognito")
        self.service = service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=self.options, service=service)
        self.page_number = 1
        self.job_links = []
        sleep(1)

    def search_for_jobs(self, url, job, locale=""):
        self.driver.get(url)
        self.driver.find_element(By.ID, "input_vaga").send_keys(job)
        self.driver.find_element(By.ID, "input_cidade").send_keys(locale)
        self.driver.find_element(
            By.XPATH, "//button[text()='Pesquisar' and contains(@class, 'btn-primary')]").click()
        sleep(2)

    def scroll_to_bottom(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def get_all_job_links(self, link_text, class_name, next_page=False):
        xpath = f"//a[text()='{link_text}' and contains(@class, '{class_name}')]"
        try:
            job_elements = self.driver.find_elements(By.XPATH, xpath)
            if not job_elements:
                return self.job_links
        except:
            return self.job_links
        for element in job_elements:
            self.job_links.append(element.get_attribute("href"))
        sleep(1)
        if next_page:
            self.page_number += 1
            self.click_pagination(self.page_number)
        return self.job_links

    def click_pagination(self, page_number):
        try:
            self.driver.get(
                f"https://www.divulgavagas.com.br/paginacao/{page_number}")
            sleep(2)
            self.get_all_job_links("Ver vaga", "btn-primary", next_page=True)
        except:
            pass

    def send_resume(self, path_resume):
        jobs_links = self.get_all_job_links(
            "Ver vaga", "btn-primary", next_page=True)
        applications = self.check_applications()

        for link in jobs_links:
            link = link.replace("vaga-de-emprego", "envioCurriculo")
            if str(link) in applications:
                continue

            self.driver.get(link)
            self.driver.find_element(By.ID, "politica").click()
            input = self.driver.find_element(By.ID, "arquivo_1")
            input.send_keys(path_resume)
            sleep(2)
            self.driver.find_element(By.ID, "enviarCV").click()
            sleep(4)
            if not "Sentimos muito, mas não podemos liberar um novo envio de seu currículo para esta vaga." in self.driver.page_source:
                self.register_application(link)

    def register_application(self, link):
        with open("vagas_cadastradas.txt", "a") as file:
            file.write(f"{link}\n")

    def check_applications(self):
        applications = []
        with open("vagas_cadastradas.txt", "r") as file:
            for line in file.readlines():
                applications.append(line.strip())
        return applications

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    # Remover o zoom da página quando o navegador iniciar!!!
    find_jobs = FindJobs()
    find_jobs.search_for_jobs("https://www.divulgavagas.com.br", "Desenvolvedor")
    find_jobs.send_resume(path_resume="caminho_do_curriculo")
    find_jobs.close()
