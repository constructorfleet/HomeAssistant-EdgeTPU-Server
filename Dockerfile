FROM balenalib/raspberrypi3-debian-python:3.7-buster

ARG CONF_FILE=server.yaml
ENV CONF_FILE=${CONF_FILE}

VOLUME /conf

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

#do installation
RUN apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
#do users
    && echo 'root:root' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
    && mkdir /var/run/sshd

#install libraries for camera

RUN apt-get install -y --no-install-recommends build-essential wget feh pkg-config libjpeg-dev zlib1g-dev \
    libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin libfreetype6-dev libxml2 libopenjp2-7 \
    libatlas-base-dev libjasper-dev libqtgui4 libqt4-test python3-pip \
    python3-dev python3-setuptools python3-wheel python3-numpy python3-pil python3-matplotlib python3-zmq

#install live camera libraries
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    libgstreamer1.0-0 gstreamer1.0-tools \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly v4l-utils \
    cmake git libgtk-3.0 libavformat-dev \
    libavcodec-dev libswscale-dev libtbb2 libtbb-dev libpng-dev \
    libtiff-dev libdc1394-22-dev libhdf5-dev libhdf5-serial-dev \
    python3-edgetpu libedgetpu1-std

WORKDIR /usr/src/app
#loading pretrained models
RUN mkdir models \
    && wget -O models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
    && wget -O models/coco_labels.txt https://dl.google.com/coral/canned_models/coco_labels.txt

COPY . .

RUN apt-get purge python3-pip python3-setuptools

RUN python3 -m pip config set global.extra-index-url https://www.piwheels.org/simple \
    && python3 -m pip install -r requirements.txt \
    && python3 -m pip install setuptools wheel

RUN python3 -m pip install  -e . \
    && LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 setup.py bdist_wheel \
    && python3 -m pip install dist/edgetpu_server-*.whl

CMD ["edgetpu_server", "-f", "/conf/$CONF_FILE"]
