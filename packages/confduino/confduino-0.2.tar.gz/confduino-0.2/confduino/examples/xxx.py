from confduino import exampallcreate
from confduino.libinstall import install_lib
from confduino.util import ConfduinoError
from entrypoint2 import entrypoint


@entrypoint
def upgrade_many(upgrade=True, create_examples_all=True):
    '''upgrade many libs

    source: http://arduino.cc/playground/Main/LibraryList

    you can set your arduino path if it is not default
    os.environ['ARDUINO_HOME'] = '/home/...'
    '''
    urls = set()

    def inst(url):
        print 'upgrading ' + url
        assert url not in urls
        urls.add(url)
        try:
            lib = install_lib(url, upgrade)
            print ' -> ', lib
        except Exception as e:
            print e

    inst('http://arduino.cc/playground/uploads/Code/TimedAction-1_6.zip')
    print 333
