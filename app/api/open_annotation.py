

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
          "@type": "dctypes:Dataset",
          "format": "text/json"
      },
     # "on": canvas_url
  })
  return annotation_list


