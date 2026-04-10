
Here is what i did

Research into Omnivere

- Omnivere is a set of APIs provided by nvidia to do simulation, data generation or other type of processing. It uses their own ai/agents/models/llms to do this

- Omniverse Kit is a SDK used to make your own engine, using nvidia's own set of Libraries, focusing on OpenUSD, RTX Renderer, python scripting.

Omniverse Kit Features

1. An already made 3d engine/editor/template to use : "kit-editor"
    - "kit-editor" allows to create basic primitive meshes,
    - Standard Editor Panels as other 3D application
    - PathTracing by default
2. Extend Editor by creating custom Menu Items "Basic Python Extension"
3. Extend Editor by creating custom UI Popups "Python UI Extension"
4. Wireframe view, Debug view (Depth,Bary,Motion Vector,Wireframe,Heatmap   )
5. Application Streaming.
    1. Run Base Editor to use RTX GPU,
    2. Stream to Browser, React+Typescript using Nvidia WebRTC
6. Allow use of Python pip packages

---
---
---

1. Look at Omniverse Kit 
    - Follow [Tutorial] (https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)
2. Looked at [Developer (Omniverse) Blueprints](https://developer.nvidia.com/omniverse)
    1. 4 projects are avaiable to download but all but need graphic card with 80+gb vram minimum to run
3. Try to find Other Sample Kit Projects to take/reuse Extension code
    - Found Issac Sim to most comprehensive example
    - Two Official UI Extension/Tutorial [Editor Lable,Widget (UI Panels + more)](https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene) [UI Reticle (lines on screen)](https://github.com/NVIDIA-Omniverse/kit-extension-sample-reticle)
    - Nothing else
3. Look at [Issac Sim](https://github.com/isaac-sim/IsaacSim)
    - build on Kit, tune for Robot Sim
    - Has (Warehouse Creator Extension)[https://docs.isaacsim.omniverse.nvidia.com/6.0.0/digital_twin/warehouse_logistics/ext_omni_warehouse_creator.html] (Conveyor beld placing)[https://docs.isaacsim.omniverse.nvidia.com/6.0.0/digital_twin/warehouse_logistics/ext_isaacsim_asset_gen_conveyor.html]
    - Has many other utils Extension for Kit
4. Research more into Omniverse Kit Features
    - Have Many [APIs](https://build.nvidia.com/explore/industrial) that runs
        - Simulations (Automotive, CFD),
        - LLMs (Reasoning, Safety & Moderation)
        - Generative Design (Image generation, model generation)
        - Protein Sequencing Prediction
        - Route Optimization
        - Weather forcast
        - Speech transcription
        - "USD Search API", Image to USD Model search in nvidia database to download




---
---
---

Omniverse Kit Exploration
1. Import SIT Campus model (just drag drop), internally uses omni.convert.cad to convert to usd format
2. Attempt to add "player" controls
    - No default walk or player scripts
    - Unable to find extensions to do this
    - Need code custom script
3. Attempt to create a Simple 2D/3D UI Text + Button
    - No default Text or Button object creation or any other UI
    - Add 3D Text via custom extension
    - Tried a workaround by using a 3d plane to do ui
        - Attempt to find existing material library to do unlit UI, could not find
        - Attempt to adjust standard material, have issue with the material and shader appereance not correct, due to Pathtracing rendering
        - Attempt to create a custom shader, found it not possible
    - Found Widgets to be the only way to do UI
        - UI is done fully in code, Similar code structure to concept XAML/WPF
        - Large Code Required
4. Attempt to Spawn Cube On MousePosition point on model
    - Could not find Sample code online
    - Documentation on raycast hard to understand
    - Paired with LLM to produce non functioning code.
    - Able to spawn Cube, but could not make raycast to work
5. Tried Web streaming
    - Kit-Editor Connects to Simple React App that mirrors app
    - Laggy

Comments:
1. Omniverse is not a 3d engine/editor
2. Omniverse kit is an example of a ready made editor/engine created using Omniverse provided library code
3. Editor is bear bones. Many of standard tools to create a 3D app, game or simulation needs to be customly made
4. Rendering is hard fix to use Pathtracing RTX, this limits the type of application or use cases that can fit
5. Currently have limited Extensions & sometimes doesnt work





Dev Notes:
- .kit file is just a manifest containg "extensions" and "depenedency" like a npm package.json file

Create Service -> is creating an api service files, that define the endpoints in the form of pydantic data model 
An Extension/Service Type Developer can create a Service/Extension
1. Create a Service from template by running ".\repo.bat template new"
2. Select Application->Kit Servce->Enter App Name that you want to extend
3. A Extension folder will be created e.g Source\extension, Edit python script within file to create new apis to do more stuff

Package a fat package (20mins build time)
1. Package app ".\repo.bat package --name desired_package_name"
2. Run package app ".\repo.bat launch --package {path}"

Package a Thin package
1. .\repo.bat package --name desired_package_name --thin
2. pull_kit_sdk to download kit kernel and extensions
3. \{path_to_extracted_thin_package}\pull_kit_sdk.bat

Commands:
 - Run Kit .\_build\windows-x86_64\release\kit\kit.exe
 - Run Kit with extension .\_build\windows-x86_64\release\kit\kit.exe --enable omni.usd
 - Run Kit with exntesion .\_build\windows-x86_64\release\kit\kit.exe --enable omni.kit.mainwindow
 - Create App or extension .\repo.bat template new
 - Build App .\repo.bat build
 - Run app .\repo.bat launch
 - List extension .\_build\windows-x86_64\release\kit\kit.exe --list-exts
 - Run Web Viewer npm run dev

Links: 
- [Kit Manual](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_exts.html)
- [USD Search Tutorial](https://docs.omniverse.nvidia.com/guide-sdg/latest/setup.html)
- [APIs](https://build.nvidia.com/explore/industrial)





