## -*- coding: utf-8 -*-
##
## Copyright 2017 Mario Frasca <mario@anche.no>.
##
## This file is part of ghini.desktop.
##
## ghini.desktop is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ghini.desktop is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ghini.desktop. If not, see <http://www.gnu.org/licenses/>.
##
## report/mako/
##
## DOMAIN plant
##
## OPTION single_page: (type: bool, default: 'True', tooltip: 'use false for engraver, true for printer.\ndon\'t exceed the 72 elements on single page.')
## OPTION colour: (type: string, default: '#000000', tooltip: 'use blue for engraver, black for printer.')
## OPTION extra_text: (type: string, default: '', tooltip: 'trailing text to accession code.')
## OPTION accession_format: (type: string, default: '', tooltip: 'ignore selection and print a range.')
## OPTION accession_first: (type: integer, default: '', tooltip: 'start of range.')
## OPTION accession_last: (type: integer, default: '', tooltip: 'end of range.')
##
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="744" height="1052" id="svg2">
<%
from bauble.plugins.report import add_text, font, add_code39, add_qr

page = 1
xpos = ypos = 0

if options.get('accession_format'):
    format = options['accession_format']
    start = format.rstrip('#')
    if start != format:
        digits = len(format) - len(start)
        format = start + '%%0%dd' % digits
    enumeration = enumerate([format % i for i in range(int(options['accession_first']), int(options['accession_last']) + 1)])
else:
    enumeration = [(i, p.accession.code + (p.code != '1' and '.' + p.code or ''), p.accession) for (i, p) in enumerate(values)]

%>\
  <defs id="defs3470">
    <path id="s2-u200b" d="" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0020" d="" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0021" d="m -7,-2 m 10.5844,-19.405662 0,14 1,0 m -1,-14 1,0 0,14 m -1,4 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0022" d="m -7,-2 m 10.5844,-19.405662 -1,1 0,6 m 1,-6 -1,6 m 1,-7 1,1 -2,6 m 10,-7 -1,1 0,6 m 1,-6 -1,6 m 1,-7 1,1 -2,6" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0023" d="m -7,-2 m 16.5844,-23.405662 -7,32 m 13,-32 -7,32 m -6,-19 14,0 m -15,6 14,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0024" d="m -7,-2 m 14.5844,-23.405662 0,29 1,0 m -1,-29 1,0 0,29 m 4,-22 2,0 -2,-2 -3,-1 -3,0 -3,1 -2,2 0,2 1,2 1,1 8,4 1,1 1,2 0,2 -1,2 -3,1 -3,0 -2,-1 -1,-1 m 9,-15 -1,-1 -2,-1 -3,0 -3,1 -1,1 0,2 1,2 8,4 2,2 1,2 0,2 -1,2 -1,1 -3,1 -3,0 -3,-1 -2,-2 2,0 m 10,0 -3,2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0025" d="m -7,-2 m 26.5844,-19.405662 -18,21 m 5,-21 2,2 0,2 -1,2 -2,1 -2,0 -2,-2 0,-2 1,-2 2,-1 2,0 2,1 3,1 3,0 3,-1 2,-1 m -4,14 -2,1 -1,2 0,2 2,2 2,0 2,-1 1,-2 0,-2 -2,-2 -2,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0026" d="m -7,-2 m 26.5844,-11.405662 -1,1 1,1 1,-1 0,-1 -1,-1 -1,0 -1,1 -1,2 -2,5 -2,3 -2,2 -2,1 -3,0 -3,-1 -1,-2 0,-3 1,-2 6,-4 2,-2 1,-2 0,-2 -1,-2 -2,-1 -2,1 -1,2 0,2 1,3 2,3 5,7 2,2 3,1 1,0 1,-1 0,-1 m -15,2 -2,-1 -1,-2 0,-3 1,-2 2,-2 m 0,-6 1,2 8,11 2,2 2,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0027" d="m -7,-2 m 10.5844,-19.405662 -1,1 0,6 m 1,-6 -1,6 m 1,-7 1,1 -2,6" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0028" d="m -7,-2 m 16.5844,-23.405662 -2,2 -2,3 -2,4 -1,5 0,4 1,5 2,4 2,3 2,2 m -2,-30 -2,4 -1,3 -1,5 0,4 1,5 1,3 2,4" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0029" d="m -7,-2 m 8.5844,-23.405662 2,2 2,3 2,4 1,5 0,4 -1,5 -2,4 -2,3 -2,2 m 2,-30 2,4 1,3 1,5 0,4 -1,5 -1,3 -2,4" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002a" d="m -7,-2 m 13.5844,-19.405662 -1,1 2,10 -1,1 m 0,-12 0,12 m 0,-12 1,1 -2,10 1,1 m -5,-9 1,0 8,6 1,0 m -10,-6 10,6 m -10,-6 0,1 10,4 0,1 m 0,-6 -1,0 -8,6 -1,0 m 10,-6 -10,6 m 10,-6 0,1 -10,4 0,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002b" d="m -7,-2 m 17.5844,-16.405662 0,17 1,0 m -1,-17 1,0 0,17 m -9,-9 17,0 0,1 m -17,-1 0,1 17,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002c" d="m -7,-2 m 12.58441,0.594338 -1,1 -1,0 -1,-1 0,-1 1,-1 1,0 1,1 0,3 -1,2 -2,1 m 1,-6 0,1 1,0 0,-1 -1,0 m 1,2 1,1 m 0,-2 -1,4" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002d" d="m -7,-2 m 9.58441,-7.405662 18,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002e" d="m -7,-2 m 10.584408,-1.405662 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u002f" d="m -7,-2 m 25.58441,-23.405662 -18,32 1,0 m 17,-32 1,0 -18,32" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0030" d="m -7,-2 m 14.58441,-19.405662 -3,1 -2,3 -1,5 0,3 1,5 2,3 3,1 2,0 3,-1 2,-3 1,-5 0,-3 -1,-5 -2,-3 -3,-1 -2,0 m -2,1 -2,3 -1,5 0,3 1,5 2,3 m -1,-1 3,1 2,0 3,-1 m -1,1 2,-3 1,-5 0,-3 -1,-5 -2,-3 m 1,1 -3,-1 -2,0 -3,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0031" d="m -7,-2 m 11.5844,-15.405662 2,-1 3,-3 0,21 m -5,-17 0,1 2,-1 2,-2 0,19 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0032" d="m -7,-2 m 9.5844,-14.405662 0,-1 1,-2 1,-1 2,-1 4,0 2,1 1,1 1,2 0,2 -1,2 -2,3 -9,10 m 0,-16 1,0 0,-1 1,-2 2,-1 4,0 2,1 1,2 0,2 -1,2 -2,3 -9,10 m 1,-1 13,0 0,1 m -14,0 14,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0033" d="m -7,-2 m 10.5844,-19.405662 11,0 -7,9 m -4,-9 0,1 10,0 m 0,-1 -7,9 m 1,-1 2,0 3,1 2,2 1,3 0,1 -1,3 -2,2 -3,1 -3,0 -3,-1 -1,-1 -1,-2 1,0 m 4,-8 3,0 3,1 2,3 m -4,-4 3,2 1,3 0,1 -1,3 -3,2 m 4,-4 -2,3 -3,1 -3,0 -3,-1 -1,-2 m 3,3 -3,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0034" d="m -7,-2 m 18.5844,-16.405662 0,18 1,0 m 0,-21 0,21 m 0,-21 -11,16 15,0 m -5,-13 -9,13 m 0,-1 14,0 0,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0035" d="m -7,-2 m 10.5844,-19.405662 -1,9 m 2,-8 -1,7 m 0,-8 10,0 0,1 m -9,0 9,0 m -10,7 3,-1 3,0 3,1 2,2 1,3 0,2 -1,3 -2,2 -3,1 -3,0 -3,-1 -1,-1 -1,-2 1,0 m 0,-8 1,0 2,-1 4,0 3,1 2,3 m -4,-4 3,2 1,3 0,2 -1,3 -3,2 m 4,-4 -2,3 -3,1 -3,0 -3,-1 -1,-2 m 3,3 -3,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0036" d="m -7,-2 m 19.5844,-18.405662 1,2 1,0 -1,-2 -3,-1 -2,0 -3,1 -2,3 -1,5 0,5 1,4 2,2 3,1 1,0 3,-1 2,-2 1,-3 0,-1 -1,-3 -2,-2 -3,-1 -1,0 -3,1 -2,2 m 10,-9 -3,-1 -2,0 -3,1 m 1,-1 -2,3 -1,5 0,5 1,4 3,2 m -4,-4 2,3 3,1 1,0 3,-1 2,-3 m -4,4 3,-2 1,-3 0,-1 -1,-3 -3,-2 m 4,4 -2,-3 -3,-1 -1,0 -3,1 -2,3 m 4,-4 -3,2 -1,3" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0037" d="m -7,-2 m 8.5844,-19.405662 14,0 -10,21 m -4,-21 0,1 13,0 m 0,-1 -10,21 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0038" d="m -7,-2 m 13.5844,-19.405662 -3,1 -1,2 0,2 1,2 1,1 2,1 4,1 2,1 1,1 1,2 0,3 -1,2 -3,1 -4,0 -3,-1 -1,-2 0,-3 1,-2 1,-1 2,-1 4,-1 2,-1 1,-1 1,-2 0,-2 -1,-2 -3,-1 -4,0 m -2,1 -1,2 0,2 1,2 2,1 4,1 2,1 2,2 1,2 0,3 -1,2 -1,1 -3,1 -4,0 -3,-1 -1,-1 -1,-2 0,-3 1,-2 2,-2 2,-1 4,-1 2,-1 1,-2 0,-2 -1,-2 m 1,1 -3,-1 -4,0 -3,1 m -1,16 3,2 m 6,0 3,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0039" d="m -7,-2 m 20.5844,-9.405662 -2,2 -3,1 -1,0 -3,-1 -2,-2 -1,-3 0,-1 1,-3 2,-2 3,-1 1,0 3,1 2,2 1,4 0,5 -1,5 -2,3 -3,1 -2,0 -3,-1 -1,-2 1,0 1,2 m 9,-13 -1,3 -3,2 m 4,-4 -2,3 -3,1 -1,0 -3,-1 -2,-3 m 4,4 -3,-2 -1,-3 0,-1 1,-3 3,-2 m -4,4 2,-3 3,-1 1,0 3,1 2,3 m -4,-4 3,2 1,4 0,5 -1,5 -2,3 m 1,-1 -3,1 -2,0 -3,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003a" d="m -7,-2 m 10.5844,-12.405662 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0 m 0,10 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003b" d="m -7,-2 m 10.5844,-12.405662 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0 m 2,12 -1,1 -1,0 -1,-1 0,-1 1,-1 1,0 1,1 0,3 -1,2 -2,1 m 1,-6 0,1 1,0 0,-1 -1,0 m 1,2 1,1 m 0,-2 -1,4" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003c" d="m -7,-2 m 25.5844,-16.405662 -16,9 16,9" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003d" d="m -7,-2 m 9.5844,-12.405662 17,0 0,1 m -17,-1 0,1 17,0 m -17,7 17,0 0,1 m -17,-1 0,1 17,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003e" d="m -7,-2 m 9.5844,-16.405662 16,9 -16,9" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u003f" d="m -7,-2 m 8.5844,-14.405662 0,-1 1,-2 1,-1 3,-1 3,0 3,1 1,1 1,2 0,2 -1,2 -1,1 -2,1 -3,1 m -6,-6 1,0 0,-1 1,-2 3,-1 3,0 3,1 1,2 0,2 -1,2 -2,1 -3,1 m -5,-7 3,-2 m 5,0 3,2 m 0,4 -4,3 m -2,0 0,4 1,0 0,-4 m -1,8 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0040" d="m -7,-2 m 18.690955,-13.000616 -1,-2 -2,-1 -3,0 -2,1 -1.0000003,1 -1,3 0,3 1,2 2.0000003,1 3,0 2,-1 1,-2 m -5,-8 -2,2 -1.0000003,3 0,3 1.0000003,2 1,1 m 7,-11 -1,8 0,2 2,1 2,0 2,-2 1,-3 0,-2 -1,-3 -1,-2 -2,-2 -2,-1 -3,-1 -3,0 -3.0000003,1 -2,1 -2,2 -1,2 -1,3 0,3 1,3 1,2 2,2 2,1 3.0000003,1 3,0 3,-1 2,-1 1,-1 m -2,-13 -1,8 0,2 1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0041" d="m -7,-2 m 15.5844,-19.405663 -8,21 m 8,-18 -7,18 -1,0 m 8,-18 7,18 1,0 m -8,-21 8,21 m -13,-6 10,0 m -11,1 12,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0042" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,19 m -1,-20 8,0 3,1 1,1 1,2 0,3 -1,2 -1,1 -3,1 m -7,-10 7,0 3,1 1,2 0,3 -1,2 -3,1 m -7,0 7,0 3,1 1,1 1,2 0,3 -1,2 -1,1 -3,1 -8,0 m 1,-10 7,0 3,1 1,2 0,3 -1,2 -3,1 -7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0043" d="m -7,-2 m 23.5844,-14.405663 -1,-2 -2,-2 -2,-1 -4,0 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4,0 2,-1 2,-2 1,-2 m 0,-11 -1,0 -1,-2 -1,-1 -2,-1 -4,0 -2,1 -2,3 -1,3 0,5 1,3 2,3 2,1 4,0 2,-1 1,-1 1,-2 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0044" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,19 m -1,-20 7,0 3,1 2,2 1,2 1,3 0,5 -1,3 -1,2 -2,2 -3,1 -7,0 m 1,-20 6,0 3,1 1,1 1,2 1,3 0,5 -1,3 -1,2 -1,1 -3,1 -6,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0045" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,19 m -1,-20 12,0 m -11,1 11,0 0,-1 m -11,10 6,0 0,1 m -6,0 6,0 m -6,9 11,0 0,1 m -12,0 12,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0046" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,20 -1,0 m 0,-21 12,0 m -11,1 11,0 0,-1 m -11,10 6,0 0,1 m -6,0 6,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0047" d="m -7,-2 m 23.5844,-14.405663 -1,-2 -2,-2 -2,-1 -4,0 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4,0 2,-1 2,-2 1,-2 0,-4 -5,0 m 5,-7 -1,0 -1,-2 -1,-1 -2,-1 -4,0 -2,1 -1,1 -1,2 -1,3 0,5 1,3 1,2 1,1 2,1 4,0 2,-1 1,-1 1,-2 0,-3 -4,0 0,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0048" d="m -7,-2 m 9.5844,-19.405663 0,21 m 0,-21 1,0 0,21 -1,0 m 14,-21 -1,0 0,21 1,0 m 0,-21 0,21 m -13,-11 12,0 m -12,1 12,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0049" d="m -7,-2 m 9.5844,-19.405663 0,21 1,0 m -1,-21 1,0 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004a" d="m -7,-2 m 17.5844,-19.405663 0,16 -1,3 -2,1 -2,0 -2,-1 -1,-3 -1,0 m 9,-16 1,0 0,16 -1,3 -1,1 -2,1 -2,0 -2,-1 -1,-1 -1,-3" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004b" d="m -7,-2 m 9.5844,-19.405663 0,21 1,0 m -1,-21 1,0 0,21 m 13,-21 -1,0 -12,12 m 13,-12 -13,13 m 3,-4 9,12 1,0 m -9,-12 9,12" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004c" d="m -7,-2 m 9.584405,-19.405663 0,21 m 0,-21 1,0 0,20 m 0,0 11,0 0,1 m -12,0 12,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004d" d="m -7,-2 m 9.584405,-19.405663 0,21 m 1,-16 0,16 -1,0 m 1,-16 7,16 m -8,-21 8,18 m 8,-18 -8,18 m 7,-13 -7,16 m 7,-16 0,16 1,0 m 0,-21 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004e" d="m -7,-2 m 9.584403,-19.405663 0,21 m 1,-18 0,18 -1,0 m 1,-18 13,18 m -14,-21 13,18 m 0,-18 0,18 m 0,-18 1,0 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u004f" d="m -7,-2 m 14.584405,-19.405663 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4,0 2,-1 2,-2 1,-2 1,-3 0,-5 -1,-3 -1,-2 -2,-2 -2,-1 -4,0 m 1,1 -3,1 -2,3 -1,3 0,5 1,3 2,3 3,1 2,0 3,-1 2,-3 1,-3 0,-5 -1,-3 -2,-3 -3,-1 -2,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0050" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,20 -1,0 m 0,-21 9,0 2,1 1,1 1,2 0,3 -1,2 -1,1 -2,1 -8,0 m 0,-10 8,0 2,1 1,2 0,3 -1,2 -2,1 -8,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0051" d="m -7,-2 m 14.5844,-19.405663 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4,0 2,-1 2,-2 1,-2 1,-3 0,-5 -1,-3 -1,-2 -2,-2 -2,-1 -4,0 m 1,1 -3,1 -2,3 -1,3 0,5 1,3 2,3 3,1 2,0 3,-1 2,-3 1,-3 0,-5 -1,-3 -2,-3 -3,-1 -2,0 m 2,17 5,5 1,0 m -6,-5 1,0 5,5" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0052" d="m -7,-2 m 9.5844,-19.405663 0,21 m 1,-20 0,20 -1,0 m 0,-21 8,0 3,1 1,1 1,2 0,3 -1,2 -1,1 -3,1 -7,0 m 0,-10 7,0 3,1 1,2 0,3 -1,2 -3,1 -7,0 m 5,1 6,10 1,0 m -6,-10 6,10" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0053" d="m -7,-2 m 22.5844,-16.405663 -2,-2 -3,-1 -4,0 -3,1 -2,2 0,2 1,2 1,1 2,1 5,2 2,1 1,1 1,2 0,3 -1,1 -3,1 -4,0 -2,-1 -1,-1 -2,0 m 14,-15 -2,0 -1,-1 -2,-1 -4,0 -3,1 -1,1 0,2 1,2 2,1 5,2 2,1 2,2 1,2 0,3 -2,2 -3,1 -4,0 -3,-1 -2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0054" d="m -7,-2 m 13.5844,-18.405663 0,20 m 1,-20 0,20 -1,0 m -6,-21 13,0 0,1 m -13,-1 0,1 13,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0055" d="m -7,-2 m 9.5844,-19.405663 0,15 1,3 2,2 3,1 2,0 3,-1 2,-2 1,-3 0,-15 m -14,0 1,0 0,15 1,3 1,1 3,1 2,0 3,-1 1,-1 1,-3 0,-15 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0056" d="m -7,-2 m 7.5844,-19.405663 8,21 m -8,-21 1,0 7,18 m 8,-18 -1,0 -7,18 m 8,-18 -8,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0057" d="m -7,-2 m 7.5844,-19.405663 6,21 m -6,-21 1,0 5,18 m 5,-18 -5,18 m 5,-15 -5,18 m 5,-18 5,18 m -5,-21 5,18 m 6,-18 -1,0 -5,18 m 6,-18 -6,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0058" d="m -7,-2 m 8.5844,-19.405663 13,21 1,0 m -14,-21 1,0 13,21 m 0,-21 -1,0 -13,21 m 14,-21 -13,21 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0059" d="m -7,-2 m 7.58439,-19.405663 7,10 0,11 1,0 m -8,-21 1,0 7,10 m 7,-10 -1,0 -7,10 m 8,-10 -7,10 0,11" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005a" d="m -7,-2 m 21.58439,-19.405663 -13,21 m 14,-21 -13,21 m -1,-21 14,0 m -14,0 0,1 13,0 m -12,19 13,0 0,1 m -14,0 14,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005b" d="m -7,-2 m 9.58439,-23.405663 0,32 m 1,-32 0,32 m -1,-32 7,0 m -7,32 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005c" d="m -7,-2 m 5.58439,-19.405663 14,24" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005d" d="m -7,-2 m 14.58439,-23.405663 0,32 m 1,-32 0,32 m -7,-32 7,0 m -7,32 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005e" d="m -7,-2 m 8.58439,-5.4056632 8,-5 8,5 m -16,0 8,-4 8,4" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u005f" d="m -7,-2 m 5.58439,8.5943368 20,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0060" d="m -7,-2 m 9.5844,-19.405662 5,6 m -5,-6 -1,1 6,5" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0061" d="m -7,-2 m 20.5844,-12.405662 0,14 1,0 m -1,-14 1,0 0,14 m -1,-11 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m 0,-8 -4,-2 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0062" d="m -7,-2 m 9.5844,-19.405662 0,21 1,0 m -1,-21 1,0 0,21 m 0,-11 2,-2 2,-1 3,0 2,1 2,2 1,3 0,2 -1,3 -2,2 -2,1 -3,0 -2,-1 -2,-2 m 0,-8 4,-2 3,0 2,1 1,1 1,3 0,2 -1,3 -1,1 -2,1 -3,0 -4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0063" d="m -7,-2 m 20.5844,-9.405662 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m 0,-8 -1,1 -1,-2 -2,-1 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 2,-1 1,-2 1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0064" d="m -7,-2 m 20.5844,-19.405662 0,21 1,0 m -1,-21 1,0 0,21 m -1,-11 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m 0,-8 -4,-2 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0065" d="m -7,-2 m 9.5844,-5.405662 11,0 0,-3 -1,-2 -1,-1 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m -11,-5 10,0 0,-2 -1,-2 -2,-1 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 2,-1 1,-2 1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0066" d="m -7,-2 m 16.5844,-19.405662 -2,0 -2,1 -1,3 0,17 1,0 m 4,-21 0,1 -2,0 -2,1 m 1,-1 -1,3 0,17 m -4,-14 7,0 0,1 m -7,-1 0,1 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0067" d="m -7,-2 m 21.5844,-12.405662 -1,0 0,15 -1,3 -1,1 -2,1 -2,0 -2,-1 -1,-1 -2,0 m 12,-18 0,15 -1,3 -2,2 -2,1 -3,0 -2,-1 -2,-2 m 11,-15 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m 0,-8 -4,-2 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0068" d="m -7,-2 m 9.5844,-19.405662 0,21 1,0 m -1,-21 1,0 0,21 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10 m -11,-10 3,-2 2,-1 2,0 2,1 1,2 0,10 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0069" d="m -7,-2 m 9.5844,-19.405662 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0 m 0,6 0,14 1,0 m -1,-14 1,0 0,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006a" d="m -7,-2 m 9.5844,-19.405662 -1,1 0,1 1,1 1,0 1,-1 0,-1 -1,-1 -1,0 m 0,1 0,1 1,0 0,-1 -1,0 m 0,6 0,21 1,0 m -1,-21 1,0 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006b" d="m -7,-2 m 9.5844,-19.405662 0,21 1,0 m -1,-21 1,0 0,21 m 11,-14 -1,0 -10,10 m 11,-10 -11,11 m 3,-4 6,7 2,0 m -7,-8 7,8" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006c" d="m -7,-2 m 9.58441,-19.405662 0,21 1,0 m -1,-21 1,0 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006d" d="m -7,-2 m 9.58441,-12.405662 0,14 1,0 m -1,-14 1,0 0,14 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10 m -11,-10 3,-2 2,-1 2,0 2,1 1,2 0,10 1,0 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10 m -11,-10 3,-2 2,-1 2,0 2,1 1,2 0,10 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006e" d="m -7,-2 m 9.58441,-12.405662 0,14 1,0 m -1,-14 1,0 0,14 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10 m -11,-10 3,-2 2,-1 2,0 2,1 1,2 0,10 1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u006f" d="m -7,-2 m 13.58441,-12.405662 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 1,-3 0,-2 -1,-3 -2,-2 -2,-1 -3,0 m 0,1 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 2,-1 1,-1 1,-3 0,-2 -1,-3 -1,-1 -2,-1 -3,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0070" d="m -7,-2 m 9.58441,-12.405662 0,21 1,0 m -1,-21 1,0 0,21 m 0,-18 2,-2 2,-1 3,0 2,1 2,2 1,3 0,2 -1,3 -2,2 -2,1 -3,0 -2,-1 -2,-2 m 0,-8 4,-2 3,0 2,1 1,1 1,3 0,2 -1,3 -1,1 -2,1 -3,0 -4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0071" d="m -7,-2 m 20.5844,-12.405662 0,21 1,0 m -1,-21 1,0 0,21 m -1,-18 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 m 0,-8 -4,-2 -3,0 -2,1 -1,1 -1,3 0,2 1,3 1,1 2,1 3,0 4,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0072" d="m -7,-2 m 9.5844,-12.405662 0,14 1,0 m -1,-14 1,0 0,14 m 0,-8 1,-3 2,-2 2,-1 3,0 m -8,6 1,-2 2,-2 2,-1 3,0 0,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0073" d="m -7,-2 m 19.5844,-9.405662 -1,-2 -3,-1 -3,0 -3,1 -1,2 1,2 2,1 5,2 2,1 m -1,-1 1,2 0,1 -1,2 m 1,-1 -3,1 -3,0 -3,-1 m 1,1 -1,-2 -1,0 m 11,-8 -1,0 -1,-2 m 1,1 -3,-1 -3,0 -3,1 m 1,-1 -1,2 1,2 m -1,-1 2,1 5,2 2,1 1,2 0,1 -1,2 -3,1 -3,0 -3,-1 -1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0074" d="m -7,-2 m 10.5844,-19.405662 0,21 1,0 m -1,-21 1,0 0,21 m -4,-14 7,0 0,1 m -7,-1 0,1 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0075" d="m -7,-2 m 9.5844,-12.405662 0,10 1,3 2,1 3,0 2,-1 3,-3 m -11,-10 1,0 0,10 1,2 2,1 2,0 2,-1 3,-2 m 0,-10 0,14 1,0 m -1,-14 1,0 0,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0076" d="m -7,-2 m 7.5844,-12.405662 6,14 m -6,-14 1,0 5,12 m 6,-12 -1,0 -5,12 m 6,-12 -6,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0077" d="m -7,-2 m 8.5844,-12.405662 5,14 m -5,-14 1,0 4,11 m 4,-11 -4,11 m 4,-8 -4,11 m 4,-11 4,11 m -4,-14 4,11 m 5,-11 -1,0 -4,11 m 5,-11 -5,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0078" d="m -7,-2 m 8.5844,-12.405662 11,14 1,0 m -12,-14 1,0 11,14 m 0,-14 -1,0 -11,14 m 12,-14 -11,14 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u0079" d="m -7,-2 m 7.5844,-12.405662 6,14 m -6,-14 1,0 5,12 m 6,-12 -1,0 -5,12 -4,9 m 10,-21 -6,14 -3,7 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u007a" d="m -7,-2 m 18.5844,-11.405662 -10,13 m 12,-14 -10,13 m -2,-13 12,0 m -12,0 0,1 10,0 m -8,12 10,0 0,1 m -12,0 12,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u007b" d="m -7,-2 m 15.5844,-23.405662 -7,16 7,16" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u007c" d="m -7,-2 m 9.5844,-23.405662 0,32" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u007d" d="m -7,-2 m 9.5844,-23.405662 7,16 -7,16" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u007e" d="m -7,-2 m 8.5844,-4.405662 0,-2 1,-3 2,-1 2,0 2,1 4,3 2,1 2,0 2,-1 1,-2 m -18,2 1,-2 2,-1 2,0 2,1 4,3 2,1 2,0 2,-1 1,-3 0,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s2-u200b" d="" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0020" d="" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0021" d="m 5.6909547,-21.000616 0,14 m 0,5 -1,1 1,1 1,-1 -1,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0022" d="m 4.6909547,-21.000616 0,7 m 8.0000003,-7 0,7" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0023" d="m 11.690955,-25.000616 -7.0000003,32 m 13.0000003,-32 -7,32 m -6.0000003,-19 14.0000003,0 m -15.0000003,6 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0024" d="m 8.6909547,-25.000616 0,29 m 4.0000003,-29 0,29 m 5,-22 -2,-2 -3,-1 -4.0000003,0 -3,1 -2,2 0,2 1,2 1,1 2,1 6.0000003,2 2,1 1,1 1,2 0,3 -2,2 -3,1 -4.0000003,0 -3,-1 -2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0025" d="m 21.690955,-21.000616 -18.0000003,21 m 5,-21 2.0000003,2 0,2 -1.0000003,2 -2,1 -2,0 -2,-2 0,-2 1,-2 2,-1 2,0 2.0000003,1 3,1 3,0 3,-1 2,-1 m -4,14 -2,1 -1,2 0,2 2,2 2,0 2,-1 1,-2 0,-2 -2,-2 -2,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0026" d="m 23.690955,-12.000616 0,-1 -1,-1 -1,0 -1,1 -1,2 -2,5 -2,3 -2,2 -2,1 -4.0000003,0 -2,-1 -1,-1 -1,-2 0,-2 1,-2 1,-1 7.0000003,-4 1,-1 1,-2 0,-2 -1,-2 -2,-1 -2.0000003,1 -1,2 0,2 1,3 2.0000003,3 5,7 2,2 2,1 2,0 1,-1 0,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0027" d="m 5.6909547,-19.000616 -1,-1 1,-1 1,1 0,2 -1,2 -1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0028" d="m 11.690955,-25.000616 -2.0000003,2 -2,3 -2,4 -1,5 0,4 1,5 2,4 2,3 2.0000003,2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0029" d="m 3.6909547,-25.000616 2,2 2,3 2,4 1.0000003,5 0,4 -1.0000003,5 -2,4 -2,3 -2,2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002a" d="m 8.6909547,-15.000616 0,12 m -5,-9 10.0000003,6 m 0,-6 -10.0000003,6" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002b" d="m 13.690955,-18.000616 0,18 m -9.0000003,-9 18.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002c" d="m 5.6909547,-4.000616 -1,1 -1,-1 1,-1 1,1 0,2 -2,2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002d" d="m 4.6909547,-9.000616 18.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002e" d="m 4.6909547,-5.000616 -1,1 1,1 1,-1 -1,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u002f" d="m 20.690955,-25.000616 -18.0000003,32" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0030" d="m 9.6909547,-21.000616 -3,1 -2,3 -1,5 0,3 1,5 2,3 3,1 2.0000003,0 3,-1 2,-3 1,-5 0,-3 -1,-5 -2,-3 -3,-1 -2.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0031" d="m 6.6909547,-17.000616 2,-1 3.0000003,-3 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0032" d="m 4.6909547,-16.000616 0,-1 1,-2 1,-1 2,-1 4.0000003,0 2,1 1,1 1,2 0,2 -1,2 -2,3 -10.0000003,10 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0033" d="m 5.6909547,-21.000616 11.0000003,0 -6,8 3,0 2,1 1,1 1,3 0,2 -1,3 -2,2 -3,1 -3.0000003,0 -3,-1 -1,-1 -1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0034" d="m 13.690955,-21.000616 -10.0000003,14 15.0000003,0 m -5,-14 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0035" d="m 15.690955,-21.000616 -10.0000003,0 -1,9 1,-1 3,-1 3.0000003,0 3,1 2,2 1,3 0,2 -1,3 -2,2 -3,1 -3.0000003,0 -3,-1 -1,-1 -1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0036" d="m 16.690955,-18.000616 -1,-2 -3,-1 -2,0 -3.0000003,1 -2,3 -1,5 0,5 1,4 2,2 3.0000003,1 1,0 3,-1 2,-2 1,-3 0,-1 -1,-3 -2,-2 -3,-1 -1,0 -3.0000003,1 -2,2 -1,3" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0037" d="m 17.690955,-21.000616 -10.0000003,21 m -4,-21 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0038" d="m 8.6909547,-21.000616 -3,1 -1,2 0,2 1,2 2,1 4.0000003,1 3,1 2,2 1,2 0,3 -1,2 -1,1 -3,1 -4.0000003,0 -3,-1 -1,-1 -1,-2 0,-3 1,-2 2,-2 3,-1 4.0000003,-1 2,-1 1,-2 0,-2 -1,-2 -3,-1 -4.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0039" d="m 16.690955,-14.000616 -1,3 -2,2 -3,1 -1.0000003,0 -3,-1 -2,-2 -1,-3 0,-1 1,-3 2,-2 3,-1 1.0000003,0 3,1 2,2 1,4 0,5 -1,5 -2,3 -3,1 -2.0000003,0 -3,-1 -1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003a" d="m 4.6909547,-12.000616 -1,1 1,1 1,-1 -1,-1 m 0,7 -1,1 1,1 1,-1 -1,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003b" d="m 4.6909547,-12.000616 -1,1 1,1 1,-1 -1,-1 m 1,8 -1,1 -1,-1 1,-1 1,1 0,2 -2,2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003c" d="m 20.690955,-18.000616 -16.0000003,9 16.0000003,9" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003d" d="m 4.6909547,-12.000616 18.0000003,0 m -18.0000003,6 18.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003e" d="m 4.6909547,-18.000616 16.0000003,9 -16.0000003,9" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u003f" d="m 3.6909547,-16.000616 0,-1 1,-2 1,-1 2,-1 4.0000003,0 2,1 1,1 1,2 0,2 -1,2 -1,1 -4.0000003,2 0,3 m 0,5 -1,1 1,1 1.0000003,-1 -1.0000003,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0040" d="m 18.690955,-13.000616 -1,-2 -2,-1 -3,0 -2,1 -1.0000003,1 -1,3 0,3 1,2 2.0000003,1 3,0 2,-1 1,-2 m -5,-8 -2,2 -1.0000003,3 0,3 1.0000003,2 1,1 m 7,-11 -1,8 0,2 2,1 2,0 2,-2 1,-3 0,-2 -1,-3 -1,-2 -2,-2 -2,-1 -3,-1 -3,0 -3.0000003,1 -2,1 -2,2 -1,2 -1,3 0,3 1,3 1,2 2,2 2,1 3.0000003,1 3,0 3,-1 2,-1 1,-1 m -2,-13 -1,8 0,2 1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0041" d="m 9.6909547,-21.000616 -8,21 m 8,-21 8.0000003,21 m -13.0000003,-7 10.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0042" d="m 4.6909547,-21.000616 0,21 m 0,-21 9.0000003,0 3,1 1,1 1,2 0,2 -1,2 -1,1 -3,1 m -9.0000003,0 9.0000003,0 3,1 1,1 1,2 0,3 -1,2 -1,1 -3,1 -9.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0043" d="m 18.690955,-16.000616 -1,-2 -2,-2 -2,-1 -4.0000003,0 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4.0000003,0 2,-1 2,-2 1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0044" d="m 4.6909547,-21.000616 0,21 m 0,-21 7.0000003,0 3,1 2,2 1,2 1,3 0,5 -1,3 -1,2 -2,2 -3,1 -7.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0045" d="m 4.6909547,-21.000616 0,21 m 0,-21 13.0000003,0 m -13.0000003,10 8.0000003,0 m -8.0000003,11 13.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0046" d="m 4.6909547,-21.000616 0,21 m 0,-21 13.0000003,0 m -13.0000003,10 8.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0047" d="m 18.690955,-16.000616 -1,-2 -2,-2 -2,-1 -4.0000003,0 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4.0000003,0 2,-1 2,-2 1,-2 0,-3 m -5,0 5,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0048" d="m 4.6909547,-21.000616 0,21 m 14.0000003,-21 0,21 m -14.0000003,-11 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0049" d="m 4.6909547,-21.000616 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004a" d="m 12.690955,-21.000616 0,16 -1,3 -1,1 -2.0000003,1 -2,0 -2,-1 -1,-1 -1,-3 0,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004b" d="m 4.6909547,-21.000616 0,21 m 14.0000003,-21 -14.0000003,14 m 5,-5 9.0000003,12" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004c" d="m 4.6909547,-21.000616 0,21 m 0,0 12.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004d" d="m 4.6909547,-21.000616 0,21 m 0,-21 8.0000003,21 m 8,-21 -8,21 m 8,-21 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004e" d="m 4.6909547,-21.000616 0,21 m 0,-21 14.0000003,21 m 0,-21 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u004f" d="m 9.6909547,-21.000616 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4.0000003,0 2,-1 2,-2 1,-2 1,-3 0,-5 -1,-3 -1,-2 -2,-2 -2,-1 -4.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0050" d="m 4.6909547,-21.000616 0,21 m 0,-21 9.0000003,0 3,1 1,1 1,2 0,3 -1,2 -1,1 -3,1 -9.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0051" d="m 9.6909547,-21.000616 -2,1 -2,2 -1,2 -1,3 0,5 1,3 1,2 2,2 2,1 4.0000003,0 2,-1 2,-2 1,-2 1,-3 0,-5 -1,-3 -1,-2 -2,-2 -2,-1 -4.0000003,0 m 3.0000003,17 6,6" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0052" d="m 4.6909547,-21.000616 0,21 m 0,-21 9.0000003,0 3,1 1,1 1,2 0,2 -1,2 -1,1 -3,1 -9.0000003,0 m 7.0000003,0 7,11" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0053" d="m 17.690955,-18.000616 -2,-2 -3,-1 -4.0000003,0 -3,1 -2,2 0,2 1,2 1,1 2,1 6.0000003,2 2,1 1,1 1,2 0,3 -2,2 -3,1 -4.0000003,0 -3,-1 -2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0054" d="m 8.6909547,-21.000616 0,21 m -7,-21 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0055" d="m 4.6909547,-21.000616 0,15 1,3 2,2 3.0000003,1 2,0 3,-1 2,-2 1,-3 0,-15" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0056" d="m 1.6909547,-21.000616 8,21 m 8.0000003,-21 -8.0000003,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0057" d="m 2.6909547,-21.000616 5,21 m 5.0000003,-21 -5.0000003,21 m 5.0000003,-21 5,21 m 5,-21 -5,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0058" d="m 3.6909547,-21.000616 14.0000003,21 m 0,-21 -14.0000003,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0059" d="m 1.6909547,-21.000616 8,10 0,11 m 8.0000003,-21 -8.0000003,10" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005a" d="m 17.690955,-21.000616 -14.0000003,21 m 0,-21 14.0000003,0 m -14.0000003,21 14.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005b" d="m 4.6909547,-25.000616 0,32 m 1,-32 0,32 m -1,-32 7.0000003,0 m -7.0000003,32 7.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005c" d="m 0.6909547,-21.000616 14.0000003,24" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005d" d="m 9.6909547,-25.000616 0,32 m 1.0000003,-32 0,32 m -7.0000003,-32 7.0000003,0 m -7.0000003,32 7.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005e" d="m 8.6909547,-23.000616 -8,14 m 8,-14 8.0000003,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u005f" d="m 0.6909547,6.999384 18.0000003,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0060" d="m 5.6909547,-16.000616 -2,2 0,2 1,1 1,-1 -1,-1 -1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0061" d="m 15.690955,-14.000616 0,14 m 0,-11 -2,-2 -2,-1 -3.0000003,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3.0000003,0 2,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0062" d="m 4.6909547,-21.000616 0,21 m 0,-11 2,-2 2,-1 3.0000003,0 2,1 2,2 1,3 0,2 -1,3 -2,2 -2,1 -3.0000003,0 -2,-1 -2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0063" d="m 15.690955,-11.000616 -2,-2 -2,-1 -3.0000003,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3.0000003,0 2,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0064" d="m 15.690955,-21.000616 0,21 m 0,-11 -2,-2 -2,-1 -3.0000003,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3.0000003,0 2,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0065" d="m 3.6909547,-8.000616 12.0000003,0 0,-2 -1,-2 -1,-1 -2,-1 -3.0000003,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3.0000003,0 2,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0066" d="m 10.69094,-21.000616 -2,0 -2,1 -1,3 0,17 m -3,-14 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0067" d="m 15.69094,-14.000616 0,16 -1,3 -1,1 -2,1 -3,0 -2,-1 m 9,-17 -2,-2 -2,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0068" d="m 4.69094,-21.000616 0,21 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0069" d="m 3.69094,-21.000616 1,1 1,-1 -1,-1 -1,1 m 1,7 0,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006a" d="m 3.69094,-21.000616 1,1 1,-1 -1,-1 -1,1 m 1,7 0,17 -1,3 -2,1 -2,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006b" d="m 4.69094,-21.000616 0,21 m 10,-14 -10,10 m 4,-4 7,8" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006c" d="m 4.690954,-21.000616 0,21" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006d" d="m 4.690954,-14.000616 0,14 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006e" d="m 4.690954,-14.000616 0,14 m 0,-10 3,-3 2,-1 3,0 2,1 1,3 0,10" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u006f" d="m 8.690954,-14.000616 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 2,-1 2,-2 1,-3 0,-2 -1,-3 -2,-2 -2,-1 -3,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0070" d="m 4.690954,-14.000616 0,21 m 0,-18 2,-2 2,-1 3,0 2,1 2,2 1,3 0,2 -1,3 -2,2 -2,1 -3,0 -2,-1 -2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0071" d="m 15.69095,-14.000616 0,21 m 0,-18 -2,-2 -1.999996,-1 -3,0 -2,1 -2,2 -1,3 0,2 1,3 2,2 2,1 3,0 1.999996,-1 2,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0072" d="m 4.69094,-14.000616 0,14 m 0,-8 1,-3 2,-2 2,-1 3,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0073" d="m 14.69094,-11.000616 -1,-2 -3,-1 -3,0 -3,1 -1,2 1,2 2,1 5,1 2,1 1,2 0,1 -1,2 -3,1 -3,0 -3,-1 -1,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0074" d="m 5.69094,-21.000616 0,17 1,3 2,1 2,0 m -8,-14 7,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0075" d="m 4.69094,-14.000616 0,10 1,3 2,1 3,0 2,-1 3,-3 m 0,-10 0,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0076" d="m 2.69094,-14.000616 6,14 m 6,-14 -6,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0077" d="m 3.69094,-14.000616 4,14 m 4,-14 -4,14 m 4,-14 4,14 m 4,-14 -4,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0078" d="m 3.69094,-14.000616 11,14 m 0,-14 -11,14" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u0079" d="m 2.69094,-14.000616 6,14 m 6,-14 -6,14 -2,4 -2,2 -2,1 -1,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007a" d="m 14.69094,-14.000616 -11,14 m 0,-14 11,0 m -11,14 11,0" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007b" d="m 9.69094,-25.000616 -2,1 -1,1 -1,2 0,2 1,2 1,1 1,2 0,2 -2,2 m 1,-14 -1,2 0,2 1,2 1,1 1,2 0,2 -1,2 -4,2 4,2 1,2 0,2 -1,2 -1,1 -1,2 0,2 1,2 m -1,-14 2,2 0,2 -1,2 -1,1 -1,2 0,2 1,2 1,1 2,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007c" d="m 4.69094,-25.000616 0,32" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007d" d="m 5.69094,-25.000616 2,1 1,1 1,2 0,2 -1,2 -1,1 -1,2 0,2 2,2 m -1,-14 1,2 0,2 -1,2 -1,1 -1,2 0,2 1,2 4,2 -4,2 -1,2 0,2 1,2 1,1 1,2 0,2 -1,2 m 1,-14 -2,2 0,2 1,2 1,1 1,2 0,2 -1,2 -1,1 -2,1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007e" d="m 3.69094,-6.000616 0,-2 1,-3 2,-1 2,0 2,1 4,3 2,1 2,0 2,-1 1,-2 m -18,2 1,-2 2,-1 2,0 2,1 4,3 2,1 2,0 2,-1 1,-3 0,-2" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u007f" d="m 16.69094,-5.000616 -1,1 1,1 1,-1 -1,-1" style="fill:none;stroke:${options['colour']}" />
    <path id="s1-u00d7" d="m 0.5,8.5 8,-8 m -8,0 8,8" style="fill:none;stroke:${options['colour']}" />
    <path id="grave" d="m 5,-22 4,4" style="fill:none;stroke:${options['colour']}" />
    <path id="acute" d="m 4,-18 4,-4" style="fill:none;stroke:${options['colour']}" />
    <path id="circum" d="m 3,-18 3,-4 3,4" style="fill:none;stroke:${options['colour']}" />
    <path id="tilde" d="m 2.5,-18 2,-3 1,0 2,3 1,0 2,-3" style="fill:none;stroke:${options['colour']}" />
    <path id="dots" d="m 2.5,-20 1,1 1,-1 -1,-1 -1,1 m 5,0 1,1 1,-1 -1,-1 -1,1" style="fill:none;stroke:${options['colour']}" />
    <path id="ring" d="m 4,-20 2,-2 1,0 2,2 0,1 -2,2 -1,0 -2,-2 0,-1" style="fill:none;stroke:${options['colour']}"/>
    <g id="s1-u00e0"><use xlink:href="#s1-u0061"/><use xlink:href="#grave" transform="translate(4,0)"/></g>
    <g id="s1-u00e1"><use xlink:href="#s1-u0061"/><use xlink:href="#acute" transform="translate(4,0)"/></g>
    <g id="s1-u00e2"><use xlink:href="#s1-u0061"/><use xlink:href="#circum" transform="translate(4,0)"/></g>
    <g id="s1-u00e3"><use xlink:href="#s1-u0061"/><use xlink:href="#tilde" transform="translate(4,0)"/></g>
    <g id="s1-u00e4"><use xlink:href="#s1-u0061"/><use xlink:href="#dots" transform="translate(4,0)"/></g>
    <g id="s1-u00e5"><use xlink:href="#s1-u0061"/><use xlink:href="#ring" transform="translate(4,0)"/></g>
    <path id="s1-u00e6" d="m 8,-12.35 -1.6,-1.5 -1.9,0 -1.5,1.5 -0.2,1 0,1 0.5,2 0.5,1 1,1 1.6,0 1,-1 1,-2 m 0,-8.15048 l -0.6,-2 -1,-1 -1.6,0 -1.1,1 -1,2 m 4.5,3.06244 7.68356,0 0,-2.02557 -0.66542,-2.02558 -0.66543,-1.01279 -1.33084,-1.0128 -1.99627,0 -1.33084,1.0128 -1.33085,2.02558 -0.36391,3.03836 0,2.0256 0.36391,3.03836 1.33085,2.02558 1.33084,1.0128 1.99627,0 1.33084,-1.0128 1.33085,-2.02558" transform="translate(0,6)" style="fill:none;stroke:${options['colour']}" />

    <g id="s1-u00e8"><use xlink:href="#s1-u0065"/><use xlink:href="#grave" transform="translate(4,0)"/></g>
    <g id="s1-u00e9"><use xlink:href="#s1-u0065"/><use xlink:href="#acute" transform="translate(4,0)"/></g>
    <g id="s1-u00ea"><use xlink:href="#s1-u0065"/><use xlink:href="#circum" transform="translate(4,0)"/></g>
    <g id="s1-u00eb"><use xlink:href="#s1-u0065"/><use xlink:href="#dots" transform="translate(4,0)"/></g>
    <g id="s1-u00ec"><path d="m 2,-14 0,14" style="fill:none;stroke:${options['colour']}"/><use xlink:href="#grave"/></g>
    <g id="s1-u00ed"><path d="m 2,-14 0,14" style="fill:none;stroke:${options['colour']}"/><use xlink:href="#acute"/></g>
    <g id="s1-u00ee"><path d="m 2,-14 0,14" style="fill:none;stroke:${options['colour']}"/><use xlink:href="#circum" transform="translate(-1,0)"/></g>
    <g id="s1-u00ef"><path d="m 2,-14 0,14" style="fill:none;stroke:${options['colour']}"/><use xlink:href="#dots" transform="translate(-1,0)"/></g>

    <g id="s1-u00f2"><use xlink:href="#s1-u006f"/><use xlink:href="#grave" transform="translate(4,0)"/></g>
    <g id="s1-u00f3"><use xlink:href="#s1-u006f"/><use xlink:href="#acute" transform="translate(4,0)"/></g>
    <g id="s1-u00f4"><use xlink:href="#s1-u006f"/><use xlink:href="#circum" transform="translate(4,0)"/></g>
    <g id="s1-u00f5"><use xlink:href="#s1-u006f"/><use xlink:href="#tilde" transform="translate(4,0)"/></g>
    <g id="s1-u00f6"><use xlink:href="#s1-u006f"/><path d="m17,-14 -14,14" style="fill:none;stroke:${options['colour']}"/></g>
    <g id="s1-u00f8"><use xlink:href="#s1-u006f"/><use xlink:href="#dots" transform="translate(4,0)"/></g>
    <g id="s1-u00f9"><use xlink:href="#s1-u0075"/><use xlink:href="#grave" transform="translate(4,0)"/></g>
    <g id="s1-u00fa"><use xlink:href="#s1-u0075"/><use xlink:href="#acute" transform="translate(4,0)"/></g>
    <g id="s1-u00fb"><use xlink:href="#s1-u0075"/><use xlink:href="#circum" transform="translate(3,0)"/></g>
    <g id="s1-u00fc"><use xlink:href="#s1-u0075"/><use xlink:href="#dots" transform="translate(3,0)"/></g>

    <g id="s1-u00c0"><use xlink:href="#s1-u0041"/><use xlink:href="#grave" transform="translate(4,-5)"/></g>
    <g id="s1-u00c1"><use xlink:href="#s1-u0041"/><use xlink:href="#acute" transform="translate(4,-5)"/></g>
    <g id="s1-u00c2"><use xlink:href="#s1-u0041"/><use xlink:href="#circum" transform="translate(4,-5)"/></g>
    <g id="s1-u00c3"><use xlink:href="#s1-u0041"/><use xlink:href="#tilde" transform="translate(4,-5)"/></g>
    <g id="s1-u00c4"><use xlink:href="#s1-u0041"/><use xlink:href="#dots" transform="translate(4,-5)"/></g>
    <g id="s1-u00c5"><use xlink:href="#s1-u0041"/><use xlink:href="#ring" transform="translate(3,-3)"/></g>
    <path id="s1-u00c6" d="m 8,-21 -1,0 -7,21 m 3,-7 5,0 m 0,7 0,-21 8,0 m -8,10 6,0 m -6,11 8,0" style="fill:none;stroke:${options['colour']}" />

    <g id="s1-u00c8"><use xlink:href="#s1-u0045"/><use xlink:href="#grave" transform="translate(4,-5)"/></g>
    <g id="s1-u00c9"><use xlink:href="#s1-u0045"/><use xlink:href="#acute" transform="translate(4,-5)"/></g>
    <g id="s1-u00ca"><use xlink:href="#s1-u0045"/><use xlink:href="#circum" transform="translate(4,-5)"/></g>
    <g id="s1-u00cb"><use xlink:href="#s1-u0045"/><use xlink:href="#dots" transform="translate(4,-5)"/></g>

    <g id="s1-u00cc"><use xlink:href="#s1-u0049"/><use xlink:href="#grave" transform="translate(-1.5,-5)"/></g>
    <g id="s1-u00cd"><use xlink:href="#s1-u0049"/><use xlink:href="#acute" transform="translate(-1.5,-5)"/></g>
    <g id="s1-u00ce"><use xlink:href="#s1-u0049"/><use xlink:href="#circum" transform="translate(-1.5,-5)"/></g>
    <g id="s1-u00cf"><use xlink:href="#s1-u0049"/><use xlink:href="#dots" transform="translate(-1.5,-5)"/></g>

    <g id="s1-u00d2"><use xlink:href="#s1-u004F"/><use xlink:href="#grave" transform="translate(5.5,-5)"/></g>
    <g id="s1-u00d3"><use xlink:href="#s1-u004F"/><use xlink:href="#acute" transform="translate(5.5,-5)"/></g>
    <g id="s1-u00d4"><use xlink:href="#s1-u004F"/><use xlink:href="#circum" transform="translate(5.5,-5)"/></g>
    <g id="s1-u00d5"><use xlink:href="#s1-u004F"/><use xlink:href="#tilde" transform="translate(5.5,-5)"/></g>
    <g id="s1-u00d6"><use xlink:href="#s1-u004F"/><path d="m 0,21 17,-20" style="fill:none;stroke:${options['colour']}"/></g>
    <g id="s1-u00d8"><use xlink:href="#s1-u004F"/><use xlink:href="#dots" transform="translate(5.5,-5)"/></g>

    <g id="s1-u00d9"><use xlink:href="#s1-u0055"/><use xlink:href="#grave" transform="translate(5,-5)"/></g>
    <g id="s1-u00da"><use xlink:href="#s1-u0055"/><use xlink:href="#acute" transform="translate(5,-5)"/></g>
    <g id="s1-u00db"><use xlink:href="#s1-u0055"/><use xlink:href="#circum" transform="translate(4.5,-5)"/></g>
    <g id="s1-u00dc"><use xlink:href="#s1-u0055"/><use xlink:href="#dots" transform="translate(4.5,-5)"/></g>
  </defs>
% if options['single_page'] is False:
<pageSet>
<page>
% endif
% for p, full_code, accession in enumeration:
  % if xpos == 4:
    <% xpos = 0 %>\
    <% ypos += 1 %>\
  % endif
  % if ypos == 18 and options['single_page'] is False:
    <% xpos = 0 %>\
    <% ypos = 0 %>\
    </page>
    <page>
  % endif
  <g transform="scale(3.543)translate(7,14)translate(${xpos*49},${ypos*15})">
    <path d="M 0,0 49,0 49,15 0,15 z" style="fill:none;stroke:#ff0000;stroke-width:0.1" />
<% unit = 2.65 / len(full_code + '!!') %>\
<% text, x, y = add_text(33, 7.5, full_code, 0.20, align=1, strokes=2) %>\
    ${text}
% if options['extra_text']:
<%
et = options['extra_text']
if accession and et.startswith('{') and et.endswith('}'):
    ets = accession
    for step in et[1:-1].split('.'):
        ets = getattr(ets, step)
    et = str(ets)
x_base = 1
text, x, y = add_text(x_base, 12.5, et, 0.12, align=0, italic=True)
%>\
 % if (x-x_base) > 32:
   <g transform="translate(${x_base},0)scale(${32.0/(x-x_base)},1)translate(-${x_base},0)">${text}</g>
 % else:
   <g transform="translate(${33 - x},0)">${text}</g>
 % endif
% endif
<% text = add_qr(35, 1, full_code, side=13) %>\
    ${text}
  </g>
<% xpos += 1 %>\
% endfor
% if options['single_page'] is False:
</page>
</pageSet>
% endif
</svg>