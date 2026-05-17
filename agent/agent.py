from doctest import debug

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.runners import Runner
from google.genai import types
from flask import Flask,request,jsonify
# import requests
from dotenv import load_dotenv
import os
load_dotenv()
app=Flask(__name__)
url=os.environ.get("MCP_URL")
MODEL=os.environ.get("MODEL")
session_service=InMemorySessionService()
# Configure xAI endpoint
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
APP_NAME='FILE ORGANIZER'
USER_ID='123'
SESSION_ID='session1'
# os.environ["OPENAI_BASE_URL"] = "https://api.x.ai/v1"
async def build_agent():
   tool=McpToolset(
       connection_params=StreamableHTTPConnectionParams(
           url=url,
       )
   )
   PRompt='''
   You are a File System Organizer Agent.

   Your task is to help the user organize files inside a filesystem directory.

   Workflow:(THIS MUST BE DONE STEP BY STEP NO SKIPPING )

   1. Ask the user for the filesystem path they want to organize.

   2. Once the user provides the path:

      * save it as `path`
      * call the tool:

        listfiles(path=path)

   3. Store the output of `listfiles` as:

      filesinfo

   4. Call the tool:

      generate_folder_structure(filesinfo=filesinfo)

   5. Store the output of `generate_folder_structure` as:

      files

   6. Show the exact output returned by `generate_folder_structure` to the user without modifying it.

   7. Explain to the user that these files will be moved into the suggested locations.

   8. Ask the user for confirmation before making any filesystem changes.

   9. ONLY if the user explicitly approves:

      call:

      create_folder(files=files)
   # 10.store the output of create_folder as:
   # files1

   11. Show the exact output of `create_folder` to the user without modifying it.
   12. call the tool :
   move_files(files=files)
   13. display the output of move_files tool

   RULES:

   1. Never create, move, rename, or delete files without explicit user approval.

   2. Never modify tool outputs before displaying them to the user.

   3. Always preserve the exact structure returned by the tools.

   4. Do not assume filesystem paths. Always ask the user first.

   5. If a tool fails, show the tool error directly to the user.

   6. Keep track of:

      * path
      * filesinfo
      * files

   7. Only proceed to the next step after the previous step succeeds.

   8. If the user rejects the proposed structure, ask them what changes they want.
   9. Do not modify the outputs of the tool calls just pass them as is and wait for the result of tool calls

   '''
   root_agent=LlmAgent(
   name='Ai_File_organizer_agent',
   model=MODEL,
   instruction=PRompt,
   tools=[tool]

   )
   return root_agent


@app.route('/agent',methods=['GET','POST'])
async def runagent():
   #capture json request
   userrequest=request.get_json()
   print(userrequest)
   query=userrequest['query']
   userid=userrequest['user_id']
   session_id=userrequest['session_id']
   
   #create memory session
   
   existing_session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=userid,
    session_id=session_id
)

   if not existing_session:
       await session_service.create_session(
           app_name=APP_NAME,
           user_id=userid,
           session_id=session_id
       )
   
   #get the agent
   rootagent=await build_agent()

   #create a runner instance to run the agent
   runner=Runner(app_name=APP_NAME,agent=rootagent,session_service=session_service)

   #format the query
   content=types.Content(role='user',parts=[types.Part(text=query)])

   #run the agent
   print("RUnning agent with the query",query)
   events=runner.run_async(
      new_message=content,
      user_id=userid,
      session_id=session_id,
   )

   #print the message
   async for event in events:
      if event.is_final_response():
         finalresponse=event.content.parts[0].text
         # print('agent response',finalresponse)
   return jsonify({
      "agent_response":finalresponse})



if __name__=='__main__':
   app.run(host='localhost',port=8500,debug=True)
