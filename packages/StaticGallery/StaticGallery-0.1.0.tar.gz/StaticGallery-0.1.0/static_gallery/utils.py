import os
import SimpleHTTPServer
import SocketServer

from PIL import Image
import ExifTags
from jinja2 import Environment, FileSystemLoader
from mimetypes import guess_type

from configuration import *


if os.path.exists(TEMPLATES_PATH):
    loader = FileSystemLoader(TEMPLATES_PATH)
else:
    loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))

env = Environment(loader=loader)


def generate_html_output(path, template_name, arguments):
    template = env.get_template(template_name)
    template_content = template.render(**arguments)

    # save static file
    new_file = file(path, 'w')
    new_file.write(template_content)
    new_file.close()


def create_menu(dst_path, template_name):
        galleries = []
        gallery_path = dst_path

        for gallery in os.listdir(gallery_path):
            gallery_elem_path = os.path.join(gallery_path, gallery)

            if os.path.isdir(gallery_elem_path) and gallery != "static":
                galleries.append({"title": gallery,
                                  "url": "/".join(["/" + gallery, "index.html"])
                                  })

        generate_html_output("/".join([gallery_path, "index.html"]),
                             template_name,
                             {"title": "Album", "galleries": galleries})


def prepare_images(src_path, dst_path, gallery_name, image_list, reload_gallery):
    src_gallery = os.path.join(src_path, gallery_name)
    dst_gallery = os.path.join(dst_path, gallery_name)
    thumbs_path = os.path.join(dst_gallery, THUMBS_NAME)

    if not os.path.exists(dst_gallery):
        os.mkdir(dst_gallery)

    if not os.path.exists(thumbs_path):
        os.mkdir(thumbs_path)

    for image in image_list:
        # create thumbs
        image_path = os.path.join(src_gallery, image)

        if not guess_type(image_path)[0] in SUPPORTED_IMAGES:
            continue

        image_thumb_path = os.path.join(thumbs_path, image)

        image_full = Image.open(os.path.normcase(image_path))
        image_exif_dict = image_full._getexif()

        if image_exif_dict is not None:
            exif = {}

            for k, v in image_exif_dict.items():
                try:
                    if ExifTags.TAGS[k] == 'Orientation':
                        exif[ExifTags.TAGS[k]] = v
                        break
                except KeyError:
                    print("the image has no metadata")

            if exif['Orientation'] == 3:
                image_full = image_full.rotate(180, expand=True)
            elif exif['Orientation'] == 6:
                image_full = image_full.rotate(270, expand=True)
            elif exif['Orientation'] == 8:
                image_full = image_full.rotate(90, expand=True)

        image_dst_path = os.path.join(dst_gallery, image)
        # TODO An option to rewrite images
        if not os.path.exists(image_dst_path) or reload_gallery:
            # FIXME PIL overrides original metadata when saving, we want to keep it
            image_full.save(image_dst_path, image_full.format)

        if not os.path.exists(os.path.join(image_thumb_path)) or reload_gallery:
            image_full.thumbnail(THUMBS_SIZE, Image.ANTIALIAS)
            image_full.save(image_thumb_path, image_full.format)


def create_gallery(src_path, dst_path, template_name, reload_gallery):
    gallery_path = src_path

    for gallery_name in os.listdir(gallery_path):
        gallery_elem_path = os.path.join(gallery_path, gallery_name)
        dst_gallery_path = os.path.join(dst_path, gallery_name)

        if os.path.isdir(gallery_elem_path):
            image_list = os.listdir(gallery_elem_path)
            image_list.sort()
            prepare_images(src_path, dst_path, gallery_name, image_list, reload_gallery)

            gallery_url = "".join(["/",  gallery_name, "/"])
            thumbs_url = "".join([gallery_url, THUMBS_NAME, "/"])

            generate_html_output("/".join([dst_gallery_path, "index.html"]),
                                 template_name,
                                 {"title": gallery_name.capitalize(),
                                  "thumbs_url": thumbs_url,
                                  "gallery_url": gallery_url,
                                  "image_list": image_list})


def exec_server(directory=DST_GALLERY_PATH, port=8000):
    """ Executes a server for development or simple gallery viewing """

    os.chdir(directory)
    print("Changing to the gallery directory... \n%s" % directory)
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), handler)

    print("Serving at port %d" % port)
    httpd.serve_forever()


def process_call(arguments):
    """ Process call arguments """

    src_path = arguments.src or SRC_GALLERY_PATH
    dst_path = arguments.dst or DST_GALLERY_PATH
    static_path = os.path.join(DST_GALLERY_PATH, 'static')
    template_gallery = arguments.template_gallery or GALLERY_TPL
    template_menu = arguments.template_menu or MENU_TPL
    reload_gallery = arguments.reload

    if arguments.port is not None:
        port = int(arguments.port)
    else:
        port = 8000

    if not os.path.exists(src_path):
        print 'The source path does not exist: %s' % src_path
        return False
    if not os.path.exists(dst_path):
        print 'The destiny path does not exist: %s' % dst_path
        return False

    create_gallery(src_path, dst_path, template_gallery, reload_gallery)
    create_menu(dst_path, template_menu)

    if not os.path.exists(static_path):
        os.symlink(os.path.join(os.path.dirname(__file__), 'static'),
                   static_path)

    if arguments.server:
        exec_server(port=port)
