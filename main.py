import sys
import os
import json
import subprocess
import shutil


def file_exists(f):
  try:
    os.stat(f)
    return True
  except FileNotFoundError:
    return False


def create_folder(config):
  if 'projects_dir' not in config:
    raise Exception(
      'projects_dir field unset! Set it to the path of the directory that will contain (all) your projects.')
  if file_exists(config['projects_dir']):
    print('NOOP: Folder already exists')
  else:
    os.makedirs(config['projects_dir'])
    print('OP: Created the folder')


def is_git_repo(path):
  if not file_exists(path):
    return False
  cwd = os.getcwd()
  os.chdir(path)
  git_status = subprocess.run(['git', 'status'], shell=True)
  os.chdir(cwd)
  return git_status.returncode == 0


def clone_git(config):
  if 'project_name' not in config:
    raise Exception('project_name field unset! Set it to the name of the project (should be a valid folder name).')
  os.chdir(config['projects_dir'])
  if is_git_repo(config['project_name']):
    print('NOOP: Repo already cloned')
    os.chdir(config['project_name'])
    return
  if file_exists(config['project_name']):
    raise Exception('The project is in a weird state, please manually clean up and rerun the script.')

  git_clone = subprocess.run(
    ['git', 'clone', '--recursive', config['git_url'], config['project_name']], shell=True)
  if git_clone.returncode != 0:
    raise Exception('git clone failed!')
  print('OP: Cloned the repo')
  os.chdir(config['project_name'])


def clone_submodules(config):
  submodules = dict(config['submodules'])
  if 'godot-cpp' not in submodules:
    submodules['godot-cpp'] = {
      'url': 'https://github.com/godotengine/godot-cpp',
      'branch': '3.x'
    }
  for name, data in submodules.items():
    if 'is_cmake' in data and data['is_cmake']:
      if 'subdirectories' not in config:
        config['subdirectories'] = []
      config['subdirectories'].append(name)
    if is_git_repo(name):
      print(f'NOOP: Submodule {name} already exists')
      continue
    url = data['url']
    branch = data['branch'] if 'branch' in data else 'origin/master'
    spres = subprocess.run(['git', 'submodule', 'add', '-b', branch, url, name], shell=True)
    if spres.returncode != 0:
      raise Exception(f'Cloning {name} failed!')
    os.chdir(name)
    spres = subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'], shell=True)
    if spres.returncode != 0:
      raise Exception(f'Submodule update for {name} failed!')
    os.chdir('..')
    print(f'OP: Submodule {name} created')


def build_gdnative(config):
  if file_exists('godot-cpp/bin'):
    print(f'NOOP: godot-cpp already built')
    return
  os.chdir('godot-cpp')
  # TODO: detect OS and do it for linux (it was more complicated than just platform=linux)
  # TODO: uncomment below
  for target in ['debug', 'release']:
    # This doesn't cache the output files for some reason and recompiles each time. Ok for production usage, not for dev
    subprocess.run(['scons', 'platform=windows', 'generate_bindings=yes', 'bits=64', f'target={target}', '-j16'],
                   shell=True)
  os.chdir('..')
  print(f'OP: godot-cpp built')


def create_dir_if_not_exists(dst):
  if file_exists(dst):
    print(f'NOOP: {dst} already exists')
  else:
    os.mkdir(dst)
    print(f'OP: Created folder {dst}')


def copy_if_not_exists(src, dst):
  if file_exists(dst):
    print(f'NOOP: {dst} already exists')
  else:
    shutil.copy(src, dst)
    print(f'OP: Copied {dst}')


def get_token_indices(st):
  return st.index('{{'), st.index('}}')


def parse_tokenized_string(config, line, dst, listsep):
  res = line
  while True:
    try:
      i, e = get_token_indices(res)
    except ValueError:
      break
    token = res[i + 2:e]
    if token not in config:
      raise Exception(f'Unknown token {token} in {dst}')
    token_value = config[token]
    if isinstance(token_value, str):
      pass
    elif isinstance(token_value, list):
      token_value = listsep.join(token_value)
    else:
      raise Exception(f'Unknown type for token {token} in {dst}')
    res = res[:i] + token_value + res[e + 2:]
  return res


def parse_for_loop(config, line, dst, listsep):
  token_end = line.index('!', 3)
  token = line[3:token_end]
  token = config[token]
  if not isinstance(token, list):
    raise Exception(f'Unknown type for looped token {token} in {dst}')
  rest = line[token_end + 1:]
  result = ''
  for it in token:
    config['it'] = it
    result += parse_tokenized_string(config, rest, dst, listsep)
  return result


def parse_line(config, line, dst, listsep):
  if line.startswith('!!!'):
    return parse_tokenized_string(config, line[3:], dst, listsep)
  elif line.startswith('!!?'):
    return parse_for_loop(config, line, dst, listsep)
  else:
    return line


def render_if_not_exists(config, src, dst, listsep):
  if file_exists(dst):
    print(f'NOOP: {dst} already exists')
    return
  with open(src) as fsrc:
    with open(dst, 'w') as fdst:
      for line in fsrc:
        res = parse_line(config, line, dst, listsep)
        fdst.write(res)
  print(f'OP: Copied {dst}')


def write_files(config):
  filesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
  copy_if_not_exists(os.path.join(filesdir, 'gitignore'), '.gitignore')
  create_dir_if_not_exists('src')
  create_dir_if_not_exists('test')
  copy_if_not_exists(os.path.join(filesdir, 'main.cpp'), 'test/main.cpp')
  copy_if_not_exists(os.path.join(filesdir, 'TestGame.cpp'), 'test/TestGame.cpp')
  copy_if_not_exists(os.path.join(filesdir, 'gdlibrary.cpp'), 'src/gdlibrary.cpp')
  copy_if_not_exists(os.path.join(filesdir, 'Game.h'), 'src/Game.h')
  copy_if_not_exists(os.path.join(filesdir, 'HUD.h'), 'src/HUD.h')
  copy_if_not_exists(os.path.join(filesdir, 'HUD.cpp'), 'src/HUD.cpp')
  render_if_not_exists(config, os.path.join(filesdir, 'CMakeLists.txt'), 'CMakeLists.txt', ' ')


def write_godot_files(config):
  filesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
  nativedir = os.path.join('godot', 'native')
  os.mkdir(nativedir)
  copy_if_not_exists(os.path.join(filesdir, 'native.gdnlib'), os.path.join(nativedir, 'native.gdnlib'))
  copy_if_not_exists(os.path.join(filesdir, 'HUD.gdns'), os.path.join(nativedir, 'HUD.gdns'))


def main():
  if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} CONFIG_FILE')
    sys.exit(-1)
  f = open(sys.argv[1], 'r')
  config = json.load(f)

  create_folder(config)
  clone_git(config)
  clone_submodules(config)
  build_gdnative(config)
  write_files(config)

  if not file_exists('godot'):
    print(f'now open godot, create a project named "godot" under {os.getcwd()} and run this script again!')
    return
  write_godot_files(config)
  print(f'now you\'re good!')

if __name__ == '__main__':
  main()
