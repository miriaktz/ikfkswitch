import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import math


# UI

def ik_fk_switch_ui():
    window = cmds.window(title='IK/FK Switch', width=270)

    cmds.columnLayout(adjustableColumn=True)


    cmds.separator(height=10)


    cmds.rowLayout(numberOfColumns=2, adjustableColumn=True)
    cmds.button(label='Create IK Setup', width=135, command='create_ik_setup()')
    cmds.button(label='Create FK Setup', width=135, command='create_fk_setup()')
    cmds.setParent('..')

    cmds.separator(height=10)

    cmds.button(label='Create Connections/Switch', width=270, command='create_connections()')
    cmds.button(label='Create SDK Setup', width=270, command='create_sdk_setup()')


    cmds.showWindow(window)
    
ik_fk_switch_ui()



# functions



def create_ik_setup():

    selected_list = cmds.ls(selection=True)
    cmds.parent(world=True)
    dup_selected_list = cmds.duplicate(selected_list[1:], parentOnly=True)
    cmds.parent(selected_list[3], selected_list[2])
    cmds.parent(selected_list[2], selected_list[1])
    cmds.parent(selected_list[1], selected_list[0])
    count = 1
    renamed_list = []
    for item in dup_selected_list:
        new_item = cmds.rename(item, selected_list[count] + '_ik')
        renamed_list.append(new_item)
        count = count + 1
    cmds.parent(renamed_list[2], renamed_list[1])
    cmds.parent(renamed_list[1], renamed_list[0])
    cmds.parent(renamed_list[0], selected_list[0])

    cmds.select(renamed_list[0])
    cmds.hide(cmds.ls(selection=True))


    get_ctrl_name=[]
    name_split = selected_list[3].split('_')
    new_name = name_split[:2]
    new_name = '_'.join(new_name)
    get_ctrl_name.append(new_name)


    #ik ctrl
    ik_ctrl = cmds.circle(r=2, nr=(1, 0, 0), n=get_ctrl_name[0] + '_ctrl')
    cmds.matchTransform(ik_ctrl, renamed_list[2])
    zro_group = cmds.group(em=True, n=ik_ctrl[0] + '_zro')
    cmds.matchTransform(zro_group, ik_ctrl)
    cmds.parent(ik_ctrl, zro_group)
    cmds.orientConstraint(ik_ctrl[0], renamed_list[2], mo=True)
    cmds.setAttr(ik_ctrl[0] + '.scaleX', lock=True, keyable=False)
    cmds.setAttr(ik_ctrl[0] + '.scaleY', lock=True, keyable=False)
    cmds.setAttr(ik_ctrl[0] + '.scaleZ', lock=True, keyable=False)

    #PV setup
    start = cmds.xform(renamed_list[0], q=1, ws=1, t=1)
    mid = cmds.xform(renamed_list[1], q=1, ws=1, t=1)
    end = cmds.xform(renamed_list[2], q=1, ws=1, t=1)

    startV = OpenMaya.MVector(start[0], start[1], start[2])
    midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
    endV = OpenMaya.MVector(end[0], end[1], end[2])

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd

    proj = float(dotP) / float(startEnd.length())

    startEndN = startEnd.normal()

    projV = startEndN * proj

    arrowV = startMid - projV
    arrowV*= 50

    finalV = arrowV + midV


    cross1 = startEnd ^ startMid
    cross1.normalize()

    cross2 = cross1 ^ arrowV
    cross2.normalize()
    arrowV.normalize()

    matrixV = [arrowV.x, arrowV.y, arrowV.z, 0,
            cross1.x, cross1.y, cross1.z, 0,
            cross2.x, cross2.y, cross2.z, 0,
            0, 0, 0, 1]
            
    matrixM = OpenMaya.MMatrix()

    OpenMaya.MScriptUtil.createMatrixFromList(matrixV, matrixM)

    matrixFn = OpenMaya.MTransformationMatrix(matrixM)

    rot = matrixFn.eulerRotation()


    pv_ctrl = cmds.circle(r=1.5, nr=(0, 0, 1), n= get_ctrl_name[0] + '_pv_ctrl')
    cmds.xform(pv_ctrl[0], ws=1, t=(finalV.x, finalV.y, finalV.z))

    cmds.xform(pv_ctrl[0], ws=1, rotation=((rot.x/math.pi*180.0),
                                            (rot.y/math.pi*180.0),
                                            (rot.z/math.pi*180.0)))

    cmds.setAttr(pv_ctrl[0] + '.rotateX', lock=True, keyable=False)
    cmds.setAttr(pv_ctrl[0] + '.rotateY', lock=True, keyable=False)
    cmds.setAttr(pv_ctrl[0] + '.rotateZ', lock=True, keyable=False)
    cmds.setAttr(pv_ctrl[0] + '.scaleX', lock=True, keyable=False)
    cmds.setAttr(pv_ctrl[0] + '.scaleY', lock=True, keyable=False)
    cmds.setAttr(pv_ctrl[0] + '.scaleZ', lock=True, keyable=False)

    zro_group = cmds.group(em=True, n=pv_ctrl[0] + '_zro')
    cmds.matchTransform(zro_group, pv_ctrl)
    cmds.parent(pv_ctrl, zro_group)

    ikh = cmds.ikHandle( sj=renamed_list[0], ee=renamed_list[2], n= get_ctrl_name[0] + '_ikHandle')
    cmds.parent(get_ctrl_name[0] + '_ikHandle', ik_ctrl)
    cmds.poleVectorConstraint(pv_ctrl[0], get_ctrl_name[0] + '_ikHandle')
    cmds.select(ikh)
    cmds.hide(cmds.ls(selection=True))




def create_fk_setup():

    selected_list = cmds.ls(selection=True)
    cmds.parent(world=True)
    dup_selected_list = cmds.duplicate(selected_list[1:], parentOnly=True)
    cmds.parent(selected_list[3], selected_list[2])
    cmds.parent(selected_list[2], selected_list[1])
    cmds.parent(selected_list[1], selected_list[0])
    renamed_list = []
    count = 1
    for item in dup_selected_list:
        new_item = cmds.rename(item, selected_list[count] + '_fk')
        renamed_list.append(new_item)
        count = count + 1
    cmds.parent(renamed_list[2], renamed_list[1])
    cmds.parent(renamed_list[1], renamed_list[0])
    cmds.parent(renamed_list[0], selected_list[0])

    cmds.select(renamed_list[0])
    cmds.hide(cmds.ls(selection=True))


    #fk ctrl

    get_name_list=[]
    for item in selected_list:
        name_split = item.split('_')
        new_name = name_split[:2]
        new_name = '_'.join(new_name)
        get_name_list.append(new_name)

    ctrl_list = []
    zro_group_list = []
    count = 0
    for jnt in renamed_list:
        ctrl = cmds.circle(r=3, nr=(1, 0, 0), n=get_name_list[count] + '_ctrl')
        ctrl_list.append(ctrl)
        cmds.matchTransform(ctrl, jnt)
        zro_group = cmds.group(em=True, n=get_name_list[count] + '_ctrl_zro')
        zro_group_list.append(zro_group)
        cmds.matchTransform(zro_group, ctrl)
        cmds.parent(ctrl, zro_group)

        cmds.setAttr(ctrl[0] + '.translateX', lock=True, keyable=False)
        cmds.setAttr(ctrl[0] + '.translateY', lock=True, keyable=False)
        cmds.setAttr(ctrl[0] + '.translateZ', lock=True, keyable=False)
        cmds.setAttr(ctrl[0] + '.scaleX', lock=True, keyable=False)
        cmds.setAttr(ctrl[0] + '.scaleY', lock=True, keyable=False)
        cmds.setAttr(ctrl[0] + '.scaleZ', lock=True, keyable=False)

        count = count + 1
        
    cmds.parent(zro_group_list[2], ctrl_list[1][0])
    cmds.parent(zro_group_list[1], ctrl_list[0][0])

    cmds.orientConstraint(ctrl_list[0][0], renamed_list[0], mo=True)
    cmds.orientConstraint(ctrl_list[1][0], renamed_list[1], mo=True)
    cmds.orientConstraint(ctrl_list[2][0], renamed_list[2], mo=True)



def create_connections():

    selection = cmds.ls(selection=True)
    bind_jnt_list = selection[:3]
    ik_jnt_list = selection[3:6]
    fk_jnt_list = selection[6:]

    #ctrl

    get_ctrl_name=[]
    name_split = selected_list[3].split('_')
    new_name = name_split[:2]
    new_name = '_'.join(new_name)
    get_ctrl_name.append(new_name)

    switch_ctrl = cmds.circle(r=1.5, nr=(1, 0, 0), n= get_ctrl_name[0] + '_switch_ctrl')
    cmds.matchTransform(switch_ctrl, ik_jnt_list[2])
    cmds.move(0, 5, 0, switch_ctrl, r=True)
    zro_group = cmds.group(em=True, n=switch_ctrl[0] + '_zro')
    cmds.matchTransform(zro_group, switch_ctrl)
    cmds.parent(switch_ctrl, zro_group)
    cmds.parentConstraint(bind_jnt_list[2], zro_group, mo=True)
    cmds.setAttr(switch_ctrl[0] + '.translateX', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.translateY', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.translateZ', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.rotateX', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.rotateY', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.rotateZ', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.scaleX', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.scaleY', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.scaleZ', lock=True, keyable=False)
    cmds.setAttr(switch_ctrl[0] + '.visibility', lock=True, keyable=False)
    cmds.addAttr(longName='ikFkSwitch', defaultValue=0, keyable=True, min=0.0, max=1.0, dv=0.0)

    #node editor
    get_name_list=[]
    for jnt in bind_jnt_list:
        jnt_split = jnt.split('_')
        new_name = jnt_split[:2]
        new_name = '_'.join(new_name)
        get_name_list.append(new_name)
        
    upArm_bc_t = cmds.createNode('blendColors', n=get_name_list[0] + '_blendColor_transl')
    elbow_bc_t = cmds.createNode('blendColors', n=get_name_list[1] + '_blendColor_transl')
    wrist_bc_t = cmds.createNode('blendColors', n=get_name_list[2] + '_blendColor_transl')
    upArm_bc_r = cmds.createNode('blendColors', n=get_name_list[0] + '_blendColor_rot')
    elbow_bc_r = cmds.createNode('blendColors', n=get_name_list[1] + '_blendColor_rot')
    wrist_bc_r = cmds.createNode('blendColors', n=get_name_list[2] + '_blendColor_rot')

    cmds.connectAttr(ik_jnt_list[0] + '.translate', upArm_bc_t + '.color1')
    cmds.connectAttr(ik_jnt_list[1] + '.translate', elbow_bc_t + '.color1')
    cmds.connectAttr(ik_jnt_list[2] + '.translate', wrist_bc_t + '.color1')
    cmds.connectAttr(ik_jnt_list[0] + '.rotate', upArm_bc_r + '.color1')
    cmds.connectAttr(ik_jnt_list[1] + '.rotate', elbow_bc_r + '.color1')
    cmds.connectAttr(ik_jnt_list[2] + '.rotate', wrist_bc_r + '.color1')
    cmds.connectAttr(fk_jnt_list[0] + '.translate', upArm_bc_t + '.color2')
    cmds.connectAttr(fk_jnt_list[1] + '.translate', elbow_bc_t + '.color2')
    cmds.connectAttr(fk_jnt_list[2] + '.translate', wrist_bc_t + '.color2')
    cmds.connectAttr(fk_jnt_list[0] + '.rotate', upArm_bc_r + '.color2')
    cmds.connectAttr(fk_jnt_list[1] + '.rotate', elbow_bc_r + '.color2')
    cmds.connectAttr(fk_jnt_list[2] + '.rotate', wrist_bc_r + '.color2')

    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', upArm_bc_t + '.blender')
    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', elbow_bc_t + '.blender')
    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', wrist_bc_t + '.blender')
    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', upArm_bc_r + '.blender')
    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', elbow_bc_r + '.blender')
    cmds.connectAttr(switch_ctrl[0] + '.ikFkSwitch', wrist_bc_r + '.blender')

    cmds.connectAttr(upArm_bc_t + '.output', bind_jnt_list[0] + '.translate')
    cmds.connectAttr(elbow_bc_t + '.output', bind_jnt_list[1] + '.translate')
    cmds.connectAttr(wrist_bc_t + '.output', bind_jnt_list[2] + '.translate')
    cmds.connectAttr(upArm_bc_r + '.output', bind_jnt_list[0] + '.rotate')
    cmds.connectAttr(elbow_bc_r + '.output', bind_jnt_list[1] + '.rotate')
    cmds.connectAttr(wrist_bc_r + '.output', bind_jnt_list[2] + '.rotate')


def create_sdk_setup():
    #sdk
    selection = cmds.ls(selection=True)
    driver = selection[0]
    ik_ctrls = selection[1:3]
    fk_ctrls = selection[3]

    cmds.setDrivenKeyframe(ik_ctrls[0], at='visibility', v=0.0, cd=driver + '.ikFkSwitch', dv=0.0)
    cmds.setDrivenKeyframe(ik_ctrls[1], at='visibility', v=0.0, cd=driver + '.ikFkSwitch', dv=0.0)
    cmds.setDrivenKeyframe(ik_ctrls[0], at='visibility', v=1.0, cd=driver + '.ikFkSwitch', dv=1.0)
    cmds.setDrivenKeyframe(ik_ctrls[1], at='visibility', v=1.0, cd=driver + '.ikFkSwitch', dv=1.0)

    cmds.setDrivenKeyframe(fk_ctrls, at='visibility', v=0.0, cd=driver + '.ikFkSwitch', dv=1.0)
    cmds.setDrivenKeyframe(fk_ctrls, at='visibility', v=1.0, cd=driver + '.ikFkSwitch', dv=0.0)

    confirmation_popup()

def confirmation_popup():
    result = cmds.confirmDialog(title='Confirmation',
                                message='Setup is done!',
                                button='Ok')
    print(result)