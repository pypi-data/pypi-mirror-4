import pkg_resources

def get_resources(keyword):
  """
   Return the resource names 
  """
  resorces = pkg_resources.iter_entry_points(keyword)
  return [entry_point.name for entry_point in resorces]


def load_resources(keyword,resource_name):
  """
   Load a resource given the name
  """
  resources = pkg_resources.iter_entry_points(keyword)
  for r in resources:
    if(r.name == resource_name):
      return r.load()

  return None