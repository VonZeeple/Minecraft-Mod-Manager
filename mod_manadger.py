# coding=UTF-8

from utils import *
import json
import os


class ModManager:
    def __init__(self, mc_version='1.12.2', path="test/", mod_list='mod_list.json'):
        self.mc_version = mc_version
        self.path = path
        self.mod_list = mod_list

    def add_mod(self, mod_id, version='latest'):
        data = self.load_mod_list()
        if mod_id in [mod['project_id'] for mod in data]:
            print('Mod already in mod list')
            return

        project = get_mod_files_info(mod_id)
        mod = find_version(self.mc_version, project, version)
        if mod is not None:
            data.append(get_mod_list_entry(mod_id, mod))
            self.save_mod_list(data)
        else:
            print('mod version: '+str(version)+' not found on CurseForge')

    def remove_mod(self, mod_id):
        data = self.load_mod_list()
        for i, mod in enumerate(data.copy()):
            if mod['project_id'] == str(mod_id):
                data.remove(i)
                print('Mod found and removed')
                return

        print('Mod not found in mod list')

    def make_mod_list(self, wish_list):
        with open(wish_list) as json_file:
            data = json.load(json_file)

        mods_to_load = list(data.values())
        mod_list = []
        for mod in mods_to_load:
            mod_file = get_mod_file_info(self.mc_version, mod['id'], mod_version=mod.get('version', 'latest'))
            if mod_file is None:
                print('File version \''+mod.get('version', 'latest')+'\' for '+str(mod['id'])+' not found')
                continue
            mod_list.append(get_mod_list_entry(mod['id'], mod_file))
            dependencies = get_dependencies(mod_file)
            for dep in dependencies:
                cond1 = str(dep['addonId']) not in [d['id'] for d in mods_to_load]
                cond2 = str(dep['addonId']) not in [d['project_id'] for d in mod_list]
                dep_mod_files = get_mod_files_info(dep['addonId'])
                if cond1 and cond2:
                    dep_mod_file = find_version_with_date(self.mc_version,dep_mod_files, get_day_from_date(mod_file['fileDate']))
                    mods_to_load.append({"id": dep['addonId'], 'version': dep_mod_file['fileName']})

        self.save_mod_list(mod_list)
        return mod_list

    def download_mods(self, *args, **kwargs):
        data = self.load_mod_list()
        for mod in data:
            if does_mod_jar_exist(self.path, mod):
                continue
            mod_file = get_mod_file_info(self.mc_version, mod["project_id"], mod_version=mod.get('fileName', 'latest'))
            download_mod_file(self.path, mod_file['downloadUrl'], mod_file['fileName'])

    def check_mod_files(self):
        jar_files = [file.name for file in os.scandir(self.path) if file.name.endswith(".jar")]
        mod_files = self.load_mod_list()
        mod_file_lenght = {mod['fileName']: mod['fileLength'] for mod in mod_files}
        missing_files = [mod for mod in mod_file_lenght.keys() if mod not in jar_files]
        unregistered_files = [file for file in jar_files if file not in mod_file_lenght.keys()]
        files_to_test = [file for file in jar_files if file not in unregistered_files]
        corrupted_files = [file for file in files_to_test if get_jar_file_length(self.path+file) != mod_file_lenght[file] ]
        print('missing files:'+str(missing_files))
        print('unregistered files:'+str(unregistered_files))
        print('File length not matching:' + str(corrupted_files))
        return missing_files, unregistered_files, corrupted_files

    def clear_files(self, all_files=False):
        for file in os.scandir(self.path):
            if file.name.endswith(".disabled") or (file.name.endswith(".jar") and all_files):
                os.unlink(file.path)

    def save_mod_list(self, mod_list):
        with open(self.path+self.mod_list, 'w') as outfile:
            json.dump(mod_list, outfile, indent=4, sort_keys=True)

    def load_mod_list(self):
        with open(self.path + self.mod_list) as json_file:
            return json.load(json_file)

    def check_updates(self):
        mod_files = self.load_mod_list()
        for mod in mod_files:
            self.check_mod_updates(mod)

    def check_mod_updates(self, mod_info):
        project_id = mod_info['project_id']
        file_id = mod_info['id']
        files_info = get_mod_files_info(project_id)
        last_version = find_last_version(self.mc_version, files_info)
        if last_version['id'] == file_id:
            return None
        else:
            print('Update found for '+str(mod_info['fileName'])+': '+str(last_version['fileName']))
            print('See changelog: '+get_file_curseforge_url(project_id, last_version['id']))
            return last_version

    def update_all_mods(self, download_files=False):
        mods = self.load_mod_list()
        for i, mod in enumerate(mods):
            update = self.check_mod_updates(mod)
            if update is not None:
                disable_file(self.path+mod['fileName'])
                mods[i].update(update)
        self.save_mod_list(mods)
        if download_files:
            self.download_mods()



