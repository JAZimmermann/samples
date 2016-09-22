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
# $Date: 2014-11-12$
# $Revision: 1.0$
# $Author: johnz $
#

import codecs
import datetime
import os
import re
import warnings

from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

import maya.cmds as mc


def warning_user_friendly(message, category, filename, lineno,
                                                        file=None, line=None):
    '''
    provide a more user friendly warning, while also displaying basic debug info
    '''
    return '%s: %s  - %s:%s' % (category.__name__, message, filename, lineno)

warnings.formatwarning = warning_user_friendly


class LightsToUFileException(Exception):
    pass


class SceneNameException(Exception):
    pass


class LightsToU(object):
    '''
    Processing of Maya scene lights to XML for Unity creation
    '''
    ENCODING_FORMAT = 'utf-8'
    def __init__(self, set_type='MayaLightSet'):
        '''
        initialize instance variables

        :type   set_type: C{str}
        :param  set_type: collection type name for root level element
        '''
        self._set_type = set_type
        self._xml_root = Element(self._set_type)
        self._xml_path = None

    @property
    def xml_root(self):
        '''
        get current xml root collection
        '''
        return self._xml_root

    @property
    def xml_path(self):
        '''
        get intended xml file path
        '''
        return self._xml_path

    @xml_path.setter
    def xml_path(self, xml_file_path):
        '''
        attempt to set specified xml save path

        :type   xml_file_path: C{str}
        :param  xml_file_path: path to the intended xml file
        '''
        if not os.path.isdir(os.path.dirname(xml_file_path)):
            raise LightsToUFileException('Directory does not exist: %s.'
                                            % os.path.dirname(xml_file_path))
        if os.path.isfile(xml_file_path):
            raise LightsToUFileException('File already exists: %s.'
                                                                % xml_file_path)

        self._xml_path = xml_file_path

    def process_scene_details(self, scene_details):
        '''
        setup processing elements for scene details

        :type   scene_details: C{Scene} / C{dict}
        :param  scene_details: collection of scene related details,
                                ie. scene name, version, etc.
        '''
        if isinstance(scene_details, Scene):
            scene_details = scene_details.details

        self._process_elements(scene_details)

    def process_lights(self, light_set):
        '''
        setup processing elements for provided set of lights

        :type   light_set: C{list}
        :param  light_set: list of lights with detail dict
        '''
        lights_elem_tag = 'Lights'
        # determine if element tag already exists before creating new
        lights_elem = None
        lights_elem_exists = self.xml_root.find(lights_elem_tag)

        if lights_elem_exists is None:
            lights_elem = SubElement(self.xml_root, 'Lights')
        else:
            lights_elem = lights_elem_exists

        # iterate through and add new light element
        for lght in light_set:
            lght_elem = SubElement(lights_elem, 'Light')
            lght_details = lght
            if isinstance(lght, SceneLightNode):
                lght_details = lght.details

            self._process_elements(lght_details, lght_elem)

    def _process_elements(self, elements, root=None):
        '''
        iterate and connect sub element to specified root element

        :type   elements: C[dict}
        :param  elements: collection of details to add under
                            specified root branch
        :type   root: C{Element}
        :param  root: element considered to be the root branch
                        for details to be placed under
        '''
        # use default top level root branch if none specified
        if root is None:
            root = self.xml_root

        # trying to better organize elements with sorting
        sorted_elements = elements.keys()
        sorted_elements.sort()

        for elem in sorted_elements:
            sub_elem = SubElement(root, elem)
            if isinstance(elements[elem], dict):
                self._process_elements(elements[elem], sub_elem)
                continue

            sub_elem.text = elements[elem]

    def print_xml(self):
        '''
        print string version of the elements
        '''
        print tostring(self._xml_root)

    def print_pretty_xml(self):
        '''
        print xml elements in a more human readable format
        '''
        print self.prettify(self._xml_root)

    def write(self):
        '''
        write xml root data to file
        '''
        if not self.xml_path:
            warnings.warn("XML file path has not been provided. " \
                            + "Please set intended file path and try again.",
                            UserWarning)
            return

        with codecs.open(self.xml_path, 'w',
                        encoding=self.ENCODING_FORMAT) as xml_file:
            xml_file.write(self.prettify(self.xml_root))

    @classmethod
    def prettify(cls, elem):
        """
        Return a pretty-printed XML string for the Element.
            based on / from PYMOTW example

        :type   elem: C{Element}
        :param  elem: element for conversion and processing
        """
        rough_string = tostring(elem, cls.ENCODING_FORMAT)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding=cls.ENCODING_FORMAT)


class Scene(object):
    def __init__(self):
        '''
        initialize instance variables
        '''
        self._scene = ''
        self._scene_version = 0
        self._time = str(datetime.datetime.now())
        self.__scene_path = ''
        self.__scene_file = ''

        self._determine_scene_version()

    @property
    def details(self):
        '''
        get the main variable and value details as a formatted dictionary
        '''
        inst_vars = vars(self)
        vars_dict = {}

        for ikey in inst_vars.keys():
            if '__' in ikey:
                continue
            new_key = ikey.title().strip('_')
            vars_dict[new_key] = inst_vars[ikey]

        return vars_dict

    def _collect_scene_file(self):
        '''
        collect the current scene file and path
        '''
        scene_file = mc.file(query=True, sceneName=True)

        self.__scene_path, self.__scene_file = os.path.split(scene_file)

    def _determine_scene_version(self):
        '''
        check the selected node name and the open scene file name to determine
        the actual scene number / name and as well as the current version
        '''
        # prep regex patterns
        scene_patt = re.compile("[0-9]{4}_[A-Z]{3}_[a-z]+")
        version_patt = re.compile("_v([0-9]{2,4})_*")

        # get scene file
        # scene_file = mc.file(query=True, sceneName=True)
        self._collect_scene_file()

        # parse the search objects to locate values
        found_all = 0
        for scene_obj in [self.__scene_file]:
            if scene_patt.search(scene_obj) and not self._scene:
                self._scene = scene_patt.search(scene_obj).group()
                found_all += 1
            if version_patt.search(scene_obj):
                self._scene_version = version_patt.search(scene_obj).groups()[0]
                found_all += 1
            if found_all >= 2:
                break

        if not self._scene:
            raise SceneNameException("Scene could not be determined. " + \
                                " Make sure scene is either in file path.")


class SceneLights(object):
    '''
    Collection of Maya scene light nodes
    '''
    _UNSUPPORTED_LIGHTS = ['ambientLight', 'volumeLight']

    def __init__(self):
        '''
        initialize instance variables
        '''
        self._lights = []

        self._collect_light_nodes()

    @property
    def lights(self):
        '''
        get collection of lights
        '''
        return self._lights

    def _collect_light_nodes(self):
        '''
        attempt to collect lights and their details in scene
        '''
        found_lights = mc.ls(lights=True, long=True)
        if not found_lights:
            return

        for lght in found_lights:
            if mc.nodeType(lght) in self._UNSUPPORTED_LIGHTS:
                continue
            self._lights.append(SceneLightNode(lght))

        self._lights.sort(key=lambda x: x.name)


class SceneLightNode(object):
    '''
    Maya light node in scene
    '''
    def __init__(self, maya_light):
        '''
        initialize instance variables
        '''
        # gather basics across all light types and determine how to deal with
        #   specifics, whether related to type or even attributes
        if not mc.objectType(maya_light, isAType='light'):
            print '%s is not a light.' % maya_light
            return

        self.__shape = maya_light
        self.__use_shadows = mc.getAttr("%s.useDepthMapShadows" % self.__shape)
        self._name = ''
        self._path = ''
        self._position = {} # x,y,z
        self._rotation = {} # x,y,z
        self._scale = {} # x,y,z
        self._type = ''
        self._color = {} # r,g,b
        self._intensity = '0.0'
        self._shadows = 'No'

        self._get_light_details()

    @property
    def name(self):
        '''
        get light name
        '''
        return self._name

    @property
    def details(self):
        '''
        get the main variable and value details as a formatted dictionary
        '''
        inst_vars = vars(self)
        vars_dict = {}

        for ikey in inst_vars.keys():
            if '__' in ikey:
                continue
            new_key = ikey.title().strip('_')
            vars_dict[new_key] = inst_vars[ikey]

        return vars_dict

    def _get_light_details(self):
        '''
        gather details for light
        '''
        self._get_naming_details()
        self._get_base_light_details()
        self._get_light_specific_details()

        if self.__use_shadows:
            self._get_shadow_details()

    def _get_naming_details(self):
        '''
        determine base parent name and path of light
        '''
        # possibly rework at some point
        light_transform = mc.listRelatives(self.__shape,
                                            parent=True, fullPath=True)[0]

        self._name = light_transform.rpartition('|')[-1]
        self._path = str(light_transform.partition("|%s" % self._name)[0])

    def _get_base_light_details(self):
        '''
        gather general, non specific light details
        '''
        self._get_type()
        self._get_light_transformations()
        self._get_light_color()
        self._intensity = str(mc.getAttr("%s.intensity" % self.__shape))

    def _get_light_specific_details(self):
        '''
        determine which light type specific details to collect
        '''
        if self._type.startswith('Spot'):
            self._get_spot_light_details()
        elif self._type.startswith('Point'):
            pass
        elif self._type.startswith('Area'):
            pass
        elif self._type.startswith('Directional'):
            pass

    def _get_type(self):
        '''
        attempt to collect light type
        '''
        light_patt = re.compile('^([a-z]+)Light', re.IGNORECASE)
        light_type = mc.nodeType(self.__shape)

        if light_patt.search(light_type):
            self._type = str(light_patt.search(light_type).groups()[0]
                                                                ).capitalize()

    def _get_light_color(self):
        '''
        collect the color of the light
        '''
        self._color = {'r': str(mc.getAttr("%s.colorR" % self.__shape)),
                        'g': str(mc.getAttr("%s.colorG" % self.__shape)),
                        'b': str(mc.getAttr("%s.colorB" % self.__shape))}

    def _get_light_transformations(self):
        '''
        collect transformations of the light
        '''
        self._get_light_translation()
        self._get_light_rotation()
        self._get_light_scale()

    def _get_light_translation(self):
        '''
        collect translation values of the light
        '''
        trans = mc.xform(self.__full_path_name(), query=True, translation=True)
        self._position = {'x': str(trans[0]),
                        'y': str(trans[1]),
                        'z': str(trans[2])}

    def _get_light_rotation(self):
        '''
        collect rotation values of the light
        '''
        rotate = mc.xform(self.__full_path_name(), query=True, rotation=True)
        self._rotation = {'x': str(rotate[0]),
                        'y': str(rotate[1]),
                        'z': str(rotate[2])}

    def _get_light_scale(self):
        '''
        collect scale values of the light
        '''
        scale = mc.xform(self.__full_path_name(), query=True,
                                                    relative=True, scale=True)
        self._scale = {'x': str(scale[0]),
                        'y': str(scale[1]),
                        'z': str(scale[2])}

    def _get_shadow_details(self):
        '''
        collect shadow related details and type for the light
        :return:
        '''
        self._shadows = 'Soft'
        # self._shadow_strength = 0
        self._shadow_resolution = str(mc.getAttr("%s.dmapResolution"
                                                                % self.__shape))
        self._shadow_bias = str(mc.getAttr("%s.dmapBias" % self.__shape))

        if mc.getAttr("%s.dmapFilterSize" % self.__shape) <= 1:
            self._shadows = 'Hard'
    #
    #     if self._shadows.startswith('Soft'):
    #         self._get_soft_shadow_details()
    #
    # def _get_soft_shadow_details(self):
    #     self._shadow_softness = 0
    #     self._shadow_softness_fade = 0

    def _get_spot_light_details(self):
        '''
        collect details for spot light type
        '''
        self._spot_angle = str(mc.getAttr("%s.coneAngle" % self.__shape))
        self._get_light_range()

    def _get_light_range(self):
        self._range = '1'

    def __full_path_name(self):
        '''
        get full path to light's transform node
        '''
        return '|'.join([self._path, self._name])