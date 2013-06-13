# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

"""Implementation of SMIL

We can find more informations here: http://www.w3.org/TR/SMIL20/
"""

# Import from lpod
from element import odf_create_element



def odf_create_anim_par(presentation_node_type=None, smil_begin=None):
    """This element is a container for SMIL Presentation Animations.

    Arguments:

        presentation_node_type -- default, on-click, with-previous,
                                  after-previous, timing-root, main-sequence
                                  and interactive-sequence

        smil_begin -- indefinite, 10s, [id].click, [id].begin
    """
    element = odf_create_element('anim:par')
    if presentation_node_type:
        element.set_attribute('presentation:node-type', presentation_node_type)
    if smil_begin:
        element.set_attribute('smil:begin', smil_begin)
    return element



def odf_create_anim_seq(presentation_node_type=None):
    """This element is a container for SMIL Presentation Animations. Animations
    inside this block are executed after the slide has executed its initial
    transition.

    Arguments:

        presentation_node_type -- default, on-click, with-previous,
                                  after-previous, timing-root, main-sequence
                                  and interactive-sequence
    """
    element = odf_create_element('anim:seq')
    if presentation_node_type:
        element.set_attribute('presentation:node-type', presentation_node_type)
    return element



def odf_create_anim_transitionFilter(smil_dur=None, smil_type=None,
                                     smil_subtype=None, smil_direction=None,
                                     smil_fadeColor=None, smil_mode=None):
    """
    Used to make a beautiful transition between two frames.

    Arguments:
      smil_dur -- XXX complete me
      smil_type and smil_subtype -- see http://www.w3.org/TR/SMIL20/smil-transitions.html#TransitionEffects-Appendix to get a list of all types/subtypes
      smil_direction -- forward, reverse
      smil_fadeColor -- forward, reverse
      smil_mode -- in, out
    """

    element = odf_create_element('anim:transitionFilter')

    if smil_dur:
        element.set_attribute('smil:dur', smil_dur)
    if smil_type:
        element.set_attribute('smil:type', smil_type)
    if smil_subtype:
        element.set_attribute('smil:subtype', smil_subtype)
    if smil_direction:
        element.set_attribute('smil:direction', smil_direction)
    if smil_fadeColor:
        element.set_attribute('smil:fadeColor', smil_fadeColor)
    if smil_mode:
        element.set_attribute('smil:mode', smil_mode)
    return element

