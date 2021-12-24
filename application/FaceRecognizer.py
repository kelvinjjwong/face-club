import time
from imutils import paths
import face_recognition
import pickle
import cv2
import os
import numpy
from PIL import Image, ImageFont, ImageDraw
import logging

from application import to_json


class FaceRecognizer:
    logger = None
    isTraining = False
    isRecognizing = False

    def __init__(self):
        self.logger = logging.getLogger('FACE')
        pass

    def training(self, dataset, model, detection_method="cnn", chunked_streaming=False):
        self.isTraining = True
        # grab the paths to the input images in our dataset
        self.logger.info("STARTUP Quantifying faces...")
        yield to_json({
            "state": "STARTUP",
            "message": "Quantifying faces...",
            "peopleId": "",
            "training_progress": "",
            "file": ""
        })
        imagePaths = list(paths.list_images(dataset))

        total = len(imagePaths)
        self.logger.info("TOTAL {}".format(total))
        yield to_json({
            "state": "COUNT",
            "message": "TOTAL {}".format(total),
            "peopleId": "",
            "training_progress": "0/{}".format(total),
            "file": ""
        })

        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []

        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            name = imagePath.split(os.path.sep)[-2]

            self.logger.info("PROCESSING IMAGE {}/{} {}".format(
                i + 1,
                len(imagePaths),
                name))
            yield to_json({
                "state": "PROCESSING",
                "message": "PROCESSING SAMPLE",
                "peopleId": name,
                "training_progress": "{}/{}".format(i + 1, len(imagePaths)),
                "file": imagePath
            })

            # load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                                                    model=detection_method)

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)

            yield to_json({
                "state": "PROCESSED",
                "message": "PROCESSED SAMPLE",
                "peopleId": name,
                "training_progress": "{}/{}".format(i + 1, len(imagePaths)),
                "file": imagePath
            })
        # dump the facial encodings + names to disk
        self.logger.info("ENCODE Serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open(model, "wb")
        f.write(pickle.dumps(data))
        f.close()
        self.logger.info("DONE")
        self.isTraining = False
        yield to_json({
            "state": "DONE",
            "message": "DONE",
            "peopleId": "",
            "training_progress": "",
            "file": ""
        })
        pass

    def get_model_data(self, model):
        # load the known faces and embeddings
        self.logger.info("Loading encoded pickle ...")
        return pickle.loads(open(model, "rb").read())

    def generate_image_file_path(self, file_path, suffix):
        filename = os.path.basename(file_path)
        folder = os.path.dirname(file_path)
        origin_filename, extension = os.path.splitext(filename)
        part = str(origin_filename).partition("_")
        out_filename = "%s_%s%s" % (part[0], suffix, extension)
        out_file_path = os.path.join(folder, out_filename)
        return out_file_path, out_filename, extension

    def resize_image(self, file_path, width: int):
        size = width, width
        out_file_path, out_filename, extension = self.generate_image_file_path(file_path, width)
        if not os.path.exists(out_file_path):
            try:
                im = Image.open(file_path)
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(out_file_path, "JPEG")
                self.logger.info("created thumbnail for %s" % file_path)
                return out_file_path
            except IOError:
                self.logger.error("cannot create thumbnail for %s" % file_path)
                return file_path
        else:
            return out_file_path

    def get_personName_from_people(self, peopleId: str, people):
        for p in people:
            if p["id"] == peopleId:
                return p["name"], p["shortName"]
        return '', ''

    def tag_faces_on_image(self, resized_image_file, faces, image_data=None):
        out_file_path, out_filename, extension = self.generate_image_file_path(resized_image_file, "faces")

        if len(faces) > 0:
            image = image_data
            if image is None:
                image = cv2.imread(resized_image_file)

            font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 14)
            font_color = (255, 255, 255)
            label_bgcolor = (80, 80, 80)
            label_border_color = (150, 150, 150)

            name_label_offset = 1
            name_label_width_offset = 2

            # loop over the recognized faces
            for face in faces:
                left = face['left']
                top = face['top']
                right = face['right']
                bottom = face['bottom']
                name = face['personName']
                if name == '':
                    name = face['peopleId']

                # draw the predicted face name on the image

                # Draw a box around the face
                cv2.rectangle(image, (left, top), (right, bottom), (100, 100, 100), 1)

                text_size = font.getsize(name)
                text_width = text_size[0]
                text_height = text_size[1]

                # Draw a label with a name below the face

                # label_triangle_top = bottom + 5
                label_midpoint = left + round((right - left) / 2)

                # borders of name label
                label_left = label_midpoint - round(text_width / 2) - name_label_width_offset  # left
                label_top = bottom + name_label_offset
                label_right = label_midpoint + round(text_width / 2) + name_label_width_offset  # right + 10
                label_bottom = label_top + round(text_height) + 5  # bottom + 35
                label_text_x = label_left + 2  # left + 2
                label_text_y = label_top  # + round(text_height / 2) #bottom + 30

                # 4 points of name label
                label_left_top = (label_left, label_top)
                label_right_top = (label_right, label_top)
                label_left_bottom = (label_left, label_bottom)
                label_right_bottom = (label_right, label_bottom)

                # name label rectangle - fill color
                cv2.rectangle(image, label_left_top, label_right_bottom, label_bgcolor, cv2.FILLED)

                # 3 points of triangle
                # pt1 = (label_midpoint, label_triangle_top)
                # pt2 = (label_midpoint - 7, label_top)
                # pt3 = (label_midpoint + 7, label_top)

                # triangle - fill color
                # triangle_cnt = numpy.array([pt1, pt2, pt3]).astype(numpy.int32)
                # cv2.drawContours(image, [triangle_cnt], 0, label_bgcolor, cv2.FILLED)

                # triangle - border
                # cv2.line(image, pt1, pt2, label_border_color, 1)
                # cv2.line(image, pt1, pt3, label_border_color, 1)
                # cv2.line(image, label_left_top, pt2, label_border_color, 1)
                # cv2.line(image, pt3, label_right_top, label_border_color, 1)

                # name label rectangle - border
                # cv2.line(image, label_left_top, label_right_top, label_border_color, 1)
                # cv2.line(image, label_left_top, label_left_bottom, label_border_color, 1)
                # cv2.line(image, label_right_top, label_right_bottom, label_border_color, 1)
                # cv2.line(image, label_left_bottom, label_right_bottom, label_border_color, 1)

                # Draw the name
                # cv2.putText(image, name , (label_text_x, label_text_y), font, 0.5, label_text_color, 1)
                # font.draw_text(image, (3, 3), '你好', 24, label_text_color)
                # self.logger.info("RECOGNITION RESULT: {} {} {} {} {}".format(left, top, right, bottom, name))

            # draw rectangle to image
            img_PIL = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_PIL)

            # draw name label - text
            for face in faces:
                left = face['left']
                top = face['top']
                right = face['right']
                bottom = face['bottom']
                name = face['personName']
                if name == '':
                    name = face['peopleId']

                if name != "Unknown":
                    text_size = font.getsize(name)
                    text_width = text_size[0]
                    text_height = text_size[1]

                    label_midpoint = left + round((right - left) / 2)
                    label_left = label_midpoint - round(text_width / 2) - name_label_width_offset  # left
                    label_top = bottom + name_label_offset
                    label_right = label_midpoint + round(text_width / 2) + name_label_width_offset  # right + 10
                    label_bottom = label_top + round(text_height) + 5  # bottom + 35
                    label_text_x = label_left + 2  # left + 2
                    label_text_y = label_top + 2  # + round(text_height / 2) #bottom + 30

                    draw.text((label_text_x, label_text_y), name, font=font, fill=font_color)

            image = cv2.cvtColor(numpy.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            cv2.imwrite(out_file_path, image)
            self.logger.info("Saved tagged image to {}".format(out_file_path))
            return out_file_path
        else:
            if os.path.exists(out_file_path):
                os.remove(out_file_path)
            return ''

    def recognize_image(self, model_data, image_file, people_names, detection_method="cnn"):
        # load the input image and convert it from BGR to RGB
        thumbnail_image_file = self.resize_image(image_file, 200)
        resized_image_file = self.resize_image(image_file, 1280)
        image = cv2.imread(resized_image_file)
        width, height, channels = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes corresponding
        # to each face in the input image, then compute the facial embeddings
        # for each face
        self.logger.info("recognizing faces...")
        boxes = face_recognition.face_locations(rgb,
                                                model=detection_method)
        encodings = face_recognition.face_encodings(rgb, boxes)

        # initialize the list of names for each face detected
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(model_data["encodings"],
                                                     encoding, tolerance=0.5)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = model_data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of
                # votes (note: in the event of an unlikely tie Python will
                # select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)

        faces = []
        for ((top, right, bottom, left), name) in zip(boxes, names):
            personName, shortName = self.get_personName_from_people(name, people_names)
            faces.append({
                'top': top,
                'right': right,
                'bottom': bottom,
                'left': left,
                'peopleId': name,
                'personName': personName,
                'shortName': shortName
            })
            self.logger.info("top=%s right=%s bottom=%s left=%s name=%s" % (top, right, bottom, left, name))

        self.logger.info("Recognition result: %s - %s" % (image_file, names))

        # save image
        out_file_path = self.tag_faces_on_image(resized_image_file, faces, image)

        return names, faces, width, height, resized_image_file, out_file_path
