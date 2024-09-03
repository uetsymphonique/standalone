import os, shutil, tempfile


APP_ROOT = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(APP_ROOT, '../tmp')
PLUGIN_ROOT = os.path.join(APP_ROOT, '../..')

paths_to_zip = ['/home/stupidhacker/caldera/plugins/standalones/tmp']
temp_dir = tempfile.mkdtemp()
zip_file_path = os.path.join(temp_dir, 'files.zip')
shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', root_dir='/', base_dir=None, base_dir_list=paths_to_zip)
print(temp_dir)