from bs4 import BeautifulSoup
from requests import get
import sqlite3

from flask import Flask, render_template, escape, request

app = Flask(__name__)

@app.route('/jquery-3.4.1.min.js')
def getJquery():
    jquery = open("jquery-3.4.1.min.js")
    return jquery.read()

@app.route('/')
def poem():
    html_doc = open("template.html")
    return html_doc.read()

@app.route('/poem_links')
def getLinks():
    cl_missedconnections = get('https://sfbay.craigslist.org/d/missed-connections/search/mis')
    clmc_soup = BeautifulSoup(cl_missedconnections.text, 'html.parser')

    posts = clmc_soup.find_all('li', class_= 'result-row')
    poem_links = []
    for p in posts:
        post_link = p.find_all('a', class_= 'result-title')[0]['href']
        poem_links.append('"{}"'.format(post_link))
    return '[{}]'.format(','.join(poem_links))

@app.route('/poem')
def getPoem():
    # TODO Get URL, check if the database already has the poem info
    # conn = sqlite3.connect('example.db')

    # TODO scan head for metadata

    post_link = request.args.get('post_link')
    post_req = get(post_link)

    post_soup = BeautifulSoup(post_req.text, 'html.parser')
    post_head = post_soup.head

    placeName = post_soup.find("meta", {'name': "geo.placename"})["content"]
    coordinates = post_soup.find("meta", {'name': "geo.position"})["content"]

    poem_body = post_soup.find(id='postingbody')
    item = ''
    for item in poem_body.children:
        pass
    words = item.split()
    # word_syllables = [(w,h_en.syllables(w)) for w in words]
    haiku_syllables = 0
    ind_syllables = 0
    debug_text = ''
    poem_text = ''

    newline = '<br>'

    from hyphen import Hyphenator
    h_en = Hyphenator('en_US')

    for word in words:
        if haiku_syllables >= 17:
            break
        syl = h_en.syllables(word)
        old_haiku_syllables = haiku_syllables
        num_syls = len(syl)
        haiku_syllables += num_syls
        if num_syls == 0:
            debug_text += '0'
            num_syls = 1
            haiku_syllables += 1
        if num_syls > 0:
            syllable_bounds = [5,12]
            did_bound_op = False
            for bd in syllable_bounds:
                if haiku_syllables == bd:
                    did_bound_op = True
                    poem_text += word + newline
                    debug_text += 'a'
                if old_haiku_syllables < bd and haiku_syllables > bd:
                    debug_text += 'b'
                    did_bound_op = True
                    syl_index = 0
                    while syl_index + old_haiku_syllables < bd:
                        poem_text += syl[syl_index]
                        syl_index += 1
                    poem_text += '-{}'.format(newline)
                    while syl_index + old_haiku_syllables < haiku_syllables:
                        poem_text += syl[syl_index]
                        syl_index += 1
                    poem_text += ' '
                if did_bound_op:
                    break
            if not did_bound_op:
                debug_text += 'c'
                poem_text += word + ' '
        ind_syllables += 1
    print debug_text
    obj = dict()
    obj['poem'] = poem_text
    obj['url'] = post_link
    obj['placeName'] = placeName
    obj['coordinates'] = coordinates
    import json
    return json.dumps(obj)
