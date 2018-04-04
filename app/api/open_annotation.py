import pprint


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
      "@id": "http://adele.chartes.psl.eu/dossiers/{0}/list/f1".format(doc_id),
      "@type": "sc:AnnotationList",
      "resources": [
      ]
  }

def add_annotation(annotation_list, content_url):
  annotation_list["resources"].append( {
      "@type": "oa:Annotation",
      "motivation": "sc:painting",
      "resource": {
          "@id": content_url,
          "@type": "dctypes:Text",
          "format": "text/xml"
      },
     # "on": canvas_url
  })
  return annotation_list


