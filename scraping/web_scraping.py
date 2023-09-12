import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

current_file = os.path.basename(__file__)

class WebScraping ():
    """
    Class to manage and configure web browser
    """

    def __init__(self, headless=False, time_out=0,
                 proxy_server="", proxy_port="", proxy_user="", proxy_pass="",
                 chrome_folder="", user_agent=False, 
                 download_folder="", extensions=[], incognito=False, experimentals=True,
                 start_killing=False, start_openning:bool=True, width:int=1280, height:int=720,
                 mute:bool=True):
        """ Constructor of the class

        Args:
            headless (bool, optional): Hide (True) or Show (False) the google chrome window. Defaults to False.
            time_out (int, optional): Wait time to load each page. Defaults to 0.
            proxy_server (str, optional): Proxy server or host to use in the window. Defaults to "".
            proxy_port (str, optional): Proxy post to use in the window. Defaults to "".
            proxy_user (str, optional): Proxy user to use in the window. Defaults to "".
            proxy_pass (str, optional): Proxy password to use in the window. Defaults to "".
            chrome_folder (str, optional): folder with user google chrome data. Defaults to "".
            user_agent (bool, optional): user agent to setup to chrome. Defaults to False.
            download_folder (str, optional): Default download folder. Defaults to "".
            extensions (list, optional): Paths of extensions in format .crx, to install. Defaults to [].
            incognito (bool, optional): Open chrome in incognito mode. Defaults to False.
            experimentals (bool, optional): Activate the experimentals options. Defaults to True.
            start_killing (bool, optional): Kill chrome process before start. Defaults to False.
            start_openning (bool, optional): Open chrome window before start. Defaults to True.
            width (int, optional): Width of the window. Defaults to 1280.
            height (int, optional): Height of the window. Defaults to 720.
            mute (bool, optional): Mute the audio of the window. Defaults to True.
        """

        self.basetime = 1

        # variables of class
        self.current_folder = os.path.dirname(__file__)
        self.__headless__ = headless
        self.__proxy_server__ = proxy_server
        self.__proxy_port__ = proxy_port
        self.__proxy_user__ = proxy_user
        self.__proxy_pass__ = proxy_pass
        self.__pluginfile__ = os.path.join(self.current_folder, 'proxy_auth_plugin.zip')
        self.__chrome_folder__ = chrome_folder
        self.__user_agent__ = user_agent
        self.__download_folder__ = download_folder
        self.__extensions__ = extensions
        self.__incognito__ = incognito
        self.__experimentals__ = experimentals
        self.__start_openning__ = start_openning
        self.__width__ = width
        self.__height__ = height
        self.__mute__ = mute
        
        self.__web_page__ = None

        # Kill chrome from CMD in donwows
        if start_killing:
            print("\nTry to kill chrome...")
            command = 'taskkill /IM "chrome.exe" /F'
            os.system(command)
            print("Ok\n")

        # Create and instance of the web browser
        if self.__start_openning__:
            self.__set_browser_instance__()

        # Get current file name
        self.current_file = os.path.basename(__file__)

        # Set time out
        if time_out > 0:
            self.driver.set_page_load_timeout(time_out)

    def set_cookies (self, cookies: dict):
        """ Get list of cookies, formatted, from 'cookies.json' file

        Args:
            cookies (dict): list of cookies generated by 'EditThisCookie' extension
        """

        # Format cookies
        cookies_formatted = []
        for cookie in cookies:

            # rename expiration date
            if "expirationDate" in cookie:
                cookie["expiry"] = int(cookie["expirationDate"])
                del cookie["expirationDate"]

            # remove unnecessary keys
            if cookie.get ("hostOnly"):
                del cookie["hostOnly"]
            
            if cookie.get ("sameSite"):
                del cookie["sameSite"]
            
            if cookie.get ("session"):
                del cookie["session"]
            
            if cookie.get ("storeId"):
                del cookie["storeId"]
            
            if cookie.get ("id"):
                del cookie["id"]

            # Fix domain
            if cookie.get("domain") and cookie["domain"].startswith("."):
                cookie["domain"] = cookie["domain"][1:]

            cookies_formatted.append(cookie)

        for cookie in cookies_formatted:
            try:
                self.driver.add_cookie(cookie)
            except:
                pass

    def __set_browser_instance__(self):
        """
        Open and configure browser
        """

        # Disable logs
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

        # Configure browser
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--output=/dev/null')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--safebrowsing-disable-download-protection")

        # Experimentals
        if self.__experimentals__:
            options.add_experimental_option(
                'excludeSwitches', ['enable-logging', "enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

        # screen size
        options.add_argument(f"--window-size={self.__width__},{self.__height__}")
        
        # headless mode
        if self.__headless__:
            options.add_argument("--headless=new")
            
        if self.__mute__:
            options.add_argument("--mute-audio")

        # Set proxy without autentication
        if (self.__proxy_server__ and self.__proxy_port__
                and not self.__proxy_user__ and not self.__proxy_pass__):

            proxy = f"{self.__proxy_server__}:{self.__proxy_port__}"
            options.add_argument(f"--proxy-server={proxy}")

        # Set proxy with autentification
        # seleniumwire_options = {}
        if (self.__proxy_server__ and self.__proxy_port__
                and self.__proxy_user__ and self.__proxy_pass__):
            
            self.__create_proxy_extesion__()
            options.add_extension(self.__pluginfile__)

        # Set chrome folder
        if self.__chrome_folder__:
            options.add_argument(f"--user-data-dir={self.__chrome_folder__}")

        # Set default user agent
        if self.__user_agent__:
            options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')

        if self.__download_folder__:
            prefs = {"download.default_directory": f"{self.__download_folder__}",
                     "download.prompt_for_download": "false",
                     'profile.default_content_setting_values.automatic_downloads': 1,
                     'profile.default_content_settings.popups': 0,
                     "download.directory_upgrade": True,
                     "plugins.always_open_pdf_externally": True,
                     "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                     'download.extensions_to_open': 'xml',
                     'safebrowsing.enabled': True
                     }

            options.add_experimental_option("prefs", prefs)

        if self.__extensions__:
            for extension in self.__extensions__:
                options.add_extension(extension)

        if self.__incognito__:
            options.add_argument("--incognito")

        if self.__experimentals__:
            options.add_argument(
                "--disable-blink-features=AutomationControlled")

        # Set configuration to  and create instance
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)

    def __create_proxy_extesion__(self):
        """Create a proxy chrome extension"""

        # plugin data
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.__proxy_server__, self.__proxy_port__, self.__proxy_user__, self.__proxy_pass__)

        # Compress file
        with zipfile.ZipFile(self.__pluginfile__, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

    def screenshot(self, base_name):
        """
        Take a sreenshot of the current browser window
        """

        if str(base_name).endswith(".png"):
            file_name = base_name
        else:
            file_name = f"{base_name}.png"

        self.driver.save_screenshot(file_name)

    def full_screenshot(self, path: str):
        # Ref: https://stackoverflow.com/a/52572919/
        original_size = self.driver.get_window_size()
        required_width = self.driver.execute_script(
            'return document.body.parentNode.scrollWidth')
        required_height = self.driver.execute_script(
            'return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(required_width, required_height)
        # driver.save_screenshot(path)  # has scrollbar
        self.screenshot(path)  # avoids scrollbar
        self.driver.set_window_size(
            original_size['width'], original_size['height'])

    def get_browser(self):
        """
        Return the current instance of web browser
        """

        return self.driver

    def end_browser(self):
        """
        End current instance of web browser
        """

        self.driver.quit()

    def __reload_browser__(self):
        """
        Close the current instance of the web browser and reload in the same page
        """

        self.end_browser()
        self.driver = self.get_browser()
        self.driver.get(self.__web_page__)

    def send_data(self, selector, data):
        """
        Send data to specific input fill
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(data)

    def click(self, selector):
        """
        Send click to specific element in the page
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.click()

    def wait_load(self, selector, time_out=10, refresh_back_tab=-1):
        """
        Wait to page load an element
        """

        total_time = 0

        while True:
            if total_time < time_out:
                total_time += 1
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    elem.text
                    break
                except:

                    # Wait time or refresh page
                    if refresh_back_tab != -1:
                        self.refresh_selenium(back_tab=refresh_back_tab)
                    else:
                        time.sleep(self.basetime)

                    continue
            else:
                raise Exception(
                    "Time out exeded. The element {} is not in the page".format(selector))

    def wait_die(self, selector, time_out=10):
        """
        Wait to page vanish and element
        """

        total_time = 0

        while True:
            if total_time < time_out:
                total_time += 1
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    elem.text
                    time.sleep(self.basetime)
                    continue
                except:
                    break
            else:
                raise Exception(
                    "Time out exeded. The element {} is until in the page".format(selector))

    def get_text(self, selector):
        """
        Return text for specific element in the page
        """

        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            return elem.text
        except Exception as err:
            # print (err)
            return None

    def get_texts(self, selector):
        """
        Return a list of text for specific selector
        """

        texts = []

        elems = self.driver.find_elements(By.CSS_SELECTOR, selector)

        for elem in elems:
            try:
                texts.append(elem.text)
            except:
                continue

        return texts

    def set_attrib(self, selector, attrib_name, attrib_value):
        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script(
            f"arguments[0].setAttribute('{attrib_name}', '{attrib_value}');", elem)

    def get_attrib(self, selector, attrib_name):
        """
        Return the class value from specific element in the page
        """

        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            return elem.get_attribute(attrib_name)
        except:
            return None

    def get_attribs(self, selector, attrib_name, allow_duplicates=True, allow_empty=True):
        """
        Return the attributes value from specific element in the page
        """

        attributes = []
        elems = self.driver.find_elements(By.CSS_SELECTOR, selector)

        for elem in elems:

            try:
                attribute = elem.get_attribute(attrib_name)

                # Skip duplicates in not duplicate mode
                if not allow_duplicates and attribute in attributes:
                    continue

                # Skip empty results in not ampty mode
                if not allow_empty and attribute.strip() == "":
                    continue

                attributes.append(attribute)

            except:
                continue

        return attributes

    def get_elem(self, selector):
        """
        Return an specific element in the page
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        return elem

    def get_elems(self, selector):
        """
        Return a list of specific element in the page
        """

        elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return elems

    def set_page_js(self, web_page, new_tab=False):
        """Open page with js, in current or new tab
        """

        self.__web_page__ = web_page

        if new_tab:
            script = f'window.open("{web_page}");'
        else:
            script = f'window.open("{web_page}").focus();'

        print(script)

        self.driver.execute_script(script)

    def set_page(self, web_page, time_out=0, break_time_out=False):
        """
        Update the web page in browser
        """

        try:

            self.__web_page__ = web_page

            # Save time out when is greader than 0
            if time_out > 0:
                self.driver.set_page_load_timeout(time_out)

            self.driver.get(self.__web_page__)

        # Catch error in load page
        except Exception as err:

            # Raise error
            if break_time_out:
                raise Exception(f"Time out to load page: {web_page}")

            # Ignore error
            else:
                self.driver.execute_script("window.stop();")

    def click_js(self, selector):
        """
        Send click with js, for hiden elements
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script("arguments[0].click();", elem)

    def select_drop_down_index(self, selector, index):
        """
        Select specific elemet (with number) in a drop down elemet
        """

        select_elem = Select(self.get_elem(selector))
        select_elem.select_by_index(index)

    def select_drop_down_text(self, selector, text):
        """ Select a value in a drop down eleme (Select elem)"""

        select_elem = Select(self.get_elem(selector))
        select_elem.select_by_visible_text(text)

    def go_bottom(self, selector: str = "body"):
        """
        Go to the end of the page, sending keys
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(Keys.CONTROL + Keys.END)

    def go_top(self, selector: str = "body"):
        """
        Go to the start of the page, sending keys
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(Keys.CONTROL + Keys.UP)

    def go_down(self, selector: str = "body"):
        """
        advance to down, in the page, sending keys
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(Keys.PAGE_DOWN)

    def go_up(self, selector: str = "body"):
        """
        Return to up, in page, sending keys
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(Keys.PAGE_UP)

    def switch_to_main_frame(self):
        """
        Switch to the main contecnt of the page
        """

        self.driver.switch_to.default_content()

    def switch_to_frame(self, frame_selector):
        """
        Switch to iframe inside the main content
        """

        frame = self.get_elem(frame_selector)
        self.driver.switch_to.frame(frame)

    def open_tab(self):
        """
        Create new empty tab in browser
        """

        self.driver.execute_script("window.open('');")

    def close_tab(self):
        """
        Clase the current tab in the browser
        """

        self.driver.close()

    def switch_to_tab(self, number):
        """
        Switch to specific number of tab
        """

        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[number])

    def refresh_selenium(self, time_units=1, back_tab=0):
        """
        Refresh the selenium data, creating and closing a new tab
        """

        # Open new tab and go to it
        self.open_tab()
        self.switch_to_tab(len(self.driver.window_handles)-1)

        # Wait time
        time.sleep(self.basetime * time_units)

        # Close new tab and return to specific tab
        self.close_tab()
        self.switch_to_tab(back_tab)

        # Wait time
        time.sleep(self.basetime * time_units)

    def save_page(self, file_html):
        """ Save current page in local file"""
        page_html = self.driver.page_source
        current_folder = os.path.dirname(__file__)
        page_file = open(os.path.join(
            current_folder, file_html), "w", encoding='utf-8')
        page_file.write(page_html)
        page_file.close()

    def zoom(self, percentage=50):
        """ Custom page zoom with JS"""

        script = f"document.body.style.zoom='{percentage}%'"
        self.driver.execute_script(script)

    def kill(self):
        """ Detect and close all tabs """
        tabs = self.driver.window_handles
        for _ in tabs:
            self.switch_to_tab(0)
            self.end_browser()

    def scroll(self, selector, scroll_x, scroll_y):
        """ Scroll X or Y in specific element of the page """

        elem = self.get_elem(selector)
        self.driver.execute_script("arguments[0].scrollTo(arguments[1], arguments[2])",
                                   elem,
                                   scroll_x,
                                   scroll_y)

    def __wait_load__(self, selector, back_tab):
        """ Wait until the table is loaded """

        while True:
            elem_text = self.get_text(selector)
            if elem_text:
                break
            else:
                time.sleep(0.5)
