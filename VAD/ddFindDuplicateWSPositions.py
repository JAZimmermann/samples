#
# Confidential and Proprietary Source Code
#
# This Digital Domain Productions, Inc. source code, including without
# limitation any human-readable computer programming code and associated
# documentation (together "Source Code"), contains valuable confidential,
# proprietary and trade secret information of Digital Domain Productions and is
# protected by the laws of the United States and other countries. Digital
# Domain Productions, Inc. may, from time to time, authorize specific employees
# to use the Source Code internally at Digital Domain Production Inc.'s premises
# solely for developing, updating, and/or troubleshooting the Source Code. Any
# other use of the Source Code, including without limitation any disclosure,
# copying or reproduction, without the prior written authorization of Digital
# Domain Productions, Inc. is strictly prohibited.
#
# Copyright (c) [2012] Digital Domain Productions, Inc. All rights reserved.
#
# $URL$
# $Date: 2014-10-13$
# $Revision: 1.0$
# $Author: johnz $
#

import maya.cmds as mc

import re


def get_assets():
    '''
    check all geometry assets in scene in order to collect all unique assets
    '''
    print "Locating geometry assets in scene.."
    geometry = mc.ls(geometry=True)
    # print geometry
    assets = []
    for geo in geometry:
        trans_node = mc.listRelatives(geo, parent=True, fullPath=True)[0]
        asset_node = mc.listRelatives(trans_node, parent=True, fullPath=True)[0]
        grp_patt = re.compile("_GRP_")
        if grp_patt.search(asset_node.rpartition("|")[-1]):
            assets.append(asset_node)

    return list(set(assets))


def is_at_origin(t_pivot):
    '''
    check if the asset's position is located at the origin

    :param t_pivot:
    '''
    found = 0
    for i in range(3):
        if t_pivot[i] == 0:
            found += 1

    if found == 3:
        return True

    return False


def check_for_dupe_positions(found_assets):
    '''
    test world space position of each asset against positions of scene assets
    :param found_assets:
    :return:
    '''
    print "Checking assets for similar world space positions or at origin..."
    # initialize list for duplicate position assets
    found_positions = {'ws_dupes': [], 'origin': []}
    ws_dupes = []

    mc.waitCursor(state=True)

    # check each asset
    for asset in found_assets:
        # collect world space positions for asset
        # trans = mc.xform(asset, query=True, worldSpace=True,
        #                                     absolute=True, translation=True)
        # rots = mc.xform(asset, query=True, worldSpace=True,
        #                                     absolute=True, rotation=True)

        apivots = mc.xform(asset, query=True, worldSpace=True,
                                            absolute=True, pivots=True)

        if is_at_origin(apivots):
            found_positions['origin'].append(asset)
            continue

        # TODO:: potentially do multiple lists, one for dupes and one for objects at origins

        # iterate over scene assets for comparisons
        for test_asset in found_assets:
            # skip testing if both assets are the same
            if test_asset == asset:
                continue

            # collect test asset world positions
            # test_trans = mc.xform(test_asset, query=True, worldSpace=True,
            #                                     absolute=True, translation=True)
            # test_rots = mc.xform(test_asset, query=True, worldSpace=True,
            #                                     absolute=True, rotation=True)

            tpivots = mc.xform(test_asset, query=True, worldSpace=True,
                                            absolute=True, pivots=True)

            # check if position elements match
            # trans_found = 0
            # rots_found = 0
            ps_found = 0
            # for pos in range(len(trans)):
            #     if trans[pos] == test_trans[pos]:
            #         print "%f == %f" % (trans[pos], test_trans[pos])
            #         trans_found += 1
            #     if rots[pos] == test_rots[pos]:
            #         print "%f == %f" % (rots[pos], test_rots[pos])
            #         rots_found += 1
            for attr in range(len(apivots)):
                if apivots[attr] == tpivots[attr]:
                    ps_found += 1

            # add test asset if all transform information matched
            # if (trans_found == len(trans)) and (rots_found == len(rots)):
            if ps_found == len(apivots):
                found_positions['ws_dupes'].append(test_asset)
                ws_dupes.append(test_asset)

    found_positions['origin'] = list(set(found_positions['origin']))
    found_positions['ws_dupes'] = list(set(found_positions['ws_dupes']))
    mc.waitCursor(state=False)

    return found_positions
    # return list(set(ws_dupes))


def select_duplicates():
    '''
    check scene for and select assets with same world space positions
    '''
    msg = ''
    # collect legal assets in the scene
    assets = get_assets()
    if not assets:
        msg = "Was unable to locate any legal assets in the scene to check."
    else:
        # locate duplicate positioned scene assets
        located_assets = check_for_dupe_positions(assets)

        # display results to user
        if located_assets['ws_dupes'] or located_assets['origin']:
            mc.select(located_assets['ws_dupes'])
            msg = "Found the following %d assets that " \
                                        % len(located_assets['ws_dupes']) \
                                        + "have duplicate world space positions"
            print "%s:" % msg
            print "\n".join(located_assets['ws_dupes'])

            if located_assets['origin']:
                o_msg = "Found %d assets sitting at the origin" \
                                                % len(located_assets['origin'])
                print "%s:" % o_msg
                print "\n".join(located_assets['origin'])
                msg = "%s.\n%s" % (msg, o_msg)

            msg += ".\nEach has been selected for review and " \
                                        + "also printed to the Script Editor."
        else:
            msg = "No duplicate world space assets were located."

    mc.confirmDialog(title="", messageAlign="center", message=msg,
                     button=["OK"], defaultButton="OK")

    print "Completed search."