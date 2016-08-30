from splinter import Browser
from PIL import Image
import pytesseract
# import tesseract

def openBrowser():
    # api = tesseract.TessBaseAPI()
    # api.Init(".", "jpn", tesseract.OEM_DEFAULT)
    # api.SetPageSegMode(tesseract.PSM_AUTO)
    #
    # mImgFile = "pic.jpg"
    # print mImgFile
    # mBuffer = open(mImgFile, "rb").read()
    #
    # result = tesseract.ProcessPagesBuffer(mBuffer, len(mBuffer), api)
    # print result




    image = Image.open('pic.jpg')
    image.load()
    print image.filename
    # image.show()
    captcha = pytesseract.image_to_string(image)
    print captcha

if __name__ == '__main__':
    openBrowser()
