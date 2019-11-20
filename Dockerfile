FROM balenalib/raspberrypi3-ubuntu-python:3.7-bionic

ARG CONF_FILE=server.yaml
ENV CONF_FILE=${CONF_FILE}

VOLUME /conf

#do installation
RUN apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
#do users
    && echo 'root:root' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
    && mkdir /var/run/sshd

#install libraries for camera
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
    build-essential wget feh pkg-config libjpeg-dev \
    libfreetype6-dev libxml2 libopenjp2-7 \
    libatlas-base-dev libqtgui4 libqt4-test \
    python3-wheel python3-numpy python3-pil \
    python3-matplotlib python3-zmq zlib1g-dev

#install live camera libraries
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    libgstreamer1.0-0 gstreamer1.0-tools \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly v4l-utils

#loading pretrained models
WORKDIR /usr/src/app/models
RUN wget https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
    && wget https://dl.google.com/coral/canned_models/coco_labels.txt

#python libraries
WORKDIR /usr/src/app
COPY . .

#installing library
RUN cd edgetpu_api && \
    chmod +x install.sh \
    && bash install.sh -y

RUN python3 -m pip config set global.extra-index-url https://www.piwheels.org/simple \
    && python3 -m pip install -r requirements.txt \
    && python3 -m pip install setuptools wheel

RUN python3 setup.py bdist_wheel \
    && pip3 install dist/edgetpu_server-*.whl

CMD ["edgetpu_server", "-f", "/conf/$CONF_FILE"]
