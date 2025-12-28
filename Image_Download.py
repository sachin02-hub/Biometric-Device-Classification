import tempfile
from pyfingerprint.pyfingerprint import PyFingerprint


a=1 # Image counter (Modify if you want to start from a different number)


while True:
    ##Initialize the sensor
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

    ## Tries to read image and download it
    try:
        print('Place finger...')
        while ( f.readImage() == False ):
            pass

        print('Downloading image...')
        # Change this to create different folders for different sensors

        Folder = "Sensor1" 
        imageDestination =  tempfile.gettempdir() + '/' + Folder + '/Image' +str(a)+'.bmp'
        f.downloadImage(imageDestination)
        a+=1

        print('The image was saved to "' + imageDestination + '".')

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
