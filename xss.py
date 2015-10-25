#coding=utf-8
import os
import re
import requests
import xml.etree.ElementTree as ET

URL_HANDLER_PATTERN = re.compile(r'@RequestMapping\((\{\"[^"]+\"\}|value=\{\"[^"]+\"\}\s*,\s*method=\{[^}]+\})[^)]*\)')
RETURN_PATTERN = re.compile(r'return "([^"]+)";')
PARAM_REG = re.compile(r'${([^}]+?)}')
XSS_PATTERN = r'<"\'>'
URL = 'http://www.baidu.com'
result = open('result.txt', 'w')


def sendRequest(key, urlPattern):
    url = URL + urlPattern + '?' + key + '=' + XSS_PATTERN
    r = requests.get(url)
    if PARAM_REG.match(r.text):
        result.write(url)


def analyzeFile(jsp, urlPattern):
    for line in open(jsp):
        matches = PARAM_REG.match(line)
        express = set()
        if matches:
            express.add(matches[1])
    for i in express:
        sendRequest(i, urlPattern)


def getFiles(srcfolder, reg):
    reg = re.compile(reg)
    files = []
    for filepath, dirs, files in os.walk(srcfolder):
        for f in files:
            if reg.match(f):
                files.append(os.path.join(filepath, f))
    return files

def analyzeJavaFile(javaFiles, tileMap):
    result = []
    for javaFile in javaFiles:
        urlPattern = ''
        methods = ['get']
        views = set()
        for line in open(javaFile, 'r'):
            matches =  URL_HANDLER_PATTERN.match(line)
            if matches:
                if len(views):
                    result.append({
                        "javaFIle": javaFile,
                        "views": views,
                        "methods": methods,
                        "urlMap": urlPattern
                    })
                    views = set()
                    methods = ['get']
                urlPattern = matches[1]
            else:
                matches = RETURN_PATTERN.match(line)
                if matches:
                    views.add(tileMap.get(matches[1]))
        if len(views):
            result.append({
                "javaFIle": javaFile,
                "views": views,
                "methods": methods,
                "urlPattern": urlPattern
            })
    return result

def analyzeTiles(tileFiles):
    result = {}
    for tileFile in tileFiles:
        root = ET.parse(tileFile).getroot()
        if root.tag != 'tiles-defiitions':
            continue
        for item in root.findall('definition'):
            for node in item:
                if node.tag == 'put-attribute' and node.get('name') == 'content':
                    result[item.get('name')] = node.get('value')
    return result

def checkXss(javaMap):
    for servlet in javaMap:
        for jsp in servlet.get('views'):
            analyzeFile(jsp, servlet.get('urlPattern'))


def main():
    tileFiles = getFiles(src, r'^tile.*\.xml$')
    tileMap = analyzeTiles(tileFiles)

    javaFiles = getFiles(src, r'^.*\.java$')
    javaMap = analyzeJavaFile(javaFiles, tileMap)



    checkXss(javaMap)

if __name__ == '__main__':
    main()
    walkdir('')
    result.close()