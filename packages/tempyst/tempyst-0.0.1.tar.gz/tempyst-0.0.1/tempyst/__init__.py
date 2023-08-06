import os
import shutil
import tempfile

class _TempFolderManager(object):
  def __init__(self):
    self.__managed = []


  def register(self, path):
    self.__managed.append(path)

  def unregister(self, path):
    import os
    import shutil
    
    if path in self.__managed:
      self.__managed.remove(path)


    if os.path.exists(path):
      try:
        shutil.rmtree(path)
      except Exception:
        pass
    else:
      pass

  def __del__(self):
    folders = self.__managed[:]
    for f in folders:
      self.unregister(f)


_temp_folder_manager = _TempFolderManager()


class temp_folder(object):
  def __init__(self, suffix='', prefix='tmp', dir=None):
    self.name = tempfile.mkdtemp(suffix, prefix, dir)
    _temp_folder_manager.register(self.name)

  def __enter__(self):
    return self.name

  def __exit__(self, type, value, traceback):
    _temp_folder_manager.unregister(self.name)

