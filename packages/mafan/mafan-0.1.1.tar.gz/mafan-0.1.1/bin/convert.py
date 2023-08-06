"""
A command-line wrapper for mafan encoding
"""

from mafan import convert

if __name__ == '__main__':
  try:
    fname = sys.argv[1]
    if fname and os.path.isfile(fname):
      new_fname = convert(sys.argv[1])
      if new_fname:
        print "File created! %s" % new_fname
      else:
        print "Something went wrong, it seems."
    else:
      print "Error: File not found!"
      print "Usage: convert.py [filename]"
  except Exception, e:
    print "Usage: convert.py [filename]"
    print e