import os
import urllib.request
import time
import secrets

from colorama import Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
EXTENSION_PATH = os.getcwd() + '\metamaskExtension.crx'
EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'


class MetamaskSelenium:
    """MetamaskSelenium class for automating metamask using selenium"""
    
    def __init__(self, debug=False) -> None:
        """Constructor for MetamaskSelenium class

        Args:
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.debug = debug

    def log(self, message, color:any=None) -> bool:
        """Log messages with color

        Args:
            message (_type_): Message to log
            color (any, optional): Color, like Fore.RED. Defaults to None.

        Returns:
            bool: True
        """
        if not color:
            color = secrets.choice(COLORS)
        
        if self.debug:
            print(f"{color}[debug]{message}{Fore.RESET}")
            
        return True
        
    def downloadMetamaskExtension(self) -> bool:
        """Download metamask extension

        Returns:
            bool: True/False
        """
        self.log('Setting up metamask extension please wait...')
        url = 'https://xord-testing.s3.amazonaws.com/selenium/10.0.2_0.crx'
        urllib.request.urlretrieve(f"{url}", f"{os.getcwd()}/metamaskExtension.crx")
        return True


    def launchSeleniumWebdriver(self, driverPath:str=None):
        if driverPath:
            self.log('Driver path was provided, but I do not think it can be used anymore for selenium, sorry..')
        self.log(f"Path: {EXTENSION_PATH}")
        #self.log('path', EXTENSION_PATH)
        chrome_options = Options()
        chrome_options.add_extension(EXTENSION_PATH)
        self.driver = webdriver.Chrome(options=chrome_options)
        #time.sleep(5)
        self.log("Extension has been loaded")
        return self.driver


    def metamaskSetup(self, recoveryPhrase, password):
        self.driver.switch_to.window(self.driver.window_handles[0])

        time.sleep(100000)

        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Get Started')]").click()

        self.driver.find_element(By.XPATH,'//button[contains(text(), "Import wallet")]').click()
        self.driver.find_element(By.XPATH,'//button[contains(text(), "No Thanks")]').click()
        time.sleep(5)

        inputs = self.driver.find_elements(By.XPATH,'//input')
        inputs[0].send_keys(recoveryPhrase)
        inputs[1].send_keys(password)
        inputs[2].send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, '.first-time-flow__terms').click()
        self.driver.find_element(By.XPATH,'//button[contains(text(), "Import")]').click()

        time.sleep(5)

        self.driver.find_element(By.XPATH,'//button[contains(text(), "All Done")]').click()
        time.sleep(2)

        # closing the message popup after all done metamask screen
        self.driver.find_element(By.XPATH,'//*[@id="popover-content"]/div/div/section/header/div/button').click()
        time.sleep(2)
        self.log("Wallet has been imported successfully")
        time.sleep(10)


    def changeMetamaskNetwork(self, networkName):
        # opening network
        self.log("Changing network")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
        self.log("closing popup")
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="popover-content"]/div/div/section/header/div/button').click()

        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
        time.sleep(2)
        self.log("opening network dropdown")
        elem = self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div')
        time.sleep(2)
        all_li = elem.find_elements(By.TAG_NAME, "li")
        time.sleep(2)
        for li in all_li:
            text = li.text
            if (text == networkName):
                li.click()
                self.log(text, "is selected")
                time.sleep(2)
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(3)
                return
        time.sleep(2)
        self.log("Please provide a valid network name")

        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)

    def addMetamaskNetwork(self, network_name, rpc_url, chain_id, currency_symbol):
        self.log("Adding network")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get('chrome-extension://{}/home.html#settings/networks/add-network'.format(EXTENSION_ID))
        self.log('get add network page')

        self.driver.find_element(By.XPATH,'//button[contains(text(), "Add Network")]').click()

        inputs = self.driver.find_elements(By.XPATH,'//input')
        inputs[0].send_keys(network_name)
        inputs[1].send_keys(rpc_url)
        inputs[2].send_keys(chain_id)
        inputs[3].send_keys(currency_symbol)
        self.driver.find_element(By.XPATH,'//button[contains(text(), "Save")]').click()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)

    def connectToWebsite(self):
        time.sleep(3)

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(5)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]').click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
        time.sleep(3)
        self.log('Site connected to metamask')
        self.log(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)


    def confirmApprovalFromMetamask(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(10)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(10)
        # confirm approval from metamask
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]').click()
        time.sleep(12)
        self.log("Approval transaction confirmed")

        # switch to dafi
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)


    def rejectApprovalFromMetamask(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(10)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(10)
        # confirm approval from metamask
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[1]').click()
        time.sleep(8)
        self.log("Approval transaction rejected")

        # switch to dafi
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)
        self.log("Reject approval from metamask")


    def confirmTransactionFromMetamask(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(10)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(10)

        # # confirm transaction from metamask
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[2]').click()
        time.sleep(13)
        self.log("Transaction confirmed")

        # switch to dafi
        self.driver.switch_to.window(self.driver.window_handles[0])

        time.sleep(3)


    def rejectTransactionFromMetamask(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(5)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(5)
        # confirm approval from metamask
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[1]').click()
        time.sleep(2)
        self.log("Transaction rejected")

        # switch to web window
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)

    def addToken(self, tokenAddress):
        # opening network
        self.log("Adding Token")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
        self.log("closing popup")
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="popover-content"]/div/div/section/header/div/button').click()

        # driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
        # time.sleep(2)

        self.log("clicking add token button")
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div/div/div[3]/div/div[3]/button').click()
        time.sleep(2)
        # adding address
        self.driver.find_element(By.ID, "custom-address").send_keys(tokenAddress)
        time.sleep(10)
        # clicking add
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div[2]/div[2]/footer/button[2]').click()
        time.sleep(2)
        # add tokens
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div[3]/footer/button[2]').click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)

    def signConfirm(self):
        self.log("sign")
        time.sleep(3)

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(5)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]').click()
        time.sleep(1)
        # driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
        # time.sleep(3)
        self.log('Sign confirmed')
        self.log(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)


    def signReject(self):
        self.log("sign")
        time.sleep(3)

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
        time.sleep(5)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[1]').click()
        time.sleep(1)
        # driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
        # time.sleep(3)
        self.log('Sign rejected')
        self.log(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(3)
