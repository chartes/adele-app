import json
import pprint

from flask import Response


class APIResponseFactory:

    @classmethod
    def make_response(cls, status, data=(), errors=(), meta=(), links=()):

        r = {}

        # MUST have either data either errors
        #if len(data) == 0 and len(errors) == 0:
        #    raise ValueError("MUST have either data either errors. data: {0} errors: {1}".format(data, errors))

        if len(errors) == 0:
            #if cls.is_iterable(data):
            #    if len(data) == 1:
            #        if isinstance(data, set):
            #            data = data.pop()
            #        else:
            #            data = data[0]
            r["data"] = data
        else:
            r["errors"] = errors

        if len(links) > 0:
            r["links"] = links

        if len(meta) > 0:
            r["meta"] = meta

        return Response(
            json.dumps(r, indent=2, ensure_ascii=False),
            status=status,
            content_type="application/json; charset=utf-8",
            headers={
                #"Access-Control-Allow-Origin": "*",
                #"Access-Control-Allow-Credentials": "true"
            }
        )

    @classmethod
    def is_iterable(cls, res):
        return isinstance(res, (list, tuple, set))

    @classmethod
    def has_errors(cls, response):
        return "errors" in response

    @classmethod
    def has_data(cls, response):
        return "data" in response

    @classmethod
    def is_data_single(cls, response):
        if cls.has_data(response):
            return cls.is_iterable(response["data"])
        raise ValueError("There is no data in this response")

    @classmethod
    def is_errors_single(cls, response):
        if cls.has_errors(response):
            return cls.is_iterable(response["errors"])
        raise ValueError("There is no errors in this response")

    @classmethod
    def add_error(cls, response, errors):
        if cls.has_data(response):
            raise ValueError("There is data in this response")

        d = response["errors"] if cls.is_iterable(response["errors"]) else [response["errors"]]

        if cls.is_iterable(errors):
            if len(errors) == 1:
                d.append(errors[0])
            else:
                d.extend(errors)
        else:
            d.append(errors)

        response["errors"] = d
        return response

    @classmethod
    def add_data(cls, response, data):
        if cls.has_errors(response):
            raise ValueError("There is errors in this response")

        d = response["data"] if cls.is_iterable(response["data"]) else [response["data"]]

        if cls.is_iterable(data):
            if len(data) == 1:
                d.append(data[0])
            else:
                d.extend(data)
        else:
            d.append(data)

        response["data"] = d
        return response


if __name__ == "__main__":

    r = APIResponseFactory.make_response(data={"id": 1, "name": "Deux points juxtapos\u00e9s"})
    pprint.pprint(r)
    r = APIResponseFactory.add_data(r, [{"id": 2, "name": "Brian"}, {"id": 3, "name": "John"}])
    pprint.pprint(r)
    r = APIResponseFactory.add_data(r, {"id": 4, "name": "John"})
    pprint.pprint(r)

    r = APIResponseFactory.make_response(errors={"status": 404})
    pprint.pprint(r)
    r = APIResponseFactory.add_error(r, errors={"id": 1234, "title": "this is an error 1234"})
    pprint.pprint(r)
