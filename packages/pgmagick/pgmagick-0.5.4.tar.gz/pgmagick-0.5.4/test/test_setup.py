import sys
print __file__
sys.path.append('.')
from setup import get_version_from_devheaders

print get_version_from_devheaders('.')
