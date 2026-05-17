from pathlib import Path
import shutil
def listfiles(path:str)->list[dict]:
#    p=Path(path)
    p=Path(path.strip()).expanduser().resolve()
    contents=p.iterdir()
    # files=[content for content in contents]
    files=[]
    for content in contents:
        item = {
    "name": content.name,
    "path": str(content.resolve()),
    "parent": str(content.parent),
    "extension": content.suffix.lower() if content.is_file() else None,
    "size_bytes": content.stat().st_size,
    "type": "folder" if content.is_dir() else "file",
    "is_hidden": content.name.startswith(".")
}
        files.append(item)
    # print('tool called')

   #  log.info(f'[listfiles] tool called')
    return files #h
path=r"C:\Users\hosam\OneDrive\Pictures\Screenshots"
files=listfiles(path)
def generatefolderstructure(filesinfo:list[dict]):
   #  log.info(f'[tool called] generate info')
   #  log.info(f'[input is] {filesinfo}')
    result=[]
    for content in filesinfo:
        extension=content['extension']
        if extension=='.docx' or extension=='.pdf' or extension=='doc':
            content['location']='Docs'
        elif extension=='.img' or extension=='.jpeg' or extension=='.png':
            content['location']='Images'
        elif extension=='.mp4' or extension=='.mov' or extension=='.mpg':
            content['location']='Videos'
        else:
            continue
        result.append(content)
    return result

results=generatefolderstructure(files)
print(results)

def createfolder(files):
    for file in files:
        if file['location']=='Docs' :
            docs_folder=Path(file['parent'])/'Docs'
            docs_folder.mkdir(exist_ok=True)
            # print()
        elif file['location']=='Images':
            img_folder=Path(file['parent'])/'Images'
            img_folder.mkdir(exist_ok=True)
        elif file['location']=='Videos':
            vid_folder=Path(file['parent'])/"Videos"
            vid_folder.mkdir(exist_ok=True)
    return {"message":"folders created"}

print(createfolder(results))

def movefiles(files):
    for file in files:
       src=file['path']
       dest=f'{file['parent']}/{file['location']}'
       if src and dest:
        shutil.move(src,dest)
    return {"message":"All files moved succesfully"}

print(movefiles(results))