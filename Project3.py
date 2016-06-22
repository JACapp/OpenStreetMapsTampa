
# coding: utf-8

# In[ ]:

#import packages needed for project
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import codecs
import json

#open file
osm_file = open("C://Udacity/tampa_florida.osm", "r")

#determine type and number of first level tags
#input: osm file as xml
#output: list and count of first level tags
def count_tags_first(filename):
    
        # Set up dictionary
        tags_dictionary= {}
        
        #parse the data, collecting unique tags
        for event, elem in ET.iterparse(filename, events=('start',)):
            if elem.tag in tags_dictionary:
                tags_dictionary[elem.tag] = tags_dictionary[elem.tag] + 1
            else:
                tags_dictionary[elem.tag] = 0
                tags_dictionary[elem.tag] = tags_dictionary[elem.tag] + 1
        
        pprint.pprint(tags_dictionary)
        pprint.pprint(len(tags_dictionary))

        return tags_dictionary


#determine number of unique keys within the <tag tag in the dataset:
#input: osm file in xml format
#output: sorted and counted list of unique keys within <tag

def get_subelement(filename):
    #set key dictionary
    key_dictionary = {}
    
    #as above, parse the data to find unique tags
    for event, element in ET.iterparse(filename, events=('start', 'end')):
        for tag in element.iter():
            if tag.tag == 'tag':
                key = tag.attrib['k']
                if key in key_dictionary:
                    key_dictionary[key] = key_dictionary[key] + 1
                else:
                    key_dictionary[key] = 0
                    key_dictionary[key] = key_dictionary[key] + 1
            
    #sort the tags by count, descending
    sort_key_dictionary = sorted(key_dictionary.items(), key=lambda x: (-x[1], x[0]))
    
    pprint.pprint(sort_key_dictionary)
    pprint.pprint(len(sort_key_dictionary))
    
    return sort_key_dictionary


#audit street name data:
#create lists of acceptible street names, directions, and city names. create mappings to correct unacceptible street, city names.

#define regular expressions to search the fields addr:street and addr:city
#regular expression will match the last word in a string, case-insensitive, w/wo period
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

#regular expression will match the first word in a string, case-insensitive, w/wo period
street_type_first_re = re.compile(r'^\S+\.?\b', re.IGNORECASE)

#regular expression will match the string
city_type_re = re.compile(r'^.*$')


#set-up dictionaries and mappings:
#acceptible street types for this dataset
street_expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Causeway", "Passage", "Circle", "Cutoff", "Bypass", "Plaza", 
            "Loop", "Parking Garage", "Way", "Esplanade", "Highway", "Skyway", "Bridge", "Terrace",
            #the following, while not "street types" specifically, are acceptible ends of the string for the street data"
            "52", "Arts", "64", "19", "301", "98", "54", "Mall", "92", "Cuba", "100", "101", "41", "60"]


#street types that need fixing
street_mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "Pkwy": "Parkway",
            "Cir": "Circle",
            "dr": "Drive",
            "Cswy": "Causeway",
            "Dr.": "Drive",
            "Pl": "Place",
            "Plz": "Plaza",
            "Ave.": "Avenue",
            "Prkg": "Parking Garage",
            "Pky": "Parkway",
            "AVE": "Avenue",
            "road": "Road",
            "St": "Street",
            "Ct": "Court",
            "Ln": "Lane",
            "Hwy": "Highway",
            "Dr": "Drive",
            "skyway": "Skyway",
            "lane": "Lane",
            "st": "Street",
            "Av": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "drive": "Drive",
            #mapping individual - fixes to street names - these only occur once in the dataset, not straightforward to fix
            "US-19": "US Highway 19",
            "U.S.19": "US Highway 19",
            "FL)": "",
            "Harrison": "Harrison Avenue",
            "34205": ""}



#start of addr:street that needs fixing
start_fixes = ["Notth", "N.", "NE", "E", "N", "S", "E.", "W", "SW", "SE", "SR", "FL", "U.S.", "9201", "4040", "8203", "30387", "7499"]


#directions that need fixing
direction_mapping = {"Notth": "North",
                     "N.": "North",
                     "NE": "Northeast",
                     "E": "East",
                     "N": "North",
                     "S": "South",
                     "E.": "East",
                     "W": "West",
                     "SW": "Southwest",
                     "SE": "Southeast",
                     "SR": "State Road",
                     "FL": "State Road",
                     "U.S.": "US",
                     #single changes to the start of the street name
                     "9201": "",
                     "4040": "",
                     "8203": "",
                     "30387": "",
                     "7499": ""}


#directions present at the end of a street name that need moving to the start of the name
direction_names = ["North", "South", "East", "West", "Northeast", "Northwest", "Southeast", "Southwest",
                     "Notth", "N.", "NE", "E", "N", "S", "E.", "W", "SW", "SE"]

#acceptible city names
cities_expected = ['Anna Maria','Apollo Beach','Belleair','Belleair Beach','Bradenton','Bradenton Beach','Brandon','Clearwater','Clearwater Beach',
                   'Cortez Village','Dade City','Dover','Dunedin','Ellenton','Feather Sound','Gandy','Gibsonton','Gulfport',
                   'Holiday','Holmes Beach','Hudson','Indian Shores','Kenneth City','Lakeland','Lakewood Ranch','Land O Lakes',
                   'Largo','Lithia','Longboat Key','Lutz','Madeira Beach','New Port Richey','Odessa','Oldsmar','Palm Harbor',
                   'Palmetto','Parrish','Pass-a-Grille Beach','Pasadena', 'Pinellas Park','Plant City','Port Richey','Redington Beach',
                   'Redington Shores','Riverview','Ruskin','Safety Harbor','Saint Leo','Saint Petersburg','Saint Petersburg Beach',
                   'San Antonio','Sarasota','Seminole','South Highpoint','South Pasadena','Sun City Center','Tampa','Tarpon Springs',
                   'Temple Terrace','Thonotosassa','Treasure Island','Trinity','Valrico','Wesley Chapel','Zephyrhills']

#cities that need fixing
cities_mapping = {'Clearwater ': 'Clearwater',
                  'Land O Lakes, FL': 'Land O Lakes',
                  "Land O' Lakes": 'Land O Lakes',
                  'Palm Harbor, Fl.': "Palm Harbor",
                  "Seminole ": "Seminole",
                  'St Petersburg': "Saint Petersburg",
                  'St Petersburg ': "Saint Petersburg",
                  'St. Pete Beach': "Saint Petersburg Beach",
                  'St. Petersburg': "Saint Petersburg",
                  'St. Petersburg, FL': "Saint Petersburg",
                  'St Petersbug': "Saint Petersburg",
                  'dover': "Dover",
                  'lutz': "Lutz",
                  "sarasota": "Sarasota",
                  "tampa": "Tampa",
                  "Tampa ": "Tampa"}



#audit "addr:street"
#check for irregularities at the end of street names and move the directional terms to the start of the street name
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        
        #move direction
        if street_type in direction_names:
            street_split = str.rsplit(street_type)
            reorder = street_split[-1:] + street_split[0:-1]
            street_type = " ".join(reorder)
            return street_type
        
            if street_type not in street_expected:
                street_types[street_type].add(street_name) 
                return street_type
        
        #audit remaining street names
        elif street_type not in street_expected:
            street_types[street_type].add(street_name)
            return street_type


#check for irregularities at the beginning of street names        
def audit_street_type_first(street_types, street_name):
    m = street_type_first_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in direction_expected:
            street_types[street_type].add(street_name)
            return street_types
        
#define the street name element
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


#audit the file
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    #audit_street_type(street_types, tag.attrib['v'])
                    audit_street_type_first(street_types, tag.attrib['v'])
                    
    
    #pprint.pprint(street_types)
    pprint.pprint(sorted(street_types))
    pprint.pprint(len(sorted(street_types)))
    return street_types


#audit "addr:city"
#audit the city names to find irregularities
def audit_city_type(city_types, city_name):
    m = city_type_re.search(city_name)
    if m:
        city_type = m.group()
        if city_type not in cities_expected:
            city_types[city_type].add(city_name)
            return city_type


#define thecity name element
def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")

#audit the osm file
def audit(osmfile):
    osm_file = open(osmfile, "r")
    city_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city_name(tag):
                    audit_city_type(city_types, tag.attrib['v'])

    pprint.pprint(sorted(city_types))
    pprint.pprint(len(sorted(city_types))


#audit "addr:postcode"
#regular expression will match the entire string
postal_type_re = re.compile(r'^.*$', re.IGNORECASE)

postal_expected = []

postal_mapping = {}

#audit the postal codes to find irregularities
def audit_postal_type(postal_types, postal_name):
    m = postal_type_re.search(postal_name)
    if m:
        postal_type = m.group()
        if postal_type not in postal_expected:
            postal_types[postal_type].add(postal_name)
        return postal_type


#define the postal name element
def is_postal_name(elem):
    return (elem.attrib['k'] == "addr:postcode")

#audit the osm file
def audit(osmfile):
    osm_file = open(osmfile, "r")
    postal_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_name(tag):
                    audit_postal_type(postal_types, tag.attrib['v'])

    pprint.pprint(sorted(postal_types))
    pprint.pprint(len(sorted(postal_types))
    return postal_types


#update adrress fields:
#update "addr:city"
def update_city(name, mapping):
    m = city_type_re.search(name)
    if m:
        city_type = m.group()
        if city_type not in cities_expected:
            name = re.sub(city_type_re, mapping[city_type], name)
    return name

#update "addr:postcode"
def update_postcode(name):
    name = name[0:5]
    return name

#update "addr:street"
#first, check the end of the street name
def update_street_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        #check to see if the last word in the string is a direction, if so, move it to the start of the string
        if street_type in direction_names:
            street_split = str.rsplit(name)
            reorder = street_split[-1:] + street_split[0:-1]
            name = " ".join(reorder)          
        #if the last word in the string is not a direction, compare it to the list of acceptible street names and fix if necessary    
        elif street_type not in street_expected:
            name = re.sub(street_type_re, mapping[street_type], name)
    return name
    
#now check the start of the street name
def update_direction_name(name, mapping):
    n = street_type_first_re.search(name)
    if n:
        direction_type = n.group()
        if direction_type in start_fixes:
            name = re.sub(street_type_first_re, mapping[direction_type], name)         
    return name

#regular expressions to be applied to tags
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def shape_element(element):
    #initialize node
    node = {}
    #go through all nodes and ways
    if element.tag == "node" or element.tag == "way" :
        #check keys for created, latitude, and longitude
        for key in element.attrib:
            node["id"] = element.attrib["id"]
            node["type"] = element.tag
            node["visible"] = element.get("visible")
        
            #initialize created
            created = {}
            created["version"] = element.attrib["version"]
            created["changeset"] = element.attrib["changeset"]
            created["timestamp"] = element.attrib["timestamp"]
            created["user"] = element.attrib["user"]
            created["uid"] = element.attrib["uid"]
            node["created"] = created
        
            #retrieve lat and lon
            if "lat" in element.keys() and "lon" in element.keys():
                lat = float(element.attrib["lat"])
                lon = float(element.attrib["lon"])
                pos = [lat, lon]
                node["pos"] = pos
            else:
                node["pos"] = None
            
        #initialize address
        address = {}
        
        #go through the tags
        for tag in element.iter("tag"):
            key = tag.attrib["k"]
            value = tag.attrib["v"]
            
            #check key to make sure it is valid            
            if problemchars.search(key):
                pass
            elif lower.search(key):
                node[key] = value
            elif lower_colon.search(key):
                #keep keys that start with "addr:"
                if key[0:5] != "addr:":
                    continue
                else:
                    if "address" not in node:
                        node["address"] = {}
                        #audit and clean city names
                        if key[:] == "addr:city":
                            value = update_city(value, cities_mapping)
                            node["address"]["city"] = value     
                        #audit and clean postal codes
                        if key[:] == "addr:postcode":
                            value = update_postcode(value)
                            node["address"]["postcode"] = value
                        #audit and clean street names
                        if key[:] == "addr:street":
                            #if the end of the string is a direction, move it to the front
                            value = update_street_name(value, street_mapping)
                            #clean the street types
                            value = update_street_name(value, street_mapping)
                            #clean the start of the street names to normalize directions and highway names
                            value = update_direction_name(value, direction_mapping)
                            node["address"]["street"] = value   
                        #collect all other tags in address
                        else:
                            node["address"][key[5:]] = value

            elif key == 'type': #already assigned doesn't get overwritten
                node['typekey'] = value
            #collect all other misc. tags in data
            else:
                node[key] = value
        
        #populate way-specific field node_ref
        node_refs = []
        if element.tag == "way":
            for nd in element.iter("nd"):
                node_refs.append(nd.get("ref"))
            node["node_refs"] = node_refs

        return node
    else:
        return None


#aggregate function to clean the osm file and write it as a json file
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
    print keys

if __name__ == "__main__":
    process_map(OSMFILE, pretty = False)

