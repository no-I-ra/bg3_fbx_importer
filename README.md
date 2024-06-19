# BG3 Noesis FBX Importer for Blender 3.6 and 4.x

An addon for Blender that allows you to import Baldur's Gate 3 FBX converted by Noesis into Blender.

## Features:  
* Imports selected FBX files into Blender and make them ready for a BG3 export.
* Automatically renames the data from the filename, applies transforms, fixes the missing Dummy_Root bone, clears animation data if needed, clears the material data.
* Automatically creates a collection from the FBX file name and place the imported assets in it.
* Option to remove a suffix and/or prefix to the fbx file name.
* Imports animation keys if `Is animation` is checked.
* Add an armature modifier on ears and weight them to the Head_M bone.
* Can import several FBX files at once.

## Installing

### Manual Method  
* Download the last release zip file.
* Save the zip somewhere where you can find it again.
* Extract the zip.
* Copy the folder `bg3_fbx_importer`. Make sure this is the folder with the scripts under it (`bg3_fbx_importer\__init__.py` etc).
* Paste the `bg3_fbx_importer` folder into your addons folder. Default path:
```
%APPDATA%\Blender Foundation\Blender\3.6\scripts\addons
```
### Blender Method

* Download the last release zip file.
* Save the zip somewhere where you can find it again.
* In Blender, navigate to Edit -> Preferences -> Add-ons
* Click on `Install...`
* Browse to the zip, select it and click on `Install Add-on`
* In the addon list, search for `Noira's BG3 FBX Importer`
* Check it to enable the addon. This will add the panel `Noira's BG3 FBX Importer` the right of the 3D View

* For more information, please refer to Blender's guide for installing addons here: [Install from File](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html).

## How to use the addon:

### Default
* Choose the collection where files should be imported and set it as active.
* In the addon panel, click on `Import FBX Files`.
* Select all the fbx files to import and click on `Import`.
* Each fbx will be imported under a collection named like the fbx file, such as armatures and their data.

### Optional
* Check `Is animation` to import animation data. If unchecked, the aniamtion data will be cleared.
* Define a Prefix and/or a Suffix to remove from the fbx file name so the imported collection and armatures use that edited name.


