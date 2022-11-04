from django.test import TestCase
import time
start=time.time()
for i  in range(100000000):
    pass
end=time.time()
print(end-start)
# Create your tests here.
