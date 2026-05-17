from fastmcp import FastMCP
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
HOST=os.environ.get("MCP_HOST")
PATH=os.environ.get("MCP_PATH")
print(PATH)
import shutil
from typing import List, Dict
mcp=FastMCP()
import logging
log=logging.getLogger('MCP Logger')
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )



@mcp.tool(
    name='listfiles',
    description='This tool lists the files in that particular path'
)
async def listfiles(path:str)->List[Dict]:
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

    log.info(f'[listfiles] tool called')
    return files #here what we have to do is we have to return the filenames,extensions and size and type of file


@mcp.tool(name='generate_folder_structure',
          description='This tool is used to generate the folder structure plan')
async def generatefolderstructure(filesinfo:List[Dict])->List[Dict]:
    log.info(f'[tool called] generate info')
    log.info(f'[input is] {filesinfo}')
    result=[]
    for content in filesinfo:
        if content['type'] != 'file':
             continue
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
    log.info(f'[tool response]:{result}')
    log.info(f'Generated files count: {len(result)}')
    return result

@mcp.tool(name='create_folder',description='This is a tool that is used to create folders.')
async def createfolder(files:List[Dict]):
    for file in files:
        if file['location']=='Docs' :
            docs_folder=Path(file['parent'])/'Docs'
            docs_folder.mkdir(parents=True,exist_ok=True)
            # print()
        elif file['location']=='Images':
            img_folder=Path(file['parent'])/'Images'
            img_folder.mkdir(parents=True,exist_ok=True)
        elif file['location']=='Videos':
            vid_folder=Path(file['parent'])/"Videos"
            vid_folder.mkdir(parents=True,exist_ok=True)
    return {"message":"folders created"}

@mcp.tool(name='move_files',description='This tool is used to move files')
async def movefiles(files:List[Dict]):
    log.info(f'Files received for moving: {len(files)}')
    moved = []
    failed = []
    for file in files:
       try:
        src=Path(file['path'])
        dest=Path(file['parent'])/file['location']
        if src and dest:
            shutil.move(src,dest)
        moved.append({
                "file": file['name'],
                "destination": str(dest)
            })

        log.info(f'Moved {src} -> {dest}')

       except Exception as e:

            failed.append({
                "file": file.get('name'),
                "error": str(e)
            })

            log.error(f'Move failed: {e}')
    
    return {"moved":moved,
            "failed":failed}


if __name__=='__main__':
    mcp.run(transport='http',host=HOST,path=PATH)