# Example of a drain3.ini file

gool try to load .drain3 file from your home. Otherwise you can use **--cfg-file** option. Without any configuration, gool will try to mask HEX, IP and times.

``` ini
[MASKING]
masking = [
    {"regex_pattern":"((?<=[^A-Za-z0-9])|^)(0[xX][0-9a-fA-F]+)((?=[^A-Za-z0-9])|$)", "mask_with": "HEX"},
    {"regex_pattern":"(\\d{2}:\\d{2}:\\d{2}(.\\d+|))", "mask_with": "TIME"},
    {"regex_pattern":"((?<=[^A-Za-z0-9])|^)(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})((?=[^A-Za-z0-9])|$)", "mask_with": "IP"}
    ]
mask_prefix = <:
mask_suffix = :>

[DRAIN]
sim_th = 0.9
depth = 7
max_children = 200
extra_delimiters = ["_"]

```
