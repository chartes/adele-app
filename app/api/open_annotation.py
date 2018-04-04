import pprint

from flask import app

import requests

d = {
  "@context":"http://iiif.io/api/presentation/2/context.json",
  "@id":"http://www.example.org/iiif/book1/list/p1",
  "@type":"sc:AnnotationList",

  "resources": [
    {
      "@type":"oa:Annotation",
      "motivation":"sc:painting",
      "resource":{
        "@id":"http://www.example.org/iiif/book1/res/tei-text-p1.xml",
        "@type":"dctypes:Text",
        "format":"text/xml"
      },
      "on":"http://www.example.org/iiif/book1/canvas/p1"
    }
  ]
}

def make_annotation_list(doc_id) :
  return {
    "@context":"http://iiif.io/api/presentation/2/context.json",
    "@id": f"http://adele.chartes.psl.eu/dossiers/{doc_id}/list/f1",
    "@type": "sc:AnnotationList",
    "resources": [
    ]
  }

def make_annotation(canvas_url, content_url):
  return {
    "@type": "oa:Annotation",
    "motivation": "sc:painting",
    "resource": {
      "@id": content_url,
      "@type": "dctypes:Text",
      "format": "text/xml"
    },
    "on": canvas_url
  }


