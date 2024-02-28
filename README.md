# Meshcapade Unreal Suite

## I. Adding the Plugin To your Unreal Project

[Download](https://codeload.github.com/Meshcapade/mc-unreal/zip/refs/tags/v0.0.1) the Unreal Plugin or grab from our [git repo](https://github.com/Meshcapade/mc-unreal).

Make sure your Unreal project is closed.  Drop the Plugins folder into the top level of your Unreal project.

![adding plugins to unreal project](images/readme_plugins.gif)

## II. Configuring Unreal to Build custom C++ code
The Meshcapade Unreal plugin uses custom C++ code that needs to be compiled.  

Download and install [Visual Studio Community 2022](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&passive=false&cid=2030).

In the install options, check `Game Development with C++` and inside that, check `Unreal Engine Installer`

![visual studio UEI](images/readme_vs00.png)

Also install `.NET Desktop Development`

![.NET](images/readme_vs01.png)

After installing, when you launch the Unreal project, it will compile the C++ code as part of the launch process. 

## III. Download an Animated .FBX from [Meshcapade.me](https://meshcapade.me/)
Currently, there are two ways to get animations from [Meshcapade.me](https://meshcapade.me/): 
- [afv](https://me.meshcapade.com/from-videos) (what are we calling this externally) - Extract the human motion from a video.
- [tmr](https://me.meshcapade.com/editor) (what are we calling this externally). - Find a human motion in our library of 10,000 (made that number up) motions.  
### A. [afv](https://me.meshcapade.com/from-videos)
To get an animation from video, visit 
https://me.meshcapade.com/from-videos.  Follow the prompts until you've created an animated avatar.

![afv](images/readme_afv00.png)

### B. [tmr](https://me.meshcapade.com/editor)
To search for a motion from our motion library, visit https://me.meshcapade.com/editor. In the top right, there is a search box where you can search for an animation.  Once you've found the animation you want, save the avatar into your vault.

![tmr](images/readme_tmr00.png)

</details>

## IV. download the fbx

Go to your [avatar vault](https://me.meshcapade.com/vault), and click the `...` on the top right corner of the avatar containing the motion you'd like to download.  In the download options, make sure that `file format` is `fbx` (`obj` has no motion) and `Pose/Motion` is `Captured Motion`.  For `compatibility mode`, select `Unreal` if you are interested in using the Meshcapade body with pose correctives.  Choose `Unreal - no blenshapes` if you're only insterested in the motion, this will make the import process faster.  

![download](images/readme_download00.png)

## V. Import the fbx into Unreal

With the fbx downloaded, import it into your unreal project (File > Import).  

Set the skeleton to `SK_MeshcapadeBody`.  If you don't see it, then click the gear next to the search box and make sure `Show Plugin Content` is checked.  

![import00](images/readme_import00.png)

In the content browser, `SK_MeshcapadeBody` is located here: `Content/Plugins/Meshcapade/Meshes/SK_MeshcapadeBody` 

If you’re interested in using the Meshcapade Body outright and you want pose correctives, check `import morph targets`

![import00](images/readme_import01.png)

Also check `import animation`

![import 01](images/readme_import02.png)

## VI. Retargeting Animation
One thing you may want to do is retarget the motion from the Meshcapade body onto the body of your own character.  To do so, you will need a retargeter.  Retargeters require two IK rigs: one for the source body, the Meshcapade body in this case, and for the target body - your character.  The Meshcapade Unreal plugin comes with a sample retargeter for the Unreal mannequin, including an IK rig for the Meshcapade body and an IK rig for the Unreal mannequin.

### A. Making your own IK Rig

First you need to make an IK Rig for your character.  In the top right corner of the Content Browser, click on `Settings` and make sure `Show Plugin Content` is checked.  Then open `Plugins` > `Meshcapade Content` > `Rigs`.  Duplicate the `IK_Manniquen` rig. 

![ik rig0](images/readme_ikrig00.png)

If your character's skeleton follows the Unreal character naming convention, then all you need to do is change the preview skeletal mesh to your character.  If you're using a UE4 character, you may need to change the `End Bone` of the `Spine` IK chain to `spine_03`.  

![ik rig1](images/readme_ikrig01.png)

For more on this subject, see the Unreal documentation on [Ik Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

### B. Making your own Retargeter
Once you have the IK rig for your character created, you can make a retargeter.  Right click in the Content Browser and type `retargeter` or go to `Animation` > `Retargeting` > `IK Retargeter`.  Double click the newly created retargeter.  

A retargeter contains two IK rigs and the relationship between them.  Set the two IK rigs in the details panel.

![retarget0](images/readme_retarget00.png)

The poses of the two skeletons need to match as well.  To do this, change the display mode to `Edit Retarget Pose` on the top left.  Then rotate the bones of the source and/or the target until the angles match one another as closely as possible.   

![retarget1](images/readme_retarget01.png)

Finally, the chains of the two IK rigs need to be correlated.  There are a number of ways to do this, but if you copied the Unreal mannequin all you need to do is click `Auto-Map Chains` > `Map All (Exact)`.  

![retarget2](images/readme_retarget02.png)

For more on this, see the Unreal documentation on [Ik Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

### C. Retargeting Animation
Now that the retargeter is built, it can be used to retarget any number of animations between the Meshcapade body and the body of your character.  To do so, simply right click on an animation file (it will have a dark green bar in the middle of it), and select `Retarget Animation Assets` > `Duplicate and Retarget Animation Assets/Blueprints`.

![retarget4](images/readme_retarget04.png)

Select the retargeter you'd like to use

![retareget5](images/readme_retarget05.png)

Here's an example of the retargeted animation next to the original animation

![retarget example](images/readme_retargetingexample.gif)

## VII. Adding Pose Correctives to Meshcapade Bodies
If you're only interested in using the Meshcapade body, they come with an additional perk of having pose corrective blend shapes baked into the .fbx, if you imported morph targets on the [import step](#v-import-the-fbx-into-unreal). 

This plugin comes with special code for actors containing Meshcapade bodies, where the mesh has corrective blendshapes applied to the mesh, based on what pose the character is in.

All you need to do is add a skeletal mesh component to a blueprint actor, and then add the `Pose Correctives` actor component to the same blueprint and you're done.

![add pose correctives](images/readme_posecorrectives.gif)

Below is an example where two bodies are overlaid to illustrate what pose correctives are.  The orange body is the body without pose correctives, and the textured body has pose correctives.  Note how the mesh is corrected based on the pose. 

![pose corrective example](images/readme_posecorrectiveexample.gif)


## VIII. Editing animation

If the animation doesn't look right on your character, there are two options.  One is to go back to the platform and try to get something better, or to edit the motion.  There are several ways to edit an animation after the fact.  One way that is easy to use and gives you lots of control is to use a control rig that has a forward and backwards solver.

The control rig that comes with the third person template, which we also ship this with the plugin, is sufficient for this.  Go to `Plugins` > `Meshcapade Content` > `Rigs` and duplicate the `CR_Mannequin_Body` rig.  

![controlrig0](images/readme_controlrig00.png)

You will have to make edits to this control rig depending on how different your character's skeleton is from the Unreal convention.  

![controlrig1](images/readme_controlrig01.png)

In the Preview Scene Settings, change the preview mesh to that of your character.  

If you are retargeting a UE4 character for example, you would need to make a few changes to the skeleton.  In the Rig Hierarchy, you can rearrange bones by clicking and dragging them.  The spine, neck and hands are different between the UE4 and UE5 characters.  You'd make the following changes:
- Move `clavicle_l`, `clavicle_r` and `neck_01` to be underneath `spine_03`
- Move `head` to be underneath `neck_01`
- On both hands, move `index_01`, `middle_01`, `ring_01`, and `pinky_01` to be direct children of their corresponding `hand` bones.

For more on this, see the Unreal documentation on [Control Rig](https://docs.unrealengine.com/5.3/en-US/control-rig-in-unreal-engine/).

Now that you have a control rig that works with your character, you can bake the animation onto that control rig.  Make a new level sequence by right clicking and typing `level sequence` or going to `Cinematics` > `Level Sequence`.  Drag the animation asset into your level, select it, and then in the sequencer select `+Track` > `Actor To Sequencer` > `<your animation asset>`.  

Click the `+` to the right of `Animation` and add your animation asset.

Right click on parent top node of your animation in the track panel and choose `Bake to Control Rig` > `<your control rig>`

Note: the animation baking will happen in between the red and green markers on the timeline, so make sure that the animation you're interested in is in between them.

![anim editing](images/readme_animediting.gif).

