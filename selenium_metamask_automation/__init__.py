import time
import secrets
import pyperclip
import selenium.common

from colorama import Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

COLORS = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE,
]
# EXTENSION_PATH = os.getcwd() + '\metamaskExtension.crx'
EXTENSION_PATH = "metamask-chrome-11.14.4.zip"
EXTENSION_ID = "nkbihfbeogaeaoehlefnkodbefgpgknn"


class MetamaskSelenium:
    """MetamaskSelenium class for automating metamask using selenium"""

    def __init__(self, debug=False) -> None:
        """Constructor for MetamaskSelenium class

        Args:
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.debug = debug

    def log(self, message, color: any = None) -> bool:
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
            print(f"{color}[debug] {message}{Fore.RESET}")

        return True

    def launchSeleniumWebdriverAndLoadMetamask(
        self, driverPath: str = None
    ) -> webdriver.Chrome:
        """Launch selenium webdriver and load metamask extension

        Args:
            driverPath (str, optional): Chrome driver exe path. Defaults to None.

        Returns:
            webdriver.Chrome: Selenium webdriver
        """
        if driverPath:
            self.log(
                "Driver path was provided, but I do not think it can be used anymore for selenium, sorry.."
            )

        self.log(f"Path: {EXTENSION_PATH}")
        # self.log('path', EXTENSION_PATH)
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_extension(EXTENSION_PATH)
        self.driver = webdriver.Chrome(options=chrome_options)
        # time.sleep(5)
        self.log("Extension has been loaded")
        return self.driver

    def waitAndClick(
        self, byTag: any = By.ID, tagValue: str = None, wait: int = 10
    ) -> bool:
        """Wait and click on element

        Args:
            byTag (any, optional): By.ID, By.XPATH, etc. Defaults to By.ID.
            tagValue (str, optional): Tag value, like 'onboarding__terms-checkbox'. Defaults to None.
            wait (int, optional): Wait time. Defaults to 10.

        Returns:
            bool: True/False
        """
        try:
            element = WebDriverWait(self.driver, wait).until(
                EC.element_to_be_clickable((byTag, tagValue))
            )
            time.sleep(1)
            element.click()
            return True
        
        except selenium.common.exceptions.ElementClickInterceptedException:
            time.sleep(30)
            self.driver.refresh()
            return False
        
        except Exception as e:
            self.log(f"Error While Waiting to Click: {e}")
            return False

    def importSeedToMetamask(self, recoveryPhrase: str, password: str) -> bool:
        """Import seed to metamask

        Args:
            recoveryPhrase (str): Recovery phrase, 12~ words
            password (str): Password for metamask

        Returns:
            bool: True/False
        """
        for rt in range(3):
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])
                break
            except Exception:
                if rt == 2:
                    print("failed to switch to metamask window")
                    return False

        self.waitAndClick(byTag=By.ID, tagValue="onboarding__terms-checkbox")
        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[contains(text(), "Import an existing wallet")]',
        )
        self.waitAndClick(
            byTag=By.XPATH, tagValue='//button[contains(text(), "I agree")]'
        )

        inputs = self.driver.find_elements(By.XPATH, "//input")
        pyperclip.copy(recoveryPhrase)  # Probably unreliable lol
        inputs[0].send_keys(Keys.CONTROL, "v")

        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[contains(text(), "Confirm Secret Recovery Phrase")]',
        )

        passwordInputs = self.driver.find_elements(By.XPATH, "//input")

        for pwInput in passwordInputs:
            pwInput.send_keys(password)

        self.waitAndClick(
            byTag=By.XPATH, tagValue='//input[@data-testid="create-password-terms"]'
        )
        self.waitAndClick(
            byTag=By.XPATH, tagValue='//button[contains(text(), "Import my wallet")]'
        )
        self.waitAndClick(
            byTag=By.XPATH, tagValue='//button[contains(text(), "Got it")]'
        )
        #self.waitAndClick(
        #    byTag=By.XPATH, tagValue='//button[contains(text(), "Got it")]'
        #)
        self.waitAndClick(byTag=By.XPATH, tagValue='//button[contains(text(), "Next")]')
        self.waitAndClick(byTag=By.XPATH, tagValue='//button[contains(text(), "Done")]')
        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[contains(text(), "Enable")]',
        )

        # <span class="mm-box mm-text multichain-account-picker__label mm-text--body-md mm-text--font-weight-bold mm-text--ellipsis mm-box--color-text-default">Account 1</span>
        # if this element exists, then we have successfully imported the wallet

        if self.driver.find_elements(By.XPATH, '//span[contains(text(), "Account 1")]'):
            self.log("Wallet has been imported successfully")
            
            # Open accoutn details to parse addy
            # <button class="mm-box mm-button-icon mm-button-icon--size-sm mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-icon-default mm-box--background-color-transparent mm-box--rounded-lg" aria-label="Account options" data-testid="account-options-menu-button"><span class="mm-box mm-icon mm-icon--size-sm mm-box--display-inline-block mm-box--color-inherit" style="mask-image: url(&quot;./images/icons/more-vertical.svg&quot;);"></span></button>
            # <button class="menu-item" data-testid="account-list-menu-details"><span class="mm-box mm-icon mm-icon--size-sm mm-box--margin-right-2 mm-box--display-inline-block mm-box--color-inherit" style="mask-image: url(&quot;./images/icons/scan-barcode.svg&quot;);"></span><div><div>Account details</div></div></button>
            # <button class="mm-box mm-text mm-button-base mm-button-base--size-sm multichain-address-copy-button multichain-address-copy-button__address--wrap mm-text--body-sm mm-box--padding-0 mm-box--padding-right-4 mm-box--padding-left-4 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-default mm-box--background-color-primary-muted mm-box--rounded-pill" data-testid="address-copy-button-text"><span class="mm-box mm-text mm-text--inherit mm-box--color-primary-default"><div class="mm-box mm-box--display-flex">0x31922557f488f78CD34d56595FC02E153adc8cBA</div></span><span class="mm-box mm-icon mm-icon--size-sm mm-box--margin-inline-start-1 mm-box--display-inline-block mm-box--color-inherit" style="mask-image: url(&quot;./images/icons/copy.svg&quot;);"></span></button>
            
            # click button containing text No thanks
            
            self.waitAndClick(
                byTag=By.XPATH,
                tagValue='//button[contains(text(), "No thanks")]',
            )
            
            # first button to open ... menu
            self.waitAndClick(
                byTag=By.XPATH,
                tagValue='//button[@data-testid="account-options-menu-button"]',
            )
            
            # 2nd button to click Open Accoutn Details
            self.waitAndClick(
                byTag=By.XPATH,
                tagValue='//button[@data-testid="account-list-menu-details"]',
            )
            
            # find address text in page source and store it in mongo
            addy = self.driver.page_source.split('<div class="mm-box mm-box--display-flex">')[1].split('</div>')[0]
            
            print(f'found {addy}')
            
            return {"success": True, "addy": addy}
        


        
        self.log("Wallet import failed")
        return False

    def confirmWebsiteNetworkAddition(self):
        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        # <button class="button btn--rounded btn-primary" data-testid="confirmation-submit-button">Approve</button>

        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="confirmation-submit-button"]',
        )

        return True

    def confirmWebsiteSwitchNetwork(self):
        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        # <button class="button btn--rounded btn-primary" data-testid="confirmation-submit-button">Switch Network</button>

        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="confirmation-submit-button"]',
        )

        return True

    def waitForMetamaskWindow(self, switch=True):
        for i in range(5):
            if len(self.driver.window_handles) < 3:
                if i == 4:
                    self.log("Failed waiting for metamask")
                    return False
                time.sleep(3)
            else:
                if switch:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                return True

    def connectToWebsite(self):
        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next">Next</button>
        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
        )

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next">Confirm</button>
        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
        )

        return True

    def confirmNetworkChange(self):
        # <button class="mm-box mm-text mm-button-base mm-button-base--size-md footer__button mm-button-primary mm-text--body-md-medium mm-box--padding-0 mm-box--padding-right-4 mm-box--padding-left-4 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-inverse mm-box--background-color-primary-default mm-box--rounded-pill"><span class="mm-box mm-text mm-text--inherit mm-box--color-primary-inverse"><h6 class="mm-box mm-text mm-text--body-sm mm-box--color-inherit">Got it</h6></span></button>

        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        self.waitAndClick(byTag=By.XPATH, tagValue='//h6[contains(text(), "Got it")]')

        return True

    def hitNextMetaMask(self):
        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next">Next</button>

        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
        )

        return True

    def changeSpendingCap(self):
        # <input class="mm-box mm-text mm-input mm-input--disable-state-styles mm-text-field__input mm-text--body-md mm-box--margin-0 mm-box--padding-0 mm-box--padding-right-2 mm-box--padding-left-4 mm-box--padding-inline-end-4 mm-box--color-error-default mm-box--background-color-transparent mm-box--border-style-none" autocomplete="off" id="custom-spending-cap" placeholder="Enter a number" type="text" data-testid="custom-spending-cap-input" focused="false" value="115792089237316195423570985008687907853269984665640564039457584007913129.639935">

        if not self.waitForMetamaskWindow():
            return False

        self.driver.switch_to.window(self.driver.window_handles[2])

        # <button class="mm-box mm-text mm-button-base mm-button-link mm-button-link--size-auto mm-text--body-md-medium mm-box--padding-0 mm-box--padding-right-0 mm-box--padding-left-0 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-default mm-box--background-color-transparent">Edit</button>

        # self.waitAndClick(byTag=By.XPATH, tagValue='//button[contains(text(), "Edit")]')

        # (By.XPATH, '//input[@data-testid="custom-spending-cap-input"]')

        spendingCapInput = self.waitAndFind(
            byTag=By.XPATH, tagValue='//input[@data-testid="custom-spending-cap-input"]'
        )

        spendingCapInput.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        spendingCapInput.send_keys("10000")

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next">Next</button>
        self.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
        )

        # <button class="mm-box mm-text mm-button-base mm-button-link mm-button-link--size-auto mm-text--body-md-medium mm-box--padding-0 mm-box--padding-right-0 mm-box--padding-left-0 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-default mm-box--background-color-transparent">I want to proceed anyway</button>
        #self.waitAndClick(
        #    byTag=By.XPATH,
        #    tagValue='//button[contains(text(), "I want to proceed anyway")]',
        #)

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next" disabled="">Approve</button>
        # self.waitAndClick(byTag=By.XPATH, tagValue='//button[@data-testid="page-container-footer-next"]')

        return True

    def waitAndFind(self, byTag: any = By.ID, tagValue: str = None, wait: int = 10):
        """Like wait and click, but waits until element is found and returns it"""

        element = WebDriverWait(self.driver, wait).until(
            EC.presence_of_element_located((byTag, tagValue))
        )

        return element

    def approveTransaction(self):
        # <div>Successfully approved</div>

        self.driver.switch_to.window(self.driver.window_handles[0])

        if self.waitAndFind(
            byTag=By.XPATH,
            tagValue='//div[contains(text(), "Successfully approved")]',
            wait=45
        ):
            return True
        
        return False
    
    def approveApproval(self):
        metamaskWindowAppeared = self.metamaskSelenium.waitForMetamaskWindow()

        if not metamaskWindowAppeared:
            return False

        # Switch to 2 window handle

        self.selenium.switch_to.window(self.selenium.window_handles[2])

        # <h6 class="mm-box mm-text mm-text--body-sm mm-box--color-inherit">Got it</h6>

        self.metamaskSelenium.waitAndClick(
            byTag=By.XPATH, tagValue='//h6[contains(text(), "Got it")]', wait=10
        )

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next">Next</button>

        self.metamaskSelenium.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
            wait=10,
        )

        # <button class="button btn--rounded btn-primary page-container__footer-button" data-testid="page-container-footer-next" disabled="">Approve</button>

        self.metamaskSelenium.waitAndClick(
            byTag=By.XPATH,
            tagValue='//button[@data-testid="page-container-footer-next"]',
            wait=10,
        )

        return True

    def waitAndSendKeys(
        self, keys: str, tagValue: str, byTag: any = By.ID, wait: int = 10
    ) -> bool:
        element = WebDriverWait(self.driver, wait).until(
            EC.presence_of_element_located((byTag, tagValue))
        )

        element.clear()
        element.send_keys(keys)

        return True
