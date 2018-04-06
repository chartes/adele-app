from config import Config


def make_annotation_list(list_id, doc_id, annotations) :
  return {
      "@context":"http://iiif.io/api/presentation/2/context.json",
      "@id": "http://{0}/dossiers/{1}/list/{2}".format(Config.APP_DOMAIN_NAME, doc_id, list_id),
      "@type": "sc:AnnotationList",
      "resources": annotations
  }

def make_annotation(canvas_uri, res_uri, content, format="text/plain"):
  anno = {
      "@type": "oa:Annotation",
      "motivation": "sc:painting",
      "resource": {
          "@type":"cnt:ContentAsText",
          "chars": content,
          "format": format
      },
      "on": canvas_uri
  }
  if res_uri is not None:
      anno["resource"]["@id"] = res_uri
  return anno

