for an explanation on how this works see https://www.youtube.com/watch?v=Pl-8SomWXew

for the wav files, ask in https://sce.sjsu.edu/s/discord for google drive access.

to copy this repo to the ec2 instance running asterisk:
```sh
rsync -razP -e "ssh -i ~/Downloads/sce_vpn2.pem" \
    ../sce-toll-free ubuntu@ec2-whatever.us-yeah.compute.amazonaws.com:/home/ubuntu/
```
