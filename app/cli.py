import pprint
from urllib.request import urlopen

import click


from app import create_app
from app.api.routes import json_loads
from app.models import Image, ImageUrl

app = None
env = None

def add_default_users(db):
    # TODO
    db.session.flush()


def make_cli():
    """ Creates a Command Line Interface for everydays tasks

    :return: Click groum
    """
    @click.group()
    @click.option('--config', default="dev")
    def cli(config):
        """ Generates the client"""
        click.echo("Loading the application")
        global app
        global env
        env = config
        app = create_app(config)

    @click.command("db-create")
    def db_create():
        """ Creates a local database
        """
        with app.app_context():
            from app import db
            db.create_all()

            add_default_users(db)

            db.session.commit()
            click.echo("Created the database")

    @click.command("db-recreate")
    def db_recreate():
        """ Recreates a local database. You probably should not use this on
        production.
        """
        with app.app_context():
            from app import db
            db.drop_all()
            db.create_all()

            add_default_users(db)

            db.session.commit()
            click.echo("Dropped then recreated the database")

    @click.command("load-fixtures")
    def db_load_fixtures():
        """ Reload fixtures
        """
        with app.app_context():
            from app import db
            from tests.data.entities import load_fixtures

            load_fixtures(db)

            db.session.commit()
            click.echo("Fixtures (re)loaded")

    @click.command("add-manifest")
    @click.option('--manifest-url', required=True)
    @click.option('--doc-id', required=True)
    def db_add_manifest(manifest_url, doc_id):
        """
        Fill the image & image_url tables with every image in the given manifest
        """
        manifest_data = urlopen(manifest_url).read()
        data = json_loads(manifest_data)

        if data['@context'] == "https://iiif.io/api/presentation/3/context.json":
            print('IIIF Presentation v3 detected')

            with app.app_context():
                from app import db

                for canvas_idx, canvas in enumerate(data["items"]):
                    for img_idx, anno_page in enumerate(canvas["items"]):
                        image_url = anno_page["items"][0]["body"]["id"]

                        new_image = Image(
                            manifest_url=manifest_url,
                            canvas_idx=canvas_idx,
                            img_idx=img_idx,
                            doc_id=doc_id
                        )
                        new_image_url = ImageUrl(
                            manifest_url=manifest_url,
                            canvas_idx=canvas_idx,
                            img_idx=img_idx,
                            img_url=image_url
                        )

                        db.session.add(new_image)
                        db.session.add(new_image_url)
                        db.session.flush()
                        print('Adding new image:', new_image.serialize())
                        print('Adding new image_url:', new_image_url.serialize())

                db.session.commit()

        elif data['@context'] == "https://iiif.io/api/presentation/2/context.json":
            print('IIIF Presentation v2 detected')
            with app.app_context():
                from app import db

                for canvas_idx, canvas in enumerate(data["sequences"][0]["canvases"]):
                    for img_idx, image in enumerate(canvas["images"]):
                        image_url = image["resource"]["@id"]

                        new_image = Image(
                            manifest_url=manifest_url,
                            canvas_idx=canvas_idx,
                            img_idx=img_idx,
                            doc_id=doc_id
                        )
                        new_image_url = ImageUrl(
                            manifest_url=manifest_url,
                            canvas_idx=canvas_idx,
                            img_idx=img_idx,
                            img_url=image_url
                        )

                        db.session.add(new_image)
                        db.session.add(new_image_url)
                        db.session.flush()
                        print('Adding new image:')
                        pprint.pprint(new_image.serialize())
                        print('Adding new image_url:')
                        pprint.pprint(new_image_url.serialize())

                db.session.commit()
        else:
            print('@context not supported:', data['@context'])
            return

    @click.command("run")
    def run():
        """ Run the application in Debug Mode [Not Recommended on production]
        """
        app.run()

    cli.add_command(db_create)
    cli.add_command(db_recreate)
    cli.add_command(db_add_manifest)
    cli.add_command(db_load_fixtures)

    cli.add_command(run)

    return cli
