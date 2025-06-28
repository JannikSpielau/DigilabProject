# 🎵 Spotify Controller with Raspberry Pi & Digilab Board

This is a **school project** that lets you control Spotify playback using physical buttons on a **custom Digilab board** connected to a **Raspberry Pi**. It displays the currently playing song (title + artist) on a 2-line LCD screen, with support for scrolling long text.

Spotify integration is handled by a **TypeScript server**, hosted remotely behind a domain via **Cloudflare Zero Trust tunneling**, so it complies with Spotify's OAuth redirect requirements.

---

## 🧰 Features

- ⏯️ Pause / Resume playback
- ⏭️ Skip to next track
- ⏮️ Go to previous track
- 📺 Display song title and artist on an LCD
- 🌀 Scroll long text on the LCD
- 🔘 Use physical buttons on Digilab board
- 🌐 Secure remote server via **Cloudflare tunnel**

---

## 🔧 Hardware Setup

- 🧠 **Raspberry Pi** running:
  - Node-RED
  - Python script to write to LCD
- 🎛️ **Digilab board**:
  - 2 buttons (Next / Previous)
  - 1 switch (Pause / Resume)
  - 2-line I2C LCD display

---

## 🌐 Spotify Server (TypeScript)

The backend server handles Spotify OAuth2 login and playback control. It must be publicly accessible (not local) to satisfy Spotify’s redirect URI policy.

### Hosted Domain

The server is exposed using **Cloudflare Zero Trust Tunnel**.

This domain must be registered in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) under the Redirect URI.

### Environment Variables (.env)

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://spotify.YOURDOMAIN.com/callback
```

### Installation & Run

```bash
cd dist/
tsc
node server.js
```
Or use [PM2](https://pm2.keymetrics.io/) to keep it running in the background:

### Server Endpoints

| Endpoint          | Description                        |
|------------------|------------------------------------|
| `/login`         | Starts Spotify login flow          |
| `/callback`      | Handles OAuth2 redirect            |
| `/currentsong`   | Returns currently playing song     |
| `/next`          | Skips to the next track            |
| `/previous`      | Skips to the previous track        |
| `/pauseresume`   | Toggles between play and pause     |

---

## 🔁 Node-RED Flow

Node-RED runs on the Raspberry Pi, listens to GPIO input from the Digilab board, and interacts with the server and display.

### GPIO Pin Mapping

| BCM Pin | Function        |
|---------|-----------------|
| 20      | Pause / Resume  |
| 19      | Previous Track  |
| 16      | Next Track      |

### Flow Summary

1. Button press detected on a GPIO pin.
2. Node-RED sends a GET request to the remote server (`/next`, `/previous`, `/pauseresume`).
3. Server responds with song metadata.
4. Node-RED extracts title and artist.
5. Python script (`write_line.py`) is executed with the song info to update the LCD.

---

## 📟 LCD Display

A Python script displays the song on a 2-line LCD screen connected via I2C.

### Example command:

```bash
python /home/Jannik/digilab/lcd/write_line.py --line 0 --message "Song Title" --line 1 --message "Artist Name"
```

- Supports **scrolling** for long text.
- Called from Node-RED's `exec` node.

---

## 🌐 Cloudflare Tunnel

Used to expose the local TypeScript server to the public internet securely.

### Example tunnel setup

```bash
cloudflared tunnel create spotify-tunnel
cloudflared tunnel route dns spotify-tunnel spotify.YOURDOMAIN.com
cloudflared tunnel run spotify-tunnel
```

Ensure `spotify.YOURDOMAIN.com` is listed in your Spotify app's **redirect URIs**.

## 📜 License

GNU GENERAL PUBLIC LICENSE
