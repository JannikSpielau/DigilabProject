import http from "http";
import axios from "axios";
import { parse } from "url";
import querystring from "querystring";
import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

const client_id = process.env.SPOTIFY_CLIENT_ID!;
const client_secret = process.env.SPOTIFY_CLIENT_SECRET!;
const redirect_uri = process.env.SPOTIFY_REDIRECT_URI!;

let access_token: string | null = null;

function generateRandomString(length: number): string {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  return Array.from({ length }, () =>
    chars.charAt(Math.floor(Math.random() * chars.length))
  ).join("");
}

function json(
  res: http.ServerResponse,
  statusCode: number,
  body: { success: boolean; message: string | object }
) {
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(body));
}

function redirect(res: http.ServerResponse, url: string) {
  res.writeHead(302, { Location: url });
  res.end();
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = parse(req.url || "", true);
  const path = parsedUrl.pathname;

  if (path === "/login") {
    const state = generateRandomString(16);
    const scope =
      "user-read-currently-playing user-read-playback-state user-modify-playback-state";

    const authQueryParams = querystring.stringify({
      response_type: "code",
      client_id,
      scope,
      redirect_uri,
      state,
    });

    return redirect(
      res,
      "https://accounts.spotify.com/authorize?" + authQueryParams
    );
  }

  if (path === "/callback") {
    const code = parsedUrl.query.code as string;
    if (!code)
      return json(res, 400, { success: false, message: "No code provided" });

    try {
      const tokenResponse = await axios.post(
        "https://accounts.spotify.com/api/token",
        querystring.stringify({
          code,
          redirect_uri,
          grant_type: "authorization_code",
        }),
        {
          headers: {
            Authorization:
              "Basic " +
              Buffer.from(`${client_id}:${client_secret}`).toString("base64"),
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      access_token = tokenResponse.data.access_token;
      return json(res, 200, {
        success: true,
        message:
          "Login successful! You can now use /currentsong, /next, /previous, /pauseresume.",
      });
    } catch (error: any) {
      console.error(error.response?.data || error.message);
      return json(res, 500, {
        success: false,
        message: "Failed to authenticate.",
      });
    }
  }

  if (!access_token) {
    return json(res, 401, { success: false, message: "Please log in first." });
  }

  if (path === "/currentsong") {
    try {
      const playingResponse = await axios.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );

      if (playingResponse.status === 204 || !playingResponse.data) {
        return json(res, 200, {
          success: true,
          message: "No song currently playing.",
        });
      }

      const track = playingResponse.data.item;
      const artists = track.artists.map((a: any) => a.name).join(", ");
      return json(res, 200, {
        success: true,
        message: {
          title: track.name,
          artist: artists,
        },
      });
    } catch (err: any) {
      console.error(err.response?.data || err.message);
      return json(res, 500, {
        success: false,
        message: "Error retrieving song.",
      });
    }
  }

  if (path === "/next") {
    try {
      await axios.post("https://api.spotify.com/v1/me/player/next", null, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      await delay(1000);

      const playingResponse = await axios.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );

      if (playingResponse.status === 204 || !playingResponse.data) {
        return json(res, 200, {
          success: true,
          message: "Skipped to next, but nothing is playing now.",
        });
      }

      const track = playingResponse.data.item;
      const artists = track.artists.map((a: any) => a.name).join(", ");

      return json(res, 200, {
        success: true,
        message: {
          title: track.name,
          artist: artists,
        },
      });
    } catch (err: any) {
      console.error(err.response?.data || err.message);
      return json(res, 500, {
        success: false,
        message: "Error skipping song.",
      });
    }
  }

  if (path === "/previous") {
    try {
      await axios.post("https://api.spotify.com/v1/me/player/previous", null, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      await delay(1000);

      const playingResponse = await axios.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );

      if (playingResponse.status === 204 || !playingResponse.data) {
        return json(res, 200, {
          success: true,
          message: "Went to previous, but nothing is playing now.",
        });
      }

      const track = playingResponse.data.item;
      const artists = track.artists.map((a: any) => a.name).join(", ");

      return json(res, 200, {
        success: true,
        message: {
          title: track.name,
          artist: artists,
        },
      });
    } catch (err: any) {
      console.error(err.response?.data || err.message);
      return json(res, 500, {
        success: false,
        message: "Error going to previous song.",
      });
    }
  }

  if (path === "/pauseresume") {
    try {
      const playbackState = await axios.get(
        "https://api.spotify.com/v1/me/player",
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );

      const isPlaying = playbackState.data?.is_playing;

      if (isPlaying) {
        await axios.put("https://api.spotify.com/v1/me/player/pause", null, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        return json(res, 200, { success: true, message: "Playback paused." });
      } else {
        await axios.put("https://api.spotify.com/v1/me/player/play", null, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        return json(res, 200, { success: true, message: "Playback resumed." });
      }
    } catch (err: any) {
      console.error(err.response?.data || err.message);
      return json(res, 500, {
        success: false,
        message: "Error toggling playback.",
      });
    }
  }

  return json(res, 404, { success: false, message: "Not Found" });
});

server.listen(1337, () => {
  console.log("Server running on http://127.0.0.1:1337");
});
