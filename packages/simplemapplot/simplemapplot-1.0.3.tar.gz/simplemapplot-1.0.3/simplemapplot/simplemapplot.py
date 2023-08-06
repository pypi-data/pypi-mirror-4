#!/usr/bin/env python
#
# Plot data into a county-level map of the US.
# Counties in the US are determined by a FIPS code.
#
# Inspired by tutorial at
#   http://flowingdata.com/2009/11/12/how-to-make-a-us-county-thematic-map-using-free-tools/
#
# But modified to not use beautiful soup, and use CSS instead (cleaner, I think).
#
# Michael Anderson, May 2012

import os
import shutil

#from bs4 import BeautifulSoup

default_colors = ["#A6BDDB","#7FA9CF","#2B8CBE","#045A8D"]

svg_file_location = os.path.dirname(__file__)
blank_world_svg = svg_file_location+'/BlankMap-World6.svg'
blank_world_css = svg_file_location+'/BlankMap-World6.css'
blank_state_svg = svg_file_location+'/Blank_US_Map.svg'
blank_state_css = svg_file_location+'/Blank_US_Map.css'
blank_counties_map = svg_file_location+'/Usa_counties_large.svg'

#def make_us_county_map(
#    data,
#    colors=default_colors,
#    min_value=None,
#    max_value=None,
#    output_img="output_county_map.svg"):
#    '''
#    Create svg image of US counties colored specifically.
#    Inputs:
#    data = dict where key=FIPS (county code), value=any number (determines color)
#    colors = array of strings storing color codes
#    '''
#    if not min_value: min_value = min([data[key] for key in data]) # Counties near the min get colors[0]
#    if not max_value: max_value = max([data[key] for key in data]) # Counties near the min get colors[-1]
#    # Load SVG map into BeautifulSoup
#    svg = open(blank_counties_map, 'r').read()
#    soup = BeautifulSoup(svg)
#    # Find counties in the SVG map
#    paths = soup.findAll('path')
#    # County style
#    path_style = 'fill-opacity:1;stroke:#ffffff;stroke-opacity:1;stroke-width:0.75;stroke-miterlimit:4;stroke-dasharray:none;fill:'
#    # Color the counties based on dictionary data
#    for p in paths:
#        if p['id'] not in ["State_Lines", "separator"]:
#            try:
#                county_value = data[p['id']]
#            except:
#                continue
#            color_class = int(round(
#                                float(len(colors)-1)*float(county_value-min_value)/
#                                float(max_value - min_value)))
#            color = colors[color_class]
#            p['style'] = "".join([path_style, color])
#        
#    # Save result into a file
#    f = open(output_img, "w")
#    f.writelines(soup.prettify())
#    print "Created %s" % output_img

def make_us_state_map(data,
    colors=default_colors,
    output_img="output_state_map.svg"):
    '''
    Create svg image of US counties colored specifically.
    Inputs:
    data = dict where key=State Abbreviation (AL, AK, AZ etc..), value=number determines color
    colors = array of strings storing color codes
    '''
    if not data: return
    if min(data.values())<0 or max(data.values())>len(colors):
        print "Error: values must range 0 to %s" % len(colors)
        return
    # Determine level for each state in data
    levels = dict( (i, []) for i in range(len(colors)) )
    for key in data:
        level = data[key]
        levels[level].append(key)
    # Create CSS from levels
    css_code = []
    for i, l in enumerate(levels):
        if not levels[l]: continue
        levels[l][0] = "#" + levels[l][0] # hack to get '#' in front of first element
        names = ", #".join(levels[l])
        full_string = "%s {\n  fill:%s;\n}" % (names, colors[i])
        css_code.append(full_string)
    # Copy default CSS to local dir
    shutil.copyfile(blank_state_css, "Blank_US_Map.css")
    # Append new style code to CSS file
    style_file = open("Blank_US_Map.css", "a")
    style_file.write("\n".join(css_code))
    style_file.close()
    shutil.copyfile(blank_state_svg, output_img)
    print "Created %s" % output_img

def make_world_country_map(data,
    colors=default_colors,
    output_img="output_country_map.svg"):
    '''
    Create svg image of countries colored specifically.
    Inputs:
    data = dict where key=Country Abbreviation (US, GB, CN etc..), value=any number (determines color)
    colors = array of strings storing color codes
    '''
    if not data: return
    if min(data.values())<0 or max(data.values())>len(colors):
        print "Error: values must range 0 to %s" % len(colors)
        return
    # Determine level for each country in data
    levels = dict( (i, []) for i in range(len(colors)) )
    for key in data:
        level = data[key]
        levels[level].append(key)
    # Create CSS from levels
    css_code = []
    for i, l in enumerate(levels):
        if not levels[l]: continue
        levels[l][0] = "." + levels[l][0] # hack to get '.' in front of first element
        names = ", .".join(levels[l])
        full_string = "%s {\n  fill:%s;\n}" % (names, colors[i])
        css_code.append(full_string)
    # Copy default CSS to local dir
    shutil.copyfile(blank_world_css, "BlankMap-World6.css")
    # Append new style code to CSS file
    style_file = open("BlankMap-World6.css", "a")
    style_file.write("\n".join(css_code))
    style_file.close()
    shutil.copyfile(blank_world_svg, output_img)
    print "Created %s" % output_img

if __name__ == '__main__':
    example_colors = ["#FC8D59","#FFFFBF","#99D594"]
    state_value = {"TX":2, "WI":1, "IL":1, "AK":0, "MI":0, "HI":2} # key=state abbrev, value=index of color
    make_us_state_map(data=state_value, colors=example_colors)
    country_value = {"us":1, "au":2, "gb":0}  # key=country code, value=index of color
    make_world_country_map(data=country_value, colors=example_colors)
