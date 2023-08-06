
import time
from DateTime import DateTime

def setEffectiveDate(object, event):
    """
    Sets the publication date to NOW on objects of type File
    """
    t = time.time()
    now = DateTime(t)
    object.setEffectiveDate(now)
    