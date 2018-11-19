from django.test import TestCase

# Create your tests here.
from bs4 import BeautifulSoup

s = '<h1>hello</h1>'
soup=BeautifulSoup(s,'html.parser')
print(soup.text)
