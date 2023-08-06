
def chomp(string):
  """
  Removes the newline character from the end of the
  string if one is present.  Otherwise, it does nothing.
  """
  
  if string.endswith("\r\n"):
    return string[0:-2]
  elif string.endswith("\n"):
    return string[0:-1]
  elif string.endswith("\r"):
    return string[0:-1]
  else:
    return string