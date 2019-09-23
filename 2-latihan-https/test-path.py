import sys, os


full_path1 = "c:\\users\\creator\\mypy\\oop\\2-latihan-https\\index.html"
full_path2 = "c:\\users\\creator\\mypy\\oop\\2-latihan-https"

print('sys.argv[0] =', sys.argv[0])
pathname = os.path.dirname(sys.argv[0])
print('path =', pathname)
fullpath = os.path.normcase(os.path.abspath(pathname) + '/')
print('full path =', fullpath)
print(os.path.exists(fullpath))

print(os.path.isdir(fullpath))
print(os.path.isfile(full_path2))
