"""Provide information about boxes and the associated resources

RESOURCES: Read from the resources.ini file

    * Used by raisin.restyler to fetch the resource

BOXES: Read from the boxes.ini file

    * Used by raisin.restyler to verify that a box id passed in a url exists

    * Used by raisin.restyler to get meta information about the boxes

RESOURCES_REGISTRY: A list of registered resources. For each resource contains

    * the name of the resource

    * the method to call for augmenting the box information in BOXES

    * the list of formats that the augmentation method needs

boxes: contains methods augmenting the information in BOXES.

    * Used for injection of Javascript

    * Changing the chart options

        * adapting the width and height of a chart

        * add log scales

    * Rendering the title and description of the boxes
"""

import os
from configobj import ConfigObj

RESOURCES = ConfigObj(os.path.join(os.path.dirname(__file__), "resources.ini"),
                      interpolation=False)
BOXES = ConfigObj(os.path.join(os.path.dirname(__file__), "boxes.ini"))

# All boxes are registered here
RESOURCES_REGISTRY = []

from raisin.box import boxes
