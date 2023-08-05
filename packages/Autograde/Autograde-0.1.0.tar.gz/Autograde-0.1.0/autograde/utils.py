import os.path
def create_repo():
    import requests
    response = requests.post("https://api.github.com/authorizations")
    return response

def extract_from_zip(file):
    import zipfile
    from readmeparser import parse
    from django.conf import settings
    print file
    z = zipfile.ZipFile(file)
    try:
        name = ".".join(file.name.split(".")[0:-1])
        z.extractall(path=settings.AUTOGRADE_PROJECT_UPLOAD_PATH)
        return parse(os.path.join(settings.AUTOGRADE_PROJECT_UPLOAD_PATH,name))
    except AttributeError:
        z.extractall("projects")

def run_test(submission,test_case,folder_name="tmp"):
    import os
    import shutil
    import string
    tmp_folder = folder_name
    found = False
    while not found:
        try:
            os.mkdir(tmp_folder)
            found = True
        except OSError:
            tmp_folder = folder_name + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(5))

    for file in submission.files.all():
        shutil.copyfile(file,os.path.join(tmp_folder,file.name))

    os.chdir(tmp_folder)
    execfile(test_case.my_file.name)
    os.chdir("../")
