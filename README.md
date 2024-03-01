# Meshcapade Unreal Plugin

<span style="color:magenta">TODO: Change the "Go to GitHub Repository" to just "GitHub" with the octocat icon @gabriele</span>
<br/>
<span style="color:magenta">TODO: @simay/@gabriele figure out the buttons for two plugins FE</span>
<br/>
<span style="color:magenta">TODO: make all sections collapsable @gabriele</span>
<br/>
<span style="color:magenta">TODO: we will need to add a windows icon to the download button</span>
<br/>
<span style="color:magenta">TODO: convert all .gifs to video and send them to nathan @gabriele</span>
<br/>
<span style="color:magenta">TODO: put them on youtube and link them @nathan</span>

This plugin allows you to quickly retarget motions created on the [Meshcapade.me](https://meshcapade.me/) platform onto your own characters in [Unreal Engine 5](https://www.unrealengine.com/en-US/download). 

## I. Adding the plugin to your Unreal project

[Download](https://codeload.github.com/Meshcapade/mc-unreal/zip/refs/tags/v0.0.1) the Unreal Plugin or grab from our [git repo](https://github.com/Meshcapade/mc-unreal).

Make sure your Unreal project is closed.  Unzip the plugin and drop the `Plugins` folder into the top level of your Unreal project.

![adding plugins to unreal project](images/readme_plugins.gif)

## II. Getting animation from [Meshcapade.me](https://meshcapade.me/)
Currently, there are two ways to get animations from [Meshcapade.me](https://meshcapade.me/): 
- [Motion from video](https://me.meshcapade.com/from-videos) - extract the human motion from a video.

<span style="color:yellow">do we want this tidbit about how many animations? I just made up 10,000</span></br>
- [Motion from text](https://me.meshcapade.com/editor) - find a human motion in our library of 10,000 motions.  
### A. [Motion from video](https://me.meshcapade.com/from-videos)
to get an animation from a video, visit 
https://me.meshcapade.com/from-videos.  Follow the prompts until you've created an animated avatar.

![from video](images/readme_afv00.png)

### B. [Motion from text](https://me.meshcapade.com/editor)
To search for a motion from our motion library, visit https://me.meshcapade.com/editor. In the top right, there is a search box where you can search for an animation.  Once you've found the animation you want, save the avatar into your vault.

![from text](images/readme_tmr00.png)

</details>

## III. Download the .FBX
Go to your [avatar vault](https://me.meshcapade.com/vault), and click the `...` on the top right corner of the avatar containing the motion you'd like to download.  In the download options, make sure that `file format` is `fbx` (`obj` has no motion) and `Pose/Motion` is `Captured Motion`.  For `compatibility mode`, select `Unreal` if you are interested in using the SMPL-body with pose correctives.  Choose `Unreal - no blend shapes` if you're only interested in the motion, this will make the import process faster.  Choose `Unreal` if you're following the [Advanced Features](#vii-advanced-features) workflow.

<span style="color:magenta">TODO: update this image when possible</span>

![download](images/readme_download00.png)

## IV. Import the .FBX into Unreal

With the .FBX downloaded, import it into your unreal project (File > Import).  

Set the skeleton to `SK_MeshcapadeBody`.  If you don't see it, then click the gear next to the search box and make sure `Show Plugin Content` is checked.  In the content browser, `SK_MeshcapadeBody` is located here: `Content/Plugins/Meshcapade/Meshes/SK_MeshcapadeBody`.

![import00](images/readme_import00.png)

Be sure that `Import Animation` is checked.  

If you’re interested in the [Advanced Features](#vii-advanced-features), you need to use the check `Import Morph Targets`. 

![import00](images/readme_import03.png)

## V. Retargeting animation
One thing you may want to do is retarget the motion from the SMPL-body onto the body of your character.  To do so, you will need a retargeter.  Retargeters require two IK rigs: one for the source body, the SMPL-body in this case, and one for the target body - your character.  The Meshcapade Unreal plugin comes with a sample retargeter for the Unreal mannequin, including an IK rig for the SMPL-body and an IK rig for the Unreal mannequin.

### A. Making your own IK rig

First, you need to make an IK Rig for your character.  In the top right corner of the Content Browser, click on `Settings` and make sure `Show Plugin Content` is checked.  Then open `Plugins` > `Meshcapade Content` > `Rigs`.  Duplicate the `IK_Manniquen` rig. 

![ik rig0](images/readme_ikrig00.png)

If your character's skeleton follows the Unreal character naming convention, you only need to change the preview skeletal mesh to your character.  If you're using a UE4 character, you may need to change the `End Bone` of the `Spine` IK chain to `spine_03`.  

![ik rig1](images/readme_ikrig01.png)

For more on this subject, see the Unreal documentation on [IK Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

### B. Making your own retargeter
Once you have the IK rig for your character created, you can make a retargeter.  Right-click in the Content Browser and type `retargeter` or go to `Animation` > `Retargeting` > `IK Retargeter`.  Double-click the newly created retargeter.  

A retargeter contains two IK rigs and the relationship between them.  Set the two IK rigs in the details panel.

![retarget0](images/readme_retarget00.png)

The poses of the two skeletons need to match as well.  To do this, change the display mode to `Edit Retarget Pose` on the top left.  Then rotate the bones of the source and/or the target until the angles match one another as closely as possible.   

![retarget1](images/readme_retarget01.png)

Finally, the chains of the two IK rigs need to be correlated.  There are several ways to do this, but if you copied the Unreal mannequin all you need to do is click `Auto-Map Chains` > `Map All (Exact)`.  

![retarget2](images/readme_retarget02.png)

For more, see the Unreal documentation on [IK Rig Animation Retargeting](https://docs.unrealengine.com/5.3/en-US/ik-rig-animation-retargeting-in-unreal-engine/).

### C. Retargeting animation
Now that the retargeter is built, it can be used to retarget any number of animations between the SMPL-body and the body of your character.  To do so, simply right-click on an animation file (it will have a dark green bar in the middle of it), and select `Retarget Animation Assets` > `Duplicate and Retarget Animation Assets/Blueprints`.

![retarget4](images/readme_retarget04.png)

Select the retargeter you'd like to use

![retareget5](images/readme_retarget05.png)

Here's an example of the retargeted animation next to the original animation

![retarget example](https://youtu.be/dDYhbGmUmCA)

## VI. Editing animation

If the animation doesn't look right on your character, there are two options.  One is to go back to the platform and try to get something better, or to edit the motion.  There are several ways to edit an animation after the fact.  One way that is easy to use and gives you lots of control is to use a control rig that has a forward and backward solver.

The control rig that comes with the third-person template, which we also ship with the plugin, is sufficient for this.  Go to `Plugins` > `Meshcapade Content` > `Rigs` and duplicate the `CR_Mannequin_Body` rig.  

![controlrig0](images/readme_controlrig00.png)

You will have to make edits to this control rig depending on how different your character's skeleton is from the Unreal convention.  

![controlrig1](images/readme_controlrig01.png)

In the `Preview Scene Settings`, change the preview mesh to that of your character.  

If you are retargeting a UE4 character, for example, you would need to make a few changes to the skeleton.  In the Rig Hierarchy, you can rearrange bones by clicking and dragging them.  The spine, neck and hands are different between the UE4 and UE5 characters.  You'd make the following changes:
- Move `clavicle_l`, `clavicle_r` and `neck_01` to be underneath `spine_03`
- Move `head` to be underneath `neck_01`
- On both hands, move `index_01`, `middle_01`, `ring_01`, and `pinky_01` to be direct children of their corresponding `hand` bones.

For more, see the Unreal documentation on [Control Rig](https://docs.unrealengine.com/5.3/en-US/control-rig-in-unreal-engine/).

Now that you have a control rig that works with your character, you can bake the animation onto that control rig.  Make a new level sequence by right-clicking and typing `level sequence` or going to `Cinematics` > `Level Sequence`.  Drag the animation asset into your level, select it, and then in the sequencer select `+Track` > `Actor To Sequencer` > `<your animation asset>`.  

Click the `+` to the right of `Animation` and add your animation asset.

Right-click on the top node of your animation in the track panel and choose `Bake to Control Rig` > `<your control rig>`.  Click `Create`.

Note: the animation will only bake what's between the red and green markers on the timeline.  If you want to trim the animation, you can do it by moving the markers.

![anim editing0](https://youtu.be/FoIkByz4ePU)

Select the new control rig layer on the track and right-click and choose `Add Section` > `Additive`.  This will allow you to add animation on top of the existing animation.

![anim editing1](images/readme_animediting00.png)

At this point, you can spend as little or as much time as you'd like to make the animation do what you want to do. In the example below, I tweak the height of the global control so that the character doesn't clip the ground as much as he bends forward.  You could then fix the hands and fingers or add cartoony motion.

![anim editing1](https://youtu.be/tRF8h6V9KIw)

Once you're happy with your animation, the last step is to bake it.  Right-click on the top node in the track panel and choose `Bake Animation Sequence` and save it.  Now your edited animation can be used as normal.

![anim editing1](images/readme_animediting01.png)

## VII. Pose correctives
Pose correctives allow for real time calculation of pose based deformations to SMPL-bodies, and it's extremely easy to apply to actor blueprints.  They are a complex set of blend shapes that we apply based on the pose of the skeleton.  This achieves much more realistic soft tissue deformation than the traditional skinning method.

![pose correctives](https://youtu.be/CxJnpEXfjG0)

In order to be able to use pose correctives, make sure you enable `Import Morph Targets` in the [import step](#v-import-the-fbx-into-unreal) when you import a SMPL-body. 

To enable pose correctives on blueprint actor, add a skeletal mesh component that contains a SMPL-body, then add the `Pose Correctives` actor component to the same blueprint.

![add pose correctives](https://youtu.be/ZKWhLW5n00c)

The example below has two bodies overlaying each other to further illustrate the result.  The orange body doesn't have pose correctives, and the textured body does. 

![pose corrective example](https://youtu.be/3F3ReRXnuV4)


<details>
<summary><h2>VIII. Collapsable fake section<h2></summary>

words more words

words more words

words more words

words more words

words more words

words more words

words more words

</details>


<details>
<summary>IX. Collapsable fake section take two</summary>

words more words

words more words

words more words

words more words

words more words

words more words

words more words

</details>