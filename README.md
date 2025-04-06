# blender-2-unity-fast

An exporting tool for rapid prototyping in Blender for Unity.

Please check out [Disclaimer](##Disclaimer) below.

![./preview.png](./preview.png)

## Installation
1. Clone the repo.
2. In Blender go to `Preferences -> File Paths -> Script Directories`
2. Add the path pointing to the cloned repo (`this will ensure script will be loaded whenever you open blender automatically`)

## Why?
I used to work a lot in Unity with [ProBuilder](https://docs.unity3d.com/Packages/com.unity.probuilder@6.0/manual/index.html), because it was nice to work with models directly in Unity Editor, but Unity somehow messed up it's UI in my opinion. So I thought it is time to get back to Blender ✨, but Unity doesn't auto-import `.blend` files for Blender 4, even throws annoying warnings about it and I really dislike the repeated process to manually go to export menu whenever I want to see the model in Unity as I like to do it often, enter playmode and walk around it.

TLDR; Working in blender and seeing results in Unity immediately (even in playmode!).

## How To
It comes in a form of an n-toolbar menu.
1. Open up the 3D ViewPort
2. Open the "N-Toolbar" (press the `N` key)
3. Press the `🕊️ Uni Exp` button

ℹ️💬 All of the elements in the panel contain additional usage info when hovered.

### GLTF/GLB vs. FBX

#### 🍰🎯 IMPORTANT: You need to install an official Unity package [glTFast](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.0/manual/index.html) to work with `gLTF` fileformats in Unity.

1. I always seem to have more orientation/scaling problems when exporting `FBX` meshes from Blender.
2. `gLTF` has usually smaller filesizes.
3. `gLTF` is an open file format (fbx is a proprietary, owned by Autodesk)
4. https://www.khronos.org/gltf/
5. https://github.com/KhronosGroup/UnityGLTF Kronos also provides an importer/exporter of gltf files for Unity, but the official Unity one might be an easier plug and play solution for most cases.

`FBX` exporting option is there and it seems to work (*as I understand for some Animation edge cases it is necessary*), but I don't work much with it so please let me know if there are some issues/wishes related to it.

## Disclaimer
I'm mostly a C# programmer, so this plugin was made unter chatty's (ChatGPT) guide, it was a trial and error process, I learned a bunch about python and blender scripting, so it is an altogether fun ride and I am also happy with the results and can finally abandon ProBuilder for good.

Taking that into consideration this is by no means a professional battle-proven addon, might slowly grow into one, mostly a tool to rapidly prototype simple environments in blender to see changes almost instantly reflected unity in a possibly seamless way.

There are a bunch of code comments that explain to myself for future what some of the things do, I hope this is not too clumsy!