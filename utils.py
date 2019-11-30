# coding=UTF-8
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import quote


base_url = 'https://addons-ecs.forgesvc.net'


def get_day_from_date(date):
    return date[0:10]


def print_json(parsed_json):
    print(json.dumps(parsed_json, indent=4, sort_keys=True))


def get_mod_list_entry(mod_id, mod_file_info):
    entry = mod_file_info
    entry['project_id'] = mod_id
    return entry


def does_mod_jar_exist(path, mod_info):
    filename = mod_info['fileName']
    return os.path.isfile(path + filename)


def disable_file(filename):
    if os.path.isfile(filename):
        os.rename(filename, filename+'.disabled')


def get_dependencies(mod_file):
    if mod_file is not None:
        #Return a list of the hard dependencies
        return list(dep for dep in mod_file['dependencies'] if dep['type'] == 3)


def download_mod_file(path, url, filename):
    url = quote(url.encode("UTF-8"), safe=':/')
    print('Downloading from: '+url)
    request = Request(url)
    file = urlopen(request)
    length = file.getheader('content-length')

    bin_cont = file.read()
    file = open(path +filename, "wb")
    file.write(bin_cont)
    file.close()


def find_version_with_date(mc_version, mod_files_info, date):
    #We select the files corresponding to the right MC version
    filtered_list = list(file for file in mod_files_info if mc_version in file['gameVersion'])
    #Now find the right mod version, we make a dictionnary with the file date as a key:
    file_dict = dict(zip(list(a['fileDate'] for a in filtered_list), filtered_list))
    #We find the latest version posted that day:
    sorted_list = list(k for k in file_dict.keys() if k <= date)
    sorted_list.sort()
    if len(sorted_list) == 0:
        return None
    else:
        print('date :'+str(date))
        print('dependence date :'+str(sorted_list[-1]))
        return file_dict[sorted_list[-1]]


def find_version(mc_version, mod_files_info, version):
    if version == 'latest':
        return find_last_version(mc_version, mod_files_info)
        # We select the files corresponding to the right MC version
    filtered_list = list(file for file in mod_files_info if mc_version in file['gameVersion'])
    file_dict = dict(zip(list(a['fileName'] for a in filtered_list), filtered_list))
    return file_dict.get(version, None)


def find_last_version(mc_version, mod_files_info):
    #We select the files corresponding to the right MC version
    filtered_list = list(file for file in mod_files_info if mc_version in file['gameVersion'])
    #Now find the right mod version, we make a dictionnary with the file date as a key:
    file_dict = dict(zip(list(a['fileDate'] for a in filtered_list), filtered_list))
    #Since the keys are in alphabetical order, the latest release is given by the last element:
    sorted_list = list(file_dict.keys())
    sorted_list.sort()
    if len(sorted_list) == 0:
        return None
    else:
        return file_dict[sorted_list[-1]]


def get_mod_file_info(mc_version, mod_id, mod_version):
    parsed = get_mod_files_info(mod_id)
    return find_version(mc_version, parsed, mod_version)


def get_mod_files_info(mod_id):
    request = Request(base_url+'/api/v2/addon/'+str(mod_id)+'/files')
    response_body = urlopen(request).read()
    return json.loads(response_body)


def get_mod_curseforge_url(mod_id):
    request = Request(base_url+'/api/v2/addon/'+mod_id)
    return json.loads(urlopen(request).read())['websiteUrl']


def get_jar_file_length(jar_file):
    return os.path.getsize(jar_file)


def get_file_curseforge_url(mod_id, file_id):
    request = Request(base_url + '/api/v2/addon/' + str(mod_id))
    url = json.loads(urlopen(request).read())['websiteUrl']
    return url+'/files/'+str(file_id)

