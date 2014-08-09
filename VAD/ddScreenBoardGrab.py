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
# $Date: 2014-07-30$
# $Revision: 1.0$
# $Author: johnz $
#


import maya.cmds as mc
import maya.mel as mel

import os
import re

from mayatools.VAD import ddConstants


class BoardCamera(object):
    def __init__(self):
        '''
        initialize instance variables
        '''
        self._camera = None
        self._camera_shape = None
        self._home_position = None
        self._orig_prescale = None
        self._orig_near_clip_plane = None
        self._orig_far_clip_plane = None

        # bookmark related
        self._bookmarks = None
        self._cur_bookmark = None
        self._includes_prefix = ['board']
        self._excludes = {'prefix': [],
                        'postfix': []}

    @property
    def camera(self):
        '''
        get name for camera
        '''
        return self._camera

    @camera.setter
    def camera(self, cam):
        '''
        set and process base details specified camera

        :type   cam: C{str}
        :param  cam: camera to be object
        '''
        cam_shape = mc.listRelatives(cam, type='camera')[0] or ''
        if not cam_shape:
            raise TypeError("%s is not a camera" % cam)
        self._camera = cam

        #setup base details
        self.cam_shape = cam_shape
        self.home_position = cam
        self._get_original_attrs()

    @property
    def cam_shape(self):
        '''
        get shape name for camera
        '''
        return self._camera_shape

    @cam_shape.setter
    def cam_shape(self, cam_shape):
        '''
        set the shape of the camera

        :type   cam_shape: C{str}
        :param  cam_shape: camera shape name
        '''
        self._camera_shape = cam_shape

    @property
    def home_position(self):
        '''
        get original view position for camera
        '''
        return self._home_position

    @home_position.setter
    def home_position(self, cam):
        '''
        set the original view position of camera before processing

        :type   cam: C{str}
        :param  cam: camera for view position
        '''
        self._home_position = mc.cameraView(camera=cam)

    @property
    def all_bookmarks(self):
        '''
        get list of all bookmarks associated with the current camera
        '''
        return mc.listConnections('%s.bookmarks' % self.cam_shape, s=True) or []

    @property
    def bookmarks(self):
        '''
        get list of bookmarks
        '''
        return self._bookmarks

    @bookmarks.setter
    def bookmarks(self, bmarks):
        '''
        process and collect all bookmarks that do not match the exclude patterns

        :type   bmarks: C{list}
        :param  bmarks: list of bookmarks to process
        '''
        new_bmarks = []
        for bmark in bmarks:
            if not re.match(self.exclude_prefix_pattern, bmark) \
                    and not re.match(self.exclude_postfix_pattern, bmark):
                new_bmarks.append(bmark)

        self._bookmarks = new_bmarks

    @property
    def current_bookmark(self):
        '''
        get current bookmark
        '''
        return self._cur_bookmark

    @current_bookmark.setter
    def current_bookmark(self, bmark):
        '''
        set specified bookmark as current

        :type   bmark: C{str}
        :param  bmark: bookmark to be current
        '''
        self._cur_bookmark = bmark

    @property
    def include_prefix_pattern(self):
        '''
        combine and compile pattern for locating bookmarks
            that match the list of specified prefixes
        '''
        return re.compile("^(%s)[_\w]*$" % "|".join(self._includes_prefix))

    @property
    def exclude_prefix_pattern(self):
        '''
        combine and compile pattern for locating bookmarks
            that match the list of specified prefixes to exclude
        '''
        if not self._excludes['prefix']:
            return self.empty_pattern

        return re.compile("^(%s)[_\w]+$" % "|".join(self._excludes['prefix']))

    @property
    def exclude_postfix_pattern(self):
        '''
        combine and compile pattern for locating bookmarks
            that match the list of specified postfixes to exclude
        '''
        if not self._excludes['postfix']:
            return self.empty_pattern

        return re.compile("^[\w_]+(%s)" % "|".join(self._excludes['postfix']))

    @property
    def empty_pattern(self):
        '''
        false pattern to use when an exclude list is empty
        '''
        return re.compile("^$")

    def use_exclude_prefixes(self, exprefixes):
        '''
        add user specified exclude prefixes to list

        :type   exprefixes: C{list}
        :param  exprefixes: list of prefixes to exclude bookmarks
        '''
        for prefix in exprefixes:
            self._excludes['prefix'].append(prefix)

    def use_exclude_postfixes(self, expostfixes):
        '''
        add user specified exclude postfixes to list

        :type   expostfixes: C{list}
        :param  expostfixes: list of postfixes to exclude bookmarks
        '''
        for postfix in expostfixes:
            self._excludes['postfix'].append(postfix)

    def remove_exclude_prefix(self):
        '''
        make sure any default include prefixes are not within
            the specified exclude list
        '''
        new_exclude = []
        for prefix in self._excludes['prefix']:
            if not re.match(self.include_prefix_pattern, prefix):
                new_exclude.append(prefix)

        self._excludes['prefix'] = new_exclude

    def _get_original_attrs(self):
        '''
        collect original values of camera attributes
        '''
        self._orig_prescale = mc.getAttr('%s.preScale' % self.cam_shape)
        self._orig_near_clip_plane = mc.getAttr(
                                            '%s.nearClipPlane' % self.cam_shape)
        self._orig_far_clip_plane = mc.getAttr(
                                            '%s.farClipPlane' % self.cam_shape)

    def prep_camera(self, prescale=1.0, nearclip=0.1, farclip=100000):
        '''
        prep camera attributes for screen board grab
        '''
        mc.setAttr('%s.preScale' % self.cam_shape, prescale)
        mc.setAttr('%s.nearClipPlane' % self.cam_shape, nearclip)
        mc.setAttr('%s.farClipPlane' % self.cam_shape, farclip)

    def reset_original(self):
        '''
        reset camera attributes to original values
        '''
        mc.setAttr('%s.preScale' % self.cam_shape, self._orig_prescale)
        mc.setAttr('%s.nearClipPlane' % self.cam_shape,
                                        self._orig_near_clip_plane)
        mc.setAttr('%s.farClipPlane' % self.cam_shape,
                                        self._orig_far_clip_plane)

        # return camera to original start position
        self.current_bookmark = self.home_position
        self.set_to_bookmark()

    def set_to_bookmark(self, bmark=None):
        '''
        set camera to specified bookmark position otherwise
            set position to current bookmark if available

        :type   bmark: C{str}
        :param  bmark: bookmark for camera position
        '''
        if bmark and bmark in self.bookmarks:
            mc.cameraView(bmark, edit=True, camera=self.camera, setCamera=True)
            self.current_bookmark = bmark
        elif self.current_bookmark:
            mc.cameraView(self.current_bookmark, edit=True,
                          camera=self.camera, setCamera=True)


class BoardView(object):
    '''
    deals with processing and setting up model views, etc. for screen grab
    '''
    def __init__(self, camera, isolate_objs=False):
        '''
        initialize instance variables

        :type   camera: C{str}
        :param  camera: camera that model view / editor will be connected
        :type   isolate_objs: C{bool}
        :param  isolate_objs: should selected objects be isolated from
                            rest of scene.  Best if used for single assets, etc.
        '''
        self._current_panel = None
        self.camera = camera
        self._isolate_objs = isolate_objs
        self.display_defaults = None

        self._get_current_panel()
        self._get_display_defaults()

    def _get_current_panel(self):
        '''
        determine current model panel for use
        '''
        cur_panel = 'modelPanel4'
        if not mc.modelEditor(cur_panel, exists=True):
            cur_panel = mc.getPanel(withFocus=True)

        self._current_panel = cur_panel

    def _get_display_defaults(self):
        '''
        collect current panel display details so that it can
            be reset back after processing
        '''
        self.display_defaults = {
                'appearance': mc.modelEditor(self._current_panel,
                                            query=True, displayAppearance=True),
                'textures': mc.modelEditor(self._current_panel,
                                            query=True, displayTextures=True),
                'lights': mc.modelEditor(self._current_panel,
                                            query=True, displayLights=True)
        }

    def prep_view(self):
        '''
        prep current view panel with required settings for screen grab
        '''
        mel.eval('lookThroughModelPanel %s %s' %
                                            (self.camera, self._current_panel))
        if self._isolate_objs:
            mel.eval('enableIsolateSelect %s %s;' %
                                    (self._current_panel, self._isolate_objs))
            mc.isolateSelect(self._current_panel, state=self._isolate_objs)
            mc.viewFit()

        mc.select(clear=True)

        # attempt to use Viewport 2.0 for better image
        try:
            mel.eval('ActivateViewport20;')
        except Exception, e:
            raise 'Issue activating Viewport 2.0. %s' % e

        mc.modelEditor(self._current_panel, edit=True,
                        displayAppearance="smoothShaded",
                        displayTextures=True,
                        displayLights='all')

    def reset_view(self):
        '''
        return current view panel to original settings
        '''
        mc.isolateSelect(self._current_panel, state=False)
        mel.eval('enableIsolateSelect %s %s;' % (self._current_panel, False))
        mc.modelEditor(self._current_panel, edit=True,
                        displayAppearance=self.display_defaults['appearance'],
                        displayTextures=self.display_defaults['textures'],
                        displayLights=self.display_defaults['lights'])


class BoardImage(object):
    '''
    deals with the processing of a image name for a screen grab
    '''
    def __init__(self, node='', asset_cat=None):
        '''
        initialize instance variables

        :type   node: C{str}
        :param  node: master scene node object, for help with naming
        :type   asset_category: C{str}
        :param  asset_category: category for use with determining asset / image
                        library for use.
        '''
        self._node_name = node
        self._node = None
        self.asset_category = asset_cat
        self._asset_library = ddConstants.ASSET_DIRECTORIES[asset_cat]
        self._image_library = ddConstants.IMAGE_DIRECTORIES[asset_cat]
        self._rel_path = None
        self._img_dir = None
        self._img_prefix = None
        self._img_extension = 'jpg'
        self._img_quality = None
        self._img_width = None
        self._img_height = None

    @property
    def node(self):
        '''
        get the current node stripped to just base name
        '''
        return self._node_name.rpartition('|')[-1]

    @property
    def pub_dir(self):
        '''
        get the full publish directory path by combining the
            library and rel paths
        '''
        return os.path.join(self._asset_library, self.rel_path)

    @property
    def rel_path(self):
        '''
        get the current rel path
        '''
        return self._rel_path

    @rel_path.setter
    def rel_path(self, rpath):
        '''
        set to the specified relpath

        :type   rpath: C[str}
        :param  rpath: discovered rel path name to set to
        '''
        self._rel_path = rpath

    @property
    def img_prefix(self):
        '''
        get the current image prefix
        '''
        return self._img_prefix

    @img_prefix.setter
    def img_prefix(self, iprefix):
        '''
        get current image prefix
        '''
        self._img_prefix = iprefix

    @property
    def img_quality(self):
        '''
        get current image quality
        '''
        return self._img_quality

    @img_quality.setter
    def img_quality(self, quality):
        '''
        set image quality to specified value

        :type   quality: C{int}
        :param  quality: image quality to be used
        '''
        self._img_quality = quality

    @property
    def img_width(self):
        '''
        get current image width
        '''
        return self._img_width

    @img_width.setter
    def img_width(self, width):
        '''
        set current image width to specified value

        :type   width: C{float}
        :param  width: image width to be used
        '''
        self._img_width = width

    @property
    def img_height(self):
        '''
        get current image height
        '''
        return self._img_height

    @img_height.setter
    def img_height(self, height):
        '''
        set current image height to specified value

        :type   height: C{float}
        :param  height: image height to be used
        '''
        self._img_height = height

    @property
    def width_height(self):
        '''
        get tuple/list with current width and height values
        '''
        return (self.img_width, self.img_height)

    def use_panel(self):
        '''
        utilize current panel resolution for screen board;
            setting height and width to 0 means panel size to playblast
        '''
        self.img_height = 0
        self.img_width = 0

    def determine_relative_path(self):
        '''
        determine the relative path value for scene, ie. the remaining path
            that will follow the library path.  Child classes may have
            different definitions for processing
        '''
        pass

    def verify_path_dirs_exist(self, pub_path, extra_dirs=None):
        '''
        verify that the full path exists on disk

        :type   pub_path: C{str}
        :param  pub_path: initial starting publish path to extend
        :type   extra_dirs: C{list}
        :param  extra_dirs: *OPTIONAL* a set of extra directories to
                        extend main path that should also exist
        '''
        try:
            # collect path elements for verification
            pub_dirs = self.rel_path.split(os.sep)
            # also make sure any extra required directories exist
            if extra_dirs:
                pub_dirs += extra_dirs

            # verify if publish directories exist, if not create
            for pdir in pub_dirs:
                pub_path = os.path.join(pub_path, pdir)
                if not os.path.exists(pub_path):
                    print 'directory %s, does not exist. Creating...' % pub_path
                    os.mkdir(pub_path)
        except Exception, e:
            # mc.confirmDialog(
            #         title='Path Error',
            #         message='Issue creating/validating publish path. %s' % e,
            #         button=['OK'],
            #         defaultButton='OK')
            raise e


class LayoutBoardImage(BoardImage):
    '''
    deal with processing of the image naming for Layout / Set piece
    '''
    def __init__(self, node='', asset_category='environments', use_path=None):
        '''
        initialize instance variables

        :type   node: C{str}
        :param  node: master scene node object, for help with naming
        :type   asset_category: C{str}
        :param  asset_category: category for use with determining asset
                        library for use. Primarily for parent class use, this
                        class primarily uses the Layout Directory specified in
                        ddConstants
        :type   use_path: C{str} or None
        :param  use_path: use specified path instead of attempting
                        to determine from file name or node name
        '''
        super(LayoutBoardImage, self).__init__(node, asset_category)
        self._asset_library = ddConstants.LAYOUT_DIR
        self._use_path = use_path
        self._scene = None
        self._version = 1
        self._img_file = None
        self.img_quality = 80
        self.img_height = 1080
        self.img_width = 1920

        self.determine_relative_path()

    @property
    def scene(self):
        '''
        get scene name
        '''
        return self._scene

    @scene.setter
    def scene(self, scene_name):
        '''
        set instance scene name

        :type   scene_name: C{str}
        :param  scene_name: found scene name to be set
        '''
        self._scene = scene_name

    @property
    def version(self):
        '''
        get version number
        '''
        return self._version

    @version.setter
    def version(self, version_str):
        '''
        set int version value

        :type   version_str: C{str}
        :param  version_str: found version string to be set as an int
        '''
        self._version = int(version_str)

    @property
    def img_file(self):
        '''
        get the full image file name
        '''
        return self._img_file

    @img_file.setter
    def img_file(self, iname):
        '''
        set the full image file name, includes image prefix,
            unique name (typically name of bookmark), version and file extension
        :type   iname: C{str}
        :param  iname: name string to be applied to full image naming
        '''
        self._img_file = "%s_%s_v%03d.%s" % (self.img_prefix, iname,
                                             self.version, self._img_extension)

    @property
    def full_pub_path(self):
        '''
        get a full publish path that includes all directories and image file
        '''
        return os.path.join(self.pub_dir, self.img_file)

    def determine_relative_path(self):
        '''
        determine the relative path value for scene, ie. the remaining path
        that will follow the library path
        '''
        # collect naming details
        self._determine_scene_version()
        # images will be prefixed with only the scene number, dropping the set
        self.img_prefix = self.scene.rpartition('_')[0]

        # process path passed by user
        if self._use_path:
            # replace any found bad path separators in user provided path
            self.rel_path = self._use_path.replace("\\", "/")
            # reset asset library as it will not be used
            self._asset_library = ''
            self.verify_path_dirs_exist('')
            return

        # rel path is normally expected to include published directory
        self.rel_path = os.path.join(self.scene, "published")
        self.verify_path_dirs_exist(self._asset_library)

    def _determine_scene_version(self):
        '''
        check the selected node name and the open scene file name to determine
        the actual scene number / name and as well as the current version
        '''
        # prep regex patterns
        scene_patt = re.compile("[0-9]{4}_[A-Z]{3}_[a-z]+")
        version_patt = re.compile("_v([0-9]{2,4})_*")

        # get scene file
        scene_file = mc.file(query=True, sceneName=True)

        # parse the search objects to locate values
        found_all = 0
        for scene_obj in [self.node, scene_file]:
            if scene_patt.search(scene_obj) and not self.scene:
                self.scene = scene_patt.search(scene_obj).group()
                found_all += 1
            if version_patt.search(scene_obj):
                self.version = version_patt.search(scene_obj).groups()[0]
                found_all += 1
            if found_all >= 2:
                break

        if not self.scene:
            raise Exception("Scene could not be determined. " + \
                  " Make sure scene is either in node name or file path.")


class CharacterBoardImage(BoardImage):
    def __init__(self, node=None, asset_category='characters'):
        super(CharacterBoardImage, self).__init__(node, asset_category)
        self._charType = {"hero": "hero", "bg": "background", "sec": "secondary"}
        self._chesspieceTypes = ["CPF", "CPO", "CPD", "CPS"]
        self.img_height = 768
        self.img_width = 1024

        raise Exception("Class not yet implemented.  Needs further work.")


class EnvironmentBoardImage(BoardImage):
    def __init__(self, node=None, asset_category='environments'):
        super(EnvironmentBoardImage, self).__init__(node, asset_category)

        raise Exception("Class not yet implemented.  Needs further work.")


def ddScreenBoardGrab(image_path, quality=40, width_height=(0,0)):
    '''
    generate screen grab for specified path / board

    :type   image_path: C{str}
    :param  image_path: path to save screen board
    :type   quality: C{int}
    :param  quality: expected image quality
    :type   width_height: C{tuple}
    :param  width_height: expected width and height values for resulting image;
                            values of 0 means current panel size
    '''
    mc.playblast(
            frame=1, format="image", completeFilename=image_path,
            clearCache=True, viewer=False, showOrnaments=False,
            compression="jpg", quality=quality, percent=100,
            widthHeight=width_height)


def do_layout_boards(use_path=None, exclude_prefixes=[],
                     exclude_postfixes=[], use_panel=False):
    '''
    process layout image boards for selected camera with specified options

    :type   use_path: C{str}
    :param  use_path: user specified path to save image boards to
    :type   exclude_prefixes: C{list}
    :param  exclude_prefixes: list of prefixes to exclude bookmarks
    :type   exclude_postfixes: C{list}
    :param  exclude_postfixes: list of postfixes to exclude bookmarks
    :type   use_panel: C{bool}
    :param  use_panel: if True, use the panels current size for resolution
    '''
    sel = mc.ls(sl=True)
    if len(sel) < 1:
        raise Exception("Incorrect selection. Need to select at "
                        + "least one camera. Preferably a camera and "
                        + "layout set group node, ie. env_0080_PCR...GRP, "
                        + "as added help for proper naming / saving.")

    sel_cam = sel[0]
    sel_node = ''
    if len(sel) > 1:
        sel_node = sel[1]

    # prepping camera details
    cam = BoardCamera()
    cam.camera = sel_cam
    cam.use_exclude_prefixes(exclude_prefixes)
    cam.use_exclude_postfixes(exclude_postfixes)
    cam.remove_exclude_prefix()
    cam.bookmarks = cam.all_bookmarks

    # prepping image details
    set_image = LayoutBoardImage(sel_node, use_path=use_path)
    if use_panel:
        set_image.use_panel()

    # prepping panel view setup
    bview = BoardView(cam.camera)
    bview.prep_view()

    print 'about to process %02d bookmarks for cam %s'\
                                            % (len(cam.bookmarks), cam.camera)
    for bmark in cam.bookmarks:
        print 'processing %s' % bmark
        cam.set_to_bookmark(bmark)
        set_image.img_file = bmark
        print 'grabbing %s' % set_image.full_pub_path
        ddScreenBoardGrab(set_image.full_pub_path,
                            set_image.img_quality,
                            set_image.width_height)

    print 'completed processing bookmarks... resetting environment...'
    bview.reset_view()
    cam.reset_original()

