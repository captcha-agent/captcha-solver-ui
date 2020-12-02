from selenium import webdriver
from configparser import ConfigParser
from time import sleep
from requests import post

conf = ConfigParser()
conf.sections()
conf.read('conf.ini')

repetitions = conf.getint('getData', 'repetitions')
iteration = conf.getint('getData', 'iterations')
restart_limit = conf.getint('getData', 'restartLimit')
headless = conf.getboolean('getData', 'headless')

restart_counter = 0
for _ in range(repetitions):
    try:
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        driver.get('https://patrickhlauke.github.io/recaptcha/')

        # show captcha
        sleep(2)
        driver.find_element_by_xpath('/html/body/div[1]/div/div/iframe').click()

        # switch to frame
        sleep(2)
        driver.switch_to.frame(driver.find_element_by_xpath('/html/body/div[2]/div[4]/iframe'))

        j = 0
        while True:
            # get image
            img = driver.find_element_by_xpath(
                '//*[@id="rc-imageselect-target"]/table/tbody/tr[1]/td[1]/div/div[1]/img')

            # get image properties
            url = img.get_attribute('src')
            size = int(img.get_attribute('class').rsplit('-', 1)[1][0])
            typ = driver.find_element_by_xpath('//*[@id="rc-imageselect"]/div[2]/div[1]/div[1]/div/strong').text

            # submit to captcha handler
            print(url)

            res = post('http://194.209.154.139:38016/captcha/new', json={'url': url,
                                                                         'size': size,
                                                                         'typ': typ})
            print('%02d' % j, res)

            # reload captcha
            if iteration > j:
                driver.find_element_by_id('recaptcha-reload-button').click()
                sleep(1)
                j += 1
            else:
                break

    except:
        if restart_counter == restart_limit:
            print('--- Session expired ---')
            quit()

        restart_counter += 1
        print('--- Driver restart ---')
        continue

    restart_counter = 0
    # close browser
    driver.close()
