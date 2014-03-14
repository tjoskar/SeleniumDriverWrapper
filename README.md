SeleniumDriverWrapper
=====================

A wrapper for Selenium WebDriver (Selenium 2) in python.

Instalation: ``` pip install git+git://github.com/tjoskar/SeleniumDriverWrapper@master ```

### Example
```python
from seleniumdriverwrapper import Driver

I = Driver(timeout=5, poll=0.5, delay=0, screenshot_on_failure=False) # Default values
I.take_screenshot_on_failure = True

I.connect_local(driver_name='firefox')
I.find_by_css('#link')
I.click()
I.die()
```

### API
See latest api [here](https://github.com/tjoskar/SeleniumDriverWrapper/blob/master/seleniumdriverwrapper/driver.py)
