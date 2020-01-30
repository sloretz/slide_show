# Slide Show

This node publishes images from a directory at a fixed rate.

# Topics -

* `images` (type: `sensor_msgs/msg/Image`) - The topic on which images are published.

## Parameters

* `directory` (type: `str`) - a path to a directory containing image files
* `period` (type: `double`) - time in seconds to wait before publishing the next image

## Examples

Publish images from the current diretory at the default rate.

```
ros2 run slide_show slide_show
```

To run with custom parameters, edit and save the following as `slide_show_params.yaml`

```
/**:
  ros__parameters:
    directory: /some/dir/with/images
    period: 3.14
```

Then run the node with the path to the yaml file.

```
ros2 run slide_show slide_show --ros-args __params:=path/to/slide_show_params.yaml
```
