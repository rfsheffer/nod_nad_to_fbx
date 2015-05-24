# NOD Engine (Nihilistic Object Data) and (Nihilistic Animation Data) to FBX

This is a work in progress project. The ultimate destination of this project is to allow the user to export VtMR
vertex data completely textured and bone weighted, and also export the animation curves for the bones. The reason for this
project is to allow users to mess around with the VtMR content in their own sandbox. The projects model import code could
also be used to create Blender plugins for import and export of VtMR models and animations back to the NOD engine, but that
is beyond the scope of this project, maybe for another project if the interest in that spikes.

## Current Features:
- Exports the NOD vertex data to FBX

## Road map:
- Exports the NOD vertex data to FBX (DONE)
- Export normals and UV information for the vertex data
- Export the skeleton
- Skin the vertex data to the skeleton using weights
- Import animation curve data from the NAD files
- Create skeletal animations from the curve data and export to FBX
- DONE!

## What you need:
- Models and animations from Vampire the Masquerade Redemption
- Textures found in the VtMR texture archive
- The FBX SDK and FBX python SDK installed
- Python Pillow Imaging Library 2.8.1 or greater