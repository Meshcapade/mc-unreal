# Meshcapade Unreal Plugin

### Plugin Releases

| Unreal Version | Plugin Version | Download Release                                                                             |
|:--------------:|:--------------:|:--------------------------------------------------------------------------------------------:|
| v5.3           | v5.3.2.0       | [Download](https://github.com/Meshcapade/mc-unreal/releases/download/v5.3.2.0/mc-unreal.zip) |
| v5.4           | v5.4.4.0       | [Download](https://github.com/Meshcapade/mc-unreal/releases/download/v5.4.4.0/mc-unreal.zip) |

<p class='hidden'>For a better viewing experience, visit our <a href='https://me.meshcapade.com/integrations/unreal'>webpage</a>.</p>

This plugin allows you to quickly retarget motions created on the [Meshcapade.me](https://me.meshcapade.com/) platform onto your own characters in [Unreal Engine 5](https://www.unrealengine.com/en-US/download). Bodies created on the Meshcapade platform are created using the [SMPL](https://smpl.is.tue.mpg.de/) core technology, and are thus referred to as [SMPL-bodies](https://smpl.is.tue.mpg.de/license.html).  

📝 This guide has only been tested on Unreal Engine versions 5.3 and 5.4. It may or may not work on earlier or later versions.

<details open>
<summary>I. Adding the plugin to your Unreal project</summary>

[Download](https://github.com/Meshcapade/mc-unreal/releases/latest/download/mc-unreal.zip) our latest Unreal Plugin version directly, or grab from our release table above.

📝 Make sure that your Unreal project is closed before proceeding.  

Once you have the plugin downloaded, unzip the plugin and put the `Plugins` folder into the top level of your Unreal project.

![adding plugins to unreal project](images/readme_plugins.gif) 

📝 For MacOS users, install [Xcode](https://apps.apple.com/us/app/xcode/id497799835?mt=12) before relaunching.  When opening your Unreal project for the first time after adding the plugin, a warning will pop up asking you to rebuild missing modules.  Click `Yes` and continue normally.

📝 For Windows and Ubuntu users, there's nothing extra to do.

</details>

<details>
<summary>II. Getting an animation from <a href='https://me.meshcapade.com' target='_blank'>Meshcapade.me</a></summary>

Currently, there are two ways to get animations from [Meshcapade.me](https://me.meshcapade.com/):
- [Motion from video](https://me.meshcapade.com/from-videos) - extract the human motion from a video.

- [Motion from text](https://me.meshcapade.com/editor) - find a human motion in our library of thousands of motions.

### A. [Motion from video](https://me.meshcapade.com/from-videos)
To get an animation from a video, visit the Meshcapade [motion from video](https://me.meshcapade.com/from-videos) page.  Follow the prompts until you've created an animated avatar.

![from video](images/readme_afv00.png)

### B. [Motion from text](https://me.meshcapade.com/editor)
To search for a motion from our motion library, visit the Meshcapade [editor](https://me.meshcapade.com/editor) page. On the top right, there is a search box where you can find animation.  Once you've found the animation you want, save the avatar into your vault.

![from text](images/readme_tmr00.png) 

</details>

<details id='downloading'>
<summary>III. Downloading the animation </summary>

Go to your [avatar vault](https://me.meshcapade.com/vault) and open the avatar in editor (which contains the motion you'd like to download). Once the avatar is open in the editor, click the Download button located at the top left corner of the page. Download options will then appear. If you're only interested in downloading the motion–which will make the import process faster, make sure that `file format` is set to `.FBX` (`.OBJ` has no motion).  and `compatibility mode` is set to `Unreal - no blend shapes`. If you want to use [Pose Correctives](#pose-correctives), then make sure `compatibility mode` is set to `Unreal`. Click Download avatar. If you want to use the `.GLB` instead, you can set the `file format` to `.GLB` and `compatibility mode` to `Unreal` - we currently always export `.GLB` files with [Pose Correctives](#pose-correctives).  

![download](images/readme_download00.jpeg)

</details>

<details id='importing_glb'>
<summary>IV (1). Importing the .GLB into Unreal</summary>

You can import the .GLB into your project using either the Scene import (File > Import into Level) or Asset import (Content Drawer > Import). 

📝 If you need the animated camera, you have to use the Scene Import (File > Import into Level).  

For retargetting - Set the skeleton to `SK_Meshcapade_glb`.  If you don't see it, then click the gear next to the search box and make sure `Show Plugin Content` is checked.  In the content browser, `SK_Meshcapade_glb` is located here: `Content/Plugins/Meshcapade/Meshes/SK_Meshcapade_glb`.
</details>

<details id='importing_fbx'>
<summary>IV (2). Importing the .FBX into Unreal</summary>

📝 We generally recommend using the GLB and the corresponding retargetter, since we might deprecate FBX in future releases.

With the .FBX downloaded, import it into your unreal project through the content drawer. (Content Drawer > Import)

Set the skeleton to `SK_Meshcapade_fbx`.  If you don't see it, then click the gear next to the search box and make sure `Show Plugin Content` is checked.  In the content browser, `SK_Meshcapade_fbx` is located here: `Content/Plugins/Meshcapade/Meshes/SK_Meshcapade_fbx`.

![import00](images/readme_import00.png)

📝 Make sure that `Import Animation` is checked.

📝 If you’re interested in the [Pose Correctives](#pose-correctives), you also need to use the check `Import Morph Targets`.

![import00](images/readme_import03.png)

📝 If you are importing a single frame .FBX, for example if you [created a SMPL-body from an image](https://me.meshcapade.com/from-photos), also check `Use T0 As Ref Pose`.
</details>

<details>
<summary>V. Retargeting the animation</summary>

One thing you may want to do is retarget the motion from the SMPL-body onto the body of your character.  To do so, you will need a retargeter.  Retargeters require two IK rigs: one for the source body, the SMPL-body in this case, and one for the target body - your character.  The Meshcapade Unreal plugin comes with a sample retargeter for the Unreal mannequin, including an IK rig for the SMPL-body and an IK rig for the Unreal mannequin. There are different retargetters based on whether you want to retarget the `.FBX` or the `.GLB`. If you already have a retargeter from the Unreal mannequin to your character, then this will provide a straightforward way to get motion from a SMPL-body directly onto your character.   

### A. Retargeting animation

To use the retargeters that ship with the Meshcapade plugin, simply right-click on an animation file (it will have a dark green bar in the middle of it), and select `Retarget Animation Assets` > `Duplicate and Retarget Animation Assets/Blueprints`.

![retarget4](images/readme_retarget04.png)

Select the retargeter you'd like to use.  If the file was imported as a `.GLB`, choose `RTG_Meshcapade_to_ue5_glb`.  If the file was imported as a `.FBX`, choose `RTG_Meshcapade_to_ue5_fbx`.

![retareget5](images/readme_retarget05.png)

This process will create a new animation asset for your character.  Here's an example of the retargeted animation next to the original animation.

[![Retargeting Example](images/readme_preview_retargetingexample.png)](https://youtu.be/dDYhbGmUmCA "Retarget Example")

### B. Making your own IK rig

If you want to make a retargeter, the first thing you need to do is make an IK Rig for your character.  In the top right corner of the Content Browser, click on `Settings` and make sure `Show Plugin Content` is checked.  Then open `Plugins` > `Meshcapade Content` > `Rigs`.  Duplicate the `IK_Manniquen` rig.

![ik rig0](images/readme_ikrig00.png)

If your character's skeleton follows the UE5 character convention, you only need to change the preview skeletal mesh to your character.  If you're using a UE4 character, you may need to change the `End Bone` of the `Spine` IK chain to `spine_03`.

![ik rig1](images/readme_ikrig01.png)

For more information on this subject, see the Unreal documentation on [IK Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

### C. Making your own retargeter
Once you have the IK rig for your character created, you can make a retargeter.  Right-click in the Content Browser and type `retargeter` or go to `Animation` > `Retargeting` > `IK Retargeter`.  Double-click the newly created retargeter.

A retargeter contains two IK rigs and the relationship between them.  Set the two IK rigs in the details panel.

![retarget0](images/readme_retarget00.png)

The poses of the two skeletons need to match as well.  To do this, change the display mode to `Edit Retarget Pose` on the top left.  Then rotate the bones of the source and/or the target until the angles match one another as closely as possible.

![retarget1](images/readme_retarget01.png)

Finally, the chains of the two IK rigs need to be correlated.  There are several ways to do this, but if you copied the Unreal mannequin all you need to do is click `Auto-Map Chains` > `Map All (Exact)`.

![retarget2](images/readme_retarget02.png)

For more information on this subject, see the Unreal documentation on [IK Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

</details>

<details>
<summary>VI. Editing the animation</summary>

If the animation doesn't look right on your character, there are two options:  
1. The first is to go back to the platform and try to get something more suitable.  You can go to the [motion from video](https://me.meshcapade.com/from-videos) page and upload a different video to get different results, or you can go to the [motion from text](https://me.meshcapade.com/editor) section of the editor and try to search for a more suitable animation using a different prompt.
2. The second thing you can do is edit the animation after the fact, and there are several ways to do this.  An easy way to do this which also gives you lots of control, is to use a control rig that has a forward and backward solver.

The control rig that comes with the third-person template, which we also ship with the plugin, is sufficient for this.  In the content browser, go to `Plugins` > `Meshcapade Content` > `Rigs` and duplicate the `CR_Mannequin_Body` rig.

![controlrig0](images/readme_controlrig00.png)

You will have to make edits to this control rig depending on how different your character's skeleton is from the Unreal conventional skeleton.

In the `Preview Scene Settings`, change the preview mesh to that of your character.

If you are retargeting a UE4 character, for example, you would need to make a few changes to the skeleton.  In the Rig Hierarchy, you can rearrange bones by clicking and dragging them.  The spine, neck, and hands are in different places in the UE4 and UE5 conventional skeletons.  You would need to make the following changes:
- Move `clavicle_l`, `clavicle_r` and `neck_01` to be underneath `spine_03`
- Move `head` to be underneath `neck_01`
- On both hands, move `index_01`, `middle_01`, `ring_01`, and `pinky_01` to be direct children of their corresponding `hand` bones.

![controlrig1](images/readme_controlrig01.png)

For more information on this subject, see the Unreal documentation on [Control Rig](https://docs.unrealengine.com/5.3/en-US/control-rig-in-unreal-engine/).

Once you have a control rig that works with your character, you can bake the animation onto that control rig.  Make a new level sequence by right-clicking and typing `level sequence` or going to `Cinematics` > `Level Sequence`.  Drag the animation asset into your level, select it, and then in the sequencer select `+Track` > `Actor To Sequencer` > `<your animation asset>`.

Click the `+` to the right of `Animation` and add your animation asset.

Right-click on the top node of your animation in the track panel and choose `Bake to Control Rig` > `<your control rig>`.  Click `Create`.

Note: the animation will only bake what's between the red and green markers on the timeline.  If you want to trim the animation, you can do it by moving the markers.

[![Animation Editing Example 1](images/readme_preview_animediting0.png)](https://youtu.be/FoIkByz4ePU "Animation Editing Example 1")

Select the new control rig layer on the track, right-click, and choose `Add Section` > `Additive`.  This will allow you to add an animation on top of the existing animation.

![anim editing1](images/readme_animediting00.png)

At this point, you can spend as little or as much time as you'd like to make the animation do what you want to do. In the example below, I tweak the height of the global control so that the character doesn't clip the ground as much as he bends forward.  You could then fix the hands and fingers or, cartoony motion, etc.

[![Animation Editing Example 2](images/readme_preview_animediting1.png)](https://youtu.be/tRF8h6V9KIw "Animation Editing Example 2")

Once you're happy with your animation, the last step is to bake it.  Right-click on the top node in the track panel, choose `Bake Animation Sequence`, and save it.  Now your edited animation can be used as normal.

![anim editing1](images/readme_animediting01.png)

</details>

<details id='pose-correctives'>
<summary>VII. Using Pose correctives</summary>

Pose correctives allow for real-time calculation of pose-based deformations to SMPL-bodies.  They are a complex set of blend shapes that we apply based on the pose of the skeleton.  This achieves much more realistic soft tissue deformation than the traditional skinning method.  They are also extremely easy to apply to actor blueprints.

[![Pose Corrective Explanation](images/readme_preview_posecorrective0.png)](https://youtu.be/CxJnpEXfjG0 "Pose Corrective Explanation")

<center> 
<span style="font-size:.9em;">

_In the example above, the body on the left shows the motion with the pose correctives applied, <br>and the body on the right shows the pose correctives without the motion._

</span>
</center>

📝 To be able to use pose correctives, make sure you enable `Import Morph Targets` in the [import step](#importing_glb) when you import a SMPL-body.

To enable pose correctives on blueprint actor, add a skeletal mesh component that contains a SMPL-body, then add the `Pose Correctives` actor component to the same blueprint.

[![Adding Pose Correctives](images/readme_preview_posecorrective1.png)](https://youtu.be/ZKWhLW5n00c "Adding Pose Correctives")

The example below has two bodies overlapping to illustrate the result further.  The orange body doesn't have pose correctives, the textured body does.

[![Pose Correctives in Unreal](images/readme_preview_posecorrective2.png)](https://youtu.be/3F3ReRXnuV4 "Pose Correctives in Unreal")
</details>

For any questions, please [contact us](https://meshcapade.com/contact).