# DingDong: Your Doorbell Just Got Sillier

Have you ever wished that your doorbell could have an API that lets you configure what noise it makes?
Have I got great news for you!

## How it works

A Raspberry Pi connects to an existing doorbell via its GPIO pins and plays a sound effect over the 3.5mm headphone jack.
It gets this sound by pinging the ```DingDongWeb.py``` API hosted either locally or somewhere in the cloud.
The API keeps a library of available sound effects as well as a couple of options for playback.

## Usage

This project is still a work in progress.
You can tinker with the API in its current state by opening this repo in VSCode and running ```Run API``` in the debugger.

For manual control, especially when working on the database, open a terminal on your host machine (i.e. not the one in VSCode, which is open in a devcontainer), and run:

```bash
docker compose build && docker compose up
```

Your changes will not automatically be picked up so you will have to run this every time you want to apply your changes.
