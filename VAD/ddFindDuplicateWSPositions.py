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
from functools import partial


class DuplicateWSPositionResults_GUI(object):
    '''
    Gui to collect user input for creating layout screen boards
    '''
    WIN_NAME = 'duplicateWSPositionResultsWin'

    def __init__(self, found_assets):
        '''
        initialize instance variables
        '''
        self.found_assets = found_assets

        # initialize main gui components
        self._window = None
        self._main_flayout = None
        self._close_button = None
        self._scroll_collection_form = None
        self._dup_scroll_form = None
        self._dup_scroll_list = None
        self._origins_scroll_form = None
        self._origins_scroll_list = None

        # prep for gui building
        self._remove_existing()
        self._build_ui()

    def _build_ui(self):
        '''
        Build a one to two scroll list gui to display found
            duplicate positional assets
        '''
        # initialize basic window dimensions to start with
        base_height = {'single': 265, 'double': 480}
        base_width = 625
        use_height = 'single'

        self._window = mc.window(
                        self.WIN_NAME,
                        title='dd Find Duplicate World Space Position Results',
                        sizeable=True,
                        resizeToFitChildren=True,
                        widthHeight=(base_width, base_height['single']))

        self._main_flayout = mc.formLayout(numberOfDivisions=100)

        # kick off creation of scroll list region
        #   quit build of gui asset if region(s) were not built
        if not self._build_scroll_form():
            print "Data for scroll list(s) not located. Halting GUI Build."
            return

        self._close_button = mc.button(label='Close', height=30,
                                    parent=self._main_flayout,
                                    command=self._remove_existing,
                                    annotation="Close window.")

        # attach region and controls to gui's main layout
        mc.formLayout(self._main_flayout, edit=True,
                attachForm=[
                            (self._scroll_collection_form, 'top', 10),
                            (self._scroll_collection_form, 'left', 10),
                            (self._scroll_collection_form, 'right', 10),
                            (self._scroll_collection_form, 'bottom', 10),
                            (self._close_button, 'left', 10),
                            (self._close_button, 'bottom', 10),
                            (self._close_button, 'right', 10)
                    ],
                attachControl=[
                            (self._scroll_collection_form, "bottom",
                                                        5, self._close_button)
                    ]
                )

        # determine if gui window should be resized based on scroll lists built
        if self._dup_scroll_form and self._origins_scroll_form:
            use_height = 'double'

        mc.window(self._window, edit=True,
                  widthHeight=(base_width, base_height[use_height]))

    def _build_scroll_form(self):
        '''
        Build gui region layout that contains the scroll lists
        '''
        # create layout for entire scroll list region
        self._scroll_collection_form = mc.columnLayout(columnAlign="center",
                                                    adjustableColumn=True,
                                                    parent=self._main_flayout)

        # determine if should create a scroll list for duplicate world space
        if self.found_assets['ws_dupes']:
            self._build_duplicates_scroll_list()
            self._fill_scroll_list(self._dup_scroll_list,
                                            self.found_assets['ws_dupes'])

        # determine if should create a scroll list for assets at origin
        if self.found_assets['origin']:
            if self._dup_scroll_form:
                # add a separator between the two intended scroll lists
                sep = mc.separator(horizontal=True, style="in", height=10,
                                    parent=self._scroll_collection_form)
            self._build_origins_scroll_list()
            self._fill_scroll_list(self._origins_scroll_list,
                                                self.found_assets['origin'])

        # cancel build of gui if no scroll list forms were built
        if not self._dup_scroll_form and not self._origins_scroll_form:
            return False

        return True

    def _build_duplicates_scroll_list(self):
        '''
        Prep default values and kick of build of scroll list for
            duplicate world space assets
        '''
        scroll_label = "Discovered Legal Assets with World Space Duplicates:"
        scroll_annotate = "Displays a listing of legal assets there were " \
                        + "discovered to have the same world space pivot as " \
                        + "other assets in the scene."

        self._dup_scroll_form, self._dup_scroll_list = \
                            self._build_scroll_list(
                                            scroll_label,
                                            scroll_annotate,
                                            self._scroll_collection_form)

    def _build_origins_scroll_list(self):
        '''
        Prep default values and kick of build of scroll list for
            assets located at the origin
        '''
        scroll_label = "Discovered Legal Assets Located at Origin:"
        scroll_annotate = "Displays a listing of legal assets there were " \
                        + "discovered to be located at the origin"

        self._origins_scroll_form, self._origins_scroll_list = \
                            self._build_scroll_list(
                                            scroll_label,
                                            scroll_annotate,
                                            self._scroll_collection_form)

    @classmethod
    def _build_scroll_list(cls, ulabel, uannotate, uparent):
        '''
        Build a scroll list region that also contains a label based
            on specified details

        :type   ulabel: C{str}
        :param  ulabel: descriptive label to describe text scroll list below
        :type   uannotate: C{str}
        :param  uannotate: descriptive tool tip to be displayed over list
        :type   uparent: C{Maya UI Layout Component}
        :param  uparent: parent layout region that should contain build controls
        '''
        scroll_format = mc.columnLayout(parent=uparent, adjustableColumn=True)
        scroll_label = mc.text(label=ulabel, align='left', parent=scroll_format)
        scroll_list = mc.textScrollList(allowMultiSelection=True,
                            parent=scroll_format, annotation=uannotate)
        mc.textScrollList(scroll_list, edit=True,
                  selectCommand=partial(cls._do_select_items, scroll_list))

        return scroll_format, scroll_list

    @classmethod
    def _do_select_items(cls, scroll_list):
        '''
        Selects listed item in scene file.

        :type   scroll_list: C{Maya Text Scroll List Control Object}
        :param  scroll_list: text field scroll list to find selected
        '''
        selectedItems = cls._get_selected_items(scroll_list)
        if selectedItems:
            try:
                mc.select(selectedItems, replace=True)
            except:
                pass

    @staticmethod
    def _get_selected_items(scroll_list):
        '''
        Returns selected item from list.

        :type   scroll_list: C{Maya Text Scroll List Control Object}
        :param  scroll_list: text field scroll list to find selected
        '''
        return mc.textScrollList(scroll_list, query=True, selectItem=True)

    @staticmethod
    def _fill_scroll_list(scroll_list, list_elements):
        '''
        Fill in the specified scroll list with the passed elements

        :type   scroll_list: C{Maya Text Scroll List Control Object}
        :param  scroll_list: text field scroll list to be filled
        :type   list_elements: C{list}
        :param  list_elements: list of elements to add to scroll list
        '''
        for asset in list_elements:
            mc.textScrollList(scroll_list, edit=True, append=asset)

    def _remove_existing(self, *args):
        '''
        check if an instance of the window already exists, if so delete it
        '''
        if mc.window(self.WIN_NAME, query=True, exists=True):
            mc.deleteUI(self.WIN_NAME)

    def show_win(self):
        '''
        show instance gui
        '''
        mc.showWindow(self._window)


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
        asset_node = mc.listRelatives(trans_node, parent=True, fullPath=True)
        if asset_node:
            grp_patt = re.compile("_GRP_")
            if grp_patt.search(asset_node[0].rpartition("|")[-1]):
                assets.append(asset_node[0])

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
        apivots = mc.xform(asset, query=True, worldSpace=True,
                                            absolute=True, pivots=True)

        # check if pivot exists at origin
        if is_at_origin(apivots):
            found_positions['origin'].append(asset)
            continue

        # iterate over scene assets for comparisons
        for test_asset in found_assets:
            # skip testing if both assets are the same
            if test_asset == asset:
                continue

            # collect test asset world positions
            tpivots = mc.xform(test_asset, query=True, worldSpace=True,
                                            absolute=True, pivots=True)

            # check if position elements match
            ps_found = 0
            for attr in range(len(apivots)):
                if apivots[attr] == tpivots[attr]:
                    ps_found += 1

            # add test asset if all transform information matched
            if ps_found == len(apivots):
                found_positions['ws_dupes'].append(test_asset)
                ws_dupes.append(test_asset)

    # clean up list of found assets to eliminate duplicate assets in lists
    found_positions['origin'] = list(set(found_positions['origin']))
    found_positions['ws_dupes'] = list(set(found_positions['ws_dupes']))
    mc.waitCursor(state=False)

    return found_positions


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

            # prep and display results in a gui window
            results_win = DuplicateWSPositionResults_GUI(located_assets)
            results_win.show_win()
        else:
            msg = "No duplicate world space assets were located."

    mc.confirmDialog(title="", messageAlign="center", message=msg,
                     button=["OK"], defaultButton="OK")

    print "Completed search."