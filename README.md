# HomeAssistant-EdgeTPU-Server

Performs object detection using an Edge Tensor Processing Unit on a video stream and publishes the state to a specified Home-Assistant instance.

## Running

### Requirements

* A Google EdgeTPU, either the Coral Dev Board or the USB Accelerator
* A TensorFlow Lite compiled model file, with associated labels file
    * Example pre-compiled model file and labels file:
    ```text
    https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
    https://dl.google.com/coral/canned_models/coco_labels.txt
    ```
* The URL to your Home-Assistant instance
* A long-lived token for your Home-Assistant instance
    1. Log into your Home-Assistant with your user
    2. Click the profile button at the top of the side-bar
    3. Click the `Create Token` button at the bottom of the page
    4. Save the generated token in a password manager for future reference
* The camera stream URLs you wish to process
    * It is recommended to use a low resolution around 500 x 500

### CLI Arguments

To run with CLI arguments:
```bash
edgetpu-server \
    -m $PATH_TO_MODEL_FILE \
    -l $PATH_TO_LABEL_FILE \
    -u $HOME_ASSISTANT_BASE_URL \
    -a $LONG_LIVED_TOKEN \
    -e $ENTITY_ID \
    -s $VIDEO_STREAM_URL \
    -c $CONFIDENCE \
    -t [$CATEGORY ...]
```

**Where:**  
* `$PATH_TO_MODEL_FILE` is the path to the model (*.tflite) file downloaded above  
* `$PATH_TO_LABEL_FILE` is the path to the label (*.txt) file downloaded above
* `$HOME_ASSISTANT_BASE_URL` is the base url of the Home-Assistant instance (e.g. http://192.168.1.100:8123)
* `$LONG_LIVED_TOKEN` is the token generated above
* `$ENTITY_ID` the entity_id to publish this stream's detection information to
* `$VIDEO_STREAM_URL` the stream url to process
* `$CONFIDENCE` minimum confidence score (0-100%) to report an object detected
* `[$CATEGORY ...]` is a space separated list of categories to report found in the labels file

**Example Command**
```bash
edgetpu-server \
    -m /opt/models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
    -l /opt/models/coco_labels.txt \
    -u http://10.0.11.174:8123 \
    -a abc123pozxc \
    -s sensor.front_door|rtsp://10.0.50.117:8080 sensor.back_door|rtsp://10.0.50.118:8080 \
    -c 70 \
    -t person cat dog
```

### Configuration File

To run with configuration file:
```bash
edgetpu-server -f $PATH_TO_CONFIG_FILE
```

**Where**:
* `$PATH_TO_CONFIG_FILE` is the path to an ini or yaml configuration file with the following properties set:

```yaml
models: /src/app/models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
labels: /src/app/models/coco_labels.txt
haurl: http://10.0.11.174:8123
token: abc123pozxc
entity: sensor.front_door
stream: rtsp://10.0.50.117:7447/5c44c565e4b0b1adf6614d97_2
confidence: 10
categories: [person, cat, dog]
```
   
### Entity State

The state payload sent to Home-Assistant looks like this:

```text
state: count of objects detected
attributes:
    matches:
        category:
            score: confidence score
            boxy: bounding box of object detected as [x1, y1, x2, y2]
    summary:
        category: count of objects detected by category
    total_matches: count of objects detected
```

## Future Improvements

* Provide a URL endpoint to the annotated image frame
* Allow multiple engines to process one TPU
* Allow multple TPUs 