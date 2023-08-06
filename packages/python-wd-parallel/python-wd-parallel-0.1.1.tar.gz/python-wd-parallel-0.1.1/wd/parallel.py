from selenium import webdriver
import unittest
import json
import multiprocessing

class Remote(object):
    """
    """

    def __init__(self, desired_capabilities=None, command_executor=None):
        """

        Arguments:
        - `desired_capabilities`: Array of desired_capabilities
        - `command_executor`: Id string
        """

        self._command_executor = command_executor

        #Set up all webdrivers
        if desired_capabilities != None:
            self._desired_capabilities = desired_capabilities


    def load_config_file(self, file):
        """Open json file and load config from it

        Arguments:
        - `file`: json file containing conf
        """
        fd = open(file)
        conf = json.load(fd)
        self._command_executor = self.__build_command_executor(conf['remote'])

        #self.__create_drivers(conf['desired'])
        self._desired_capabilities = conf['desired']

    def __build_command_executor(self, remote):
        return str('http://'+remote['username']+':'+remote['accessKey']+'@'+\
            remote['host']+':'+str(remote['port'])+'/wd/hub')

    def __create_drivers(self, desired_capabilities):
        """Create  webdrives from desired capabilities

        Arguments:
        - `self`:
        - `desired_capabilities`:
        """
        for d in desired_capabilities:
            kwargs = {}
            kwargs['desired_capabilities'] = d

            if command_executor != None:
                kwargs['command_executor'] = self._command_executor

            self._drivers += [webdriver.Remote(**kwargs)]

    def register(self, wd):
        try:
            self._drivers += [wd]
        except AttributeError as e:
            self._drivers = [wd]



def multiply(test):
    """Make test run in mutiple browsers
    """

    class SubTest(unittest.TestCase):
        def __init__(self, driver=None):
            self.driver = driver
            self.driver.implicitly_wait(30)

    def thread_func(f, dc=None, ce=None, driver=None, queue=None):

        if driver == None and dc != None:
            kwargs = {}
            kwargs['desired_capabilities'] = dc

            if ce != None:
                kwargs['command_executor'] = ce

            driver = webdriver.Remote(**kwargs)
            if queue != None:
                queue.put(driver)

        f(SubTest(driver))

    def wrapper(*args, **kwargs):
        threads = []
        queue = multiprocessing.Queue(len(args[0].drivers._desired_capabilities) + 1)
        i = 0
        nb_d = 0

        try:
            for d in args[0].drivers._drivers:
                t = multiprocessing.Process(target=thread_func, args=(test,), kwargs={'driver': d})
                t.start()
                threads += [t]
                i += 1

        except AttributeError:
            for c in args[0].drivers._desired_capabilities:
                t = multiprocessing.Process(target=thread_func, args=(test,),
                                            kwargs={
                                                'dc': c,
                                                'ce': args[0].drivers._command_executor,
                                                'queue': queue
                                            })
                t.start()
                threads += [t]
                i += 1

            while nb_d < len(args[0].drivers._desired_capabilities):
                driver = queue.get(block=True)
                args[0].drivers.register(driver)
                nb_d += 1

        for t in threads:
            t.join()
            i -= 1

    return wrapper
